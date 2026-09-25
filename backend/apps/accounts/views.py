from django.conf import settings
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer
from apps.audit.utils import registrar_log
from .emails import enviar_link_definir_senha
from .models import PasswordResetToken, User
from .permissions import AceitouTermosVigentes, IsGestor
from .serializers import (
    CriarUsuarioSerializer,
    CustomTokenObtainPairSerializer,
    EsqueciSenhaSerializer,
    MeSerializer,
    RedefinirSenhaSerializer,
    UsuarioDetalheSerializer,
    UsuarioListaSerializer,
)

LIMITE_LOGS_NA_TELA = 200


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '')
        # Quando o e-mail existe, a tentativa fica ligada à conta, inclusive
        # nas falhas, para aparecer no histórico da pessoa.
        usuario = User.objects.filter(email=email).first()

        try:
            response = super().post(request, *args, **kwargs)
        except Exception:
            # Com senha errada o simplejwt lança exceção em vez de devolver
            # uma resposta; registramos a falha e deixamos o DRF responder 401.
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
        if versao != settings.VERSAO_TERMOS:
            return Response(
                {'detail': 'O termo foi atualizado. Recarregue a página e leia a versão atual.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario = request.user
        usuario.termos_versao_aceita = versao
        usuario.termos_aceitos_em = timezone.now()
        usuario.save(update_fields=['termos_versao_aceita', 'termos_aceitos_em'])
        registrar_log(usuario, 'termos_aceitos', detalhes=f'Termo de Uso e Aceite, versão {versao}', request=request)

        return Response(MeSerializer(usuario).data)



class EsqueciSenhaView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EsqueciSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        usuario = User.objects.filter(email=email).first()
        if usuario:
            try:
                # Quem ainda não criou senha (conta feita pela secretaria)
                # recebe o e-mail de primeiro acesso, não o de redefinição.
                enviar_link_definir_senha(usuario, primeiro_acesso=not usuario.has_usable_password())
            except Exception as erro:
                registrar_log(usuario, 'esqueci_senha_falha_envio', detalhes=f'erro: {erro}', request=request)
                return Response(
                    {'detail': 'Não foi possível enviar o e-mail agora. Tente novamente mais tarde.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )
            registrar_log(usuario, 'esqueci_senha_solicitado', request=request)

        # Sempre retorna sucesso, mesmo se o e-mail não existir no sistema,
        # para não revelar quais e-mails estão cadastrados.
        return Response({'detail': 'Se o e-mail existir, enviamos um link de redefinição.'})


class RedefinirSenhaView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RedefinirSenhaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_valor = serializer.validated_data['token']
        nova_senha = serializer.validated_data['nova_senha']

        reset_token = PasswordResetToken.objects.filter(token=token_valor).first()

        if not reset_token or not reset_token.esta_valido():
            # O token não vai para o log: o guia da LGPD proíbe gravar tokens.
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
    queryset = User.objects.order_by('first_name', 'last_name')

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

        email_enviado = True
        try:
            enviar_link_definir_senha(usuario, primeiro_acesso=True)
        except Exception as erro:
            email_enviado = False
            registrar_log(
                request.user, 'convite_falha_envio',
                detalhes=f'usuario id={usuario.id} | erro: {erro}', request=request,
            )

        dados = UsuarioListaSerializer(usuario).data
        dados['email_enviado'] = email_enviado
        return Response(dados, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        usuario = self.get_object()
        logs = AuditLog.objects.filter(usuario=usuario).order_by('-criado_em')[:LIMITE_LOGS_NA_TELA]
        return Response(AuditLogSerializer(logs, many=True).data)

    @action(detail=True, methods=['get'])
    def exportar(self, request, pk=None):
        usuario = self.get_object()
        logs = AuditLog.objects.filter(usuario=usuario).order_by('-criado_em')
        dados = {
            'gerado_em': timezone.now(),
            'gerado_por': request.user.email,
            'usuario': UsuarioDetalheSerializer(usuario).data,
            'logs': AuditLogSerializer(logs, many=True).data,
        }
        registrar_log(request.user, 'dados_exportados', detalhes=f'usuario id={usuario.id}', request=request)
        return Response(dados)
