from django.db.models import OuterRef, Q, Subquery
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.academic.models import Matricula
from apps.audit.models import AuditLog
from apps.audit.retencao import CONFIRMACAO_ANONIMIZAR, anonimizar_a_pedido, impedimentos_para_anonimizar
from apps.audit.serializers import AuditLogSerializer
from apps.audit.utils import registrar_log

from .documentos import descrever_versao, documento_vigente, publicar, versao_de, versao_vigente
from .emails import enviar_link_definir_senha
from .models import DocumentoLegal, PasswordResetToken, User
from .permissions import AceitouTermosVigentes, IsDirecao, IsGestor
from .serializers import (
    CriarUsuarioSerializer,
    CustomTokenObtainPairSerializer,
    DocumentoLegalSerializer,
    EsqueciSenhaSerializer,
    MeSerializer,
    PublicarDocumentoSerializer,
    RedefinirSenhaSerializer,
    UsuarioDetalheSerializer,
    UsuarioListaSerializer,
)

LIMITE_LOGS_NA_TELA = 200


class PaginacaoUsuarios(PageNumberPagination):
    """20 contas por página (RNF05); as listas de seleção da secretaria pedem mais com ?page_size=."""

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 500


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '')
        usuario = User.objects.filter(email=email).first()

        try:
            response = super().post(request, *args, **kwargs)
        except Exception:
            registrar_log(usuario, 'login_falha', detalhes=f'tentativa de login: {email}', request=request)
            raise

        registrar_log(usuario, 'login_sucesso', detalhes=f'login: {email}', request=request)
        return response


class MeView(RetrieveAPIView):
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class AceitarTermosView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        versao = request.data.get('versao')
        if versao != versao_vigente():
            return Response(
                {'detail': 'O termo foi atualizado. Recarregue a página e leia a versão atual.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario = request.user
        usuario.termos_versao_aceita = versao
        usuario.termos_aceitos_em = timezone.now()
        usuario.save(update_fields=['termos_versao_aceita', 'termos_aceitos_em'])
        registrar_log(usuario, 'termos_aceitos', detalhes=descrever_versao(versao), request=request)

        return Response(MeSerializer(usuario).data)


class EsqueciSenhaView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'senha'

    def post(self, request):
        serializer = EsqueciSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        usuario = User.objects.filter(email=email).first()
        if usuario:
            try:
                enviar_link_definir_senha(usuario, primeiro_acesso=not usuario.has_usable_password())
            except Exception as erro:
                registrar_log(usuario, 'esqueci_senha_falha_envio', detalhes=f'erro: {erro}', request=request)
                return Response(
                    {'detail': 'Não foi possível enviar o e-mail agora. Tente novamente mais tarde.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            registrar_log(usuario, 'esqueci_senha_solicitado', request=request)

        return Response({'detail': 'Se o e-mail existir, enviamos um link de redefinição.'})


class RedefinirSenhaView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'senha'

    def post(self, request):
        serializer = RedefinirSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_valor = serializer.validated_data['token']
        nova_senha = serializer.validated_data['nova_senha']

        reset_token = PasswordResetToken.objects.filter(token=token_valor).first()

        if not reset_token or not reset_token.esta_valido():
            registrar_log(None, 'redefinir_senha_falha', detalhes='token inválido ou expirado', request=request)
            return Response({'detail': 'Token inválido ou expirado.'}, status=status.HTTP_400_BAD_REQUEST)

        usuario = reset_token.usuario
        usuario.set_password(nova_senha)
        usuario.save()

        reset_token.usado = True
        reset_token.save()

        registrar_log(usuario, 'senha_redefinida', request=request)

        return Response({'detail': 'Senha redefinida com sucesso.'})


class UsuarioViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Contas de usuários, gerenciadas pela secretaria e pela direção."""

    permission_classes = [IsAuthenticated, AceitouTermosVigentes, IsGestor]
    pagination_class = PaginacaoUsuarios

    def get_queryset(self):
        turma_ativa = Matricula.objects.filter(aluno=OuterRef('pk'), situacao=Matricula.Situacao.ATIVA)
        qs = User.objects.annotate(
            turma_atual=Subquery(turma_ativa.values('turma__nome')[:1]),
        ).order_by('first_name', 'last_name')

        params = self.request.query_params
        busca = params.get('busca', '').strip()
        if busca:
            qs = qs.filter(Q(first_name__icontains=busca) | Q(last_name__icontains=busca) | Q(email__icontains=busca))
        if params.get('role'):
            qs = qs.filter(role=params['role'])
        if params.get('turma'):
            qs = qs.filter(matriculas__turma_id=params['turma'], matriculas__situacao=Matricula.Situacao.ATIVA)
        if params.get('ativo') in ('true', 'false'):
            qs = qs.filter(is_active=params['ativo'] == 'true')
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return CriarUsuarioSerializer
        if self.action == 'retrieve':
            return UsuarioDetalheSerializer
        return UsuarioListaSerializer

    def create(self, request, *args, **kwargs):
        serializer = CriarUsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        registrar_log(
            request.user, 'usuario_criado',
            detalhes=f'usuario id={usuario.id}, papel={usuario.role}', request=request,
        )
        for matricula in usuario.matriculas.all():
            registrar_log(request.user, 'matricula_criada',
                          detalhes=f'aluno id={usuario.id}, turma id={matricula.turma_id}', request=request)
        for vinculo in usuario.vinculos_como_aluno.all():
            registrar_log(request.user, 'vinculo_criado',
                          detalhes=f'responsavel id={vinculo.responsavel_id}, aluno id={usuario.id}', request=request)

        email_enviado = True
        try:
            enviar_link_definir_senha(usuario, primeiro_acesso=True)
        except Exception as erro:
            email_enviado = False
            registrar_log(
                request.user, 'convite_falha_envio',
                detalhes=f'usuario id={usuario.id} | erro: {erro}', request=request,
            )

        dados = UsuarioListaSerializer(self.get_queryset().get(pk=usuario.pk)).data
        dados['email_enviado'] = email_enviado
        return Response(dados, status=status.HTTP_201_CREATED)

    SOMENTE_DIRECAO = [IsAuthenticated, AceitouTermosVigentes, IsDirecao]

    @action(detail=True, methods=['get'], permission_classes=SOMENTE_DIRECAO)
    def logs(self, request, pk=None):
        usuario = self.get_object()
        logs = AuditLog.objects.filter(usuario=usuario).order_by('-criado_em')[:LIMITE_LOGS_NA_TELA]
        return Response(AuditLogSerializer(logs, many=True).data)

    @action(detail=True, methods=['get'], permission_classes=SOMENTE_DIRECAO)
    def exportar(self, request, pk=None):
        usuario = self.get_object()
        logs = AuditLog.objects.filter(usuario=usuario).order_by('-criado_em')
        dados = {
            'gerado_em': timezone.now(),
            'gerado_por': request.user.email,
            'usuario': UsuarioDetalheSerializer(usuario, context={'emails_completos': True}).data,
            'logs': AuditLogSerializer(logs, many=True, context={'emails_completos': True}).data,
        }
        registrar_log(request.user, 'dados_exportados', detalhes=f'usuario id={usuario.id}', request=request)
        return Response(dados)

    @action(detail=True, methods=['post'])
    def anonimizar(self, request, pk=None):
        """Anonimização a pedido do titular (Plano de Retenção, seção 5). A ação não pode ser desfeita."""
        usuario = self.get_object()
        if request.data.get('confirmacao') != CONFIRMACAO_ANONIMIZAR:
            raise ValidationError({'confirmacao': [f'Digite {CONFIRMACAO_ANONIMIZAR} para confirmar.']})
        motivos = impedimentos_para_anonimizar(usuario, request.user)
        if motivos:
            raise ValidationError({'detail': motivos})
        anonimizar_a_pedido(usuario)
        registrar_log(request.user, 'conta_anonimizada', detalhes=f'usuario id={usuario.id}, a pedido do titular',
                      request=request)
        return Response(UsuarioDetalheSerializer(self.get_queryset().get(pk=usuario.pk)).data)


class DocumentoLegalView(APIView):
    """Termo de Uso e Política de Privacidade vigentes (RF23).

    GET é público, porque os documentos podem ser lidos sem login (RN04). Enquanto a Direção não publica
    nenhuma versão pelo portal, conteudo vem nulo e o site mostra o texto que acompanha o código.
    POST publica uma nova versão (só a Direção) e exige novo aceite de todos os usuários.
    """

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), AceitouTermosVigentes(), IsDirecao()]
        return [AllowAny()]

    def tipo_valido(self, tipo):
        if tipo not in DocumentoLegal.Tipo.values:
            raise NotFound('Documento não encontrado.')
        return tipo

    def get(self, request, tipo):
        tipo = self.tipo_valido(tipo)
        documento = documento_vigente(tipo)
        if documento:
            return Response(DocumentoLegalSerializer(documento).data)
        return Response({'tipo': tipo, 'nome': DocumentoLegal.Tipo(tipo).label, 'versao': versao_de(tipo),
                         'conteudo': None, 'resumo': None, 'publicado_em': None, 'publicado_por': None})

    def post(self, request, tipo):
        tipo = self.tipo_valido(tipo)
        dados = PublicarDocumentoSerializer(data=request.data)
        dados.is_valid(raise_exception=True)
        vigente = documento_vigente(tipo)
        if vigente and vigente.conteudo == dados.validated_data['conteudo']:
            raise ValidationError(
                {'conteudo': ['O texto é igual ao da versão vigente. Altere o documento antes de publicar.']})
        documento = publicar(tipo, autor=request.user, **dados.validated_data)
        registrar_log(request.user, 'documento_publicado',
                      detalhes=f'{documento.get_tipo_display()}, versão {documento.versao}: {documento.resumo}',
                      request=request)
        return Response(DocumentoLegalSerializer(documento).data, status=status.HTTP_201_CREATED)


class VersoesDocumentoView(APIView):
    """Histórico das versões publicadas de um documento, para a Direção (RF23)."""

    permission_classes = [IsAuthenticated, AceitouTermosVigentes, IsDirecao]

    def get(self, request, tipo):
        if tipo not in DocumentoLegal.Tipo.values:
            raise NotFound('Documento não encontrado.')
        versoes = DocumentoLegal.objects.filter(tipo=tipo).select_related('publicado_por')
        return Response([
            {k: v for k, v in DocumentoLegalSerializer(d).data.items() if k != 'conteudo'} for d in versoes
        ])
