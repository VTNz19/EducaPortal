from django.db import transaction
from django.db.models import Count, ProtectedError, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import User
from apps.accounts.permissions import AceitouTermosVigentes, GestorEditaProfessorConsulta, IsGestor
from apps.accounts.serializers import UsuarioDetalheSerializer
from apps.audit.utils import registrar_log

from .models import AnoLetivo, Disciplina, Matricula, Turma, VinculoResponsavel
from .serializers import (
    AnoLetivoSerializer,
    DisciplinaSerializer,
    ResponsavelSerializer,
    TurmaDestinoSerializer,
    TurmaSerializer,
)


class EstruturaAcademicaViewSet(viewsets.ModelViewSet):
    """Base do RF13: listas pequenas, sem paginação, e exclusão protegida."""

    permission_classes = [IsAuthenticated, AceitouTermosVigentes, GestorEditaProfessorConsulta]
    pagination_class = None
    acoes = ('', '', '')
    mensagem_protegida = ''

    def descrever(self, obj):
        return f'{obj} (id={obj.id})'

    def perform_create(self, serializer):
        obj = serializer.save()
        registrar_log(self.request.user, self.acoes[0], detalhes=self.descrever(obj), request=self.request)

    def perform_update(self, serializer):
        obj = serializer.save()
        registrar_log(self.request.user, self.acoes[1], detalhes=self.descrever(obj), request=self.request)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        descricao = self.descrever(obj)
        try:
            obj.delete()
        except ProtectedError:
            return Response({'detail': self.mensagem_protegida}, status=status.HTTP_400_BAD_REQUEST)
        registrar_log(request.user, self.acoes[2], detalhes=descricao, request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnoLetivoViewSet(EstruturaAcademicaViewSet):
    queryset = AnoLetivo.objects.prefetch_related('bimestres')
    serializer_class = AnoLetivoSerializer
    acoes = ('ano_letivo_criado', 'ano_letivo_editado', 'ano_letivo_excluido')
    mensagem_protegida = 'Este ano letivo já tem turmas e não pode ser excluído.'


class TurmaViewSet(EstruturaAcademicaViewSet):
    serializer_class = TurmaSerializer
    acoes = ('turma_criada', 'turma_editada', 'turma_excluida')
    mensagem_protegida = 'Esta turma já tem disciplinas, matrículas ou avisos e não pode ser excluída.'

    def get_queryset(self):
        qs = Turma.objects.select_related('ano_letivo').annotate(
            total_alunos=Count('matriculas', filter=Q(matriculas__situacao=Matricula.Situacao.ATIVA)),
        )
        ano_letivo = self.request.query_params.get('ano_letivo')
        if ano_letivo:
            qs = qs.filter(ano_letivo_id=ano_letivo)
        return qs


class DisciplinaViewSet(EstruturaAcademicaViewSet):
    serializer_class = DisciplinaSerializer
    acoes = ('disciplina_criada', 'disciplina_editada', 'disciplina_excluida')
    mensagem_protegida = 'Esta disciplina já tem lançamentos e não pode ser excluída.'

    def get_queryset(self):
        qs = Disciplina.objects.select_related('turma__ano_letivo', 'professor')
        if self.request.user.role == 'professor':
            qs = qs.filter(professor=self.request.user)
        params = self.request.query_params
        if params.get('turma'):
            qs = qs.filter(turma_id=params['turma'])
        if params.get('ano_letivo'):
            qs = qs.filter(turma__ano_letivo_id=params['ano_letivo'])
        return qs

    def perform_update(self, serializer):
        professor_anterior = serializer.instance.professor_id
        obj = serializer.save()
        acao = 'professor_alterado' if obj.professor_id != professor_anterior else self.acoes[1]
        registrar_log(self.request.user, acao, detalhes=self.descrever(obj), request=self.request)


class AlunoMatriculaViewSet(viewsets.GenericViewSet):
    """RF14: alterações de matrícula e de vínculos de um aluno já cadastrado."""

    permission_classes = [IsAuthenticated, AceitouTermosVigentes, IsGestor]
    queryset = User.objects.filter(role=User.Role.ALUNO)

    def responder(self, aluno):
        return Response(UsuarioDetalheSerializer(aluno).data)

    def log(self, acao, detalhes):
        registrar_log(self.request.user, acao, detalhes=detalhes, request=self.request)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def transferir(self, request, pk=None):
        aluno = self.get_object()
        dados = TurmaDestinoSerializer(data=request.data)
        dados.is_valid(raise_exception=True)
        destino = dados.validated_data['turma']
        atual = aluno.matriculas.filter(situacao=Matricula.Situacao.ATIVA, ano_letivo=destino.ano_letivo).first()
        if atual is None:
            return erro('O aluno não tem matrícula ativa no ano letivo dessa turma. Use a rematrícula.')
        if atual.turma_id == destino.id:
            return erro('O aluno já está matriculado nessa turma.')
        hoje = timezone.localdate()
        atual.situacao, atual.data_fim = Matricula.Situacao.TRANSFERIDA, hoje
        atual.save(update_fields=['situacao', 'data_fim'])
        Matricula.objects.create(aluno=aluno, turma=destino, data_inicio=hoje)
        self.log('matricula_transferida', f'aluno id={aluno.id}, turma id={atual.turma_id} -> {destino.id}')
        return self.responder(aluno)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def rematricular(self, request, pk=None):
        aluno = self.get_object()
        dados = TurmaDestinoSerializer(data=request.data)
        dados.is_valid(raise_exception=True)
        destino = dados.validated_data['turma']
        ativas = aluno.matriculas.filter(situacao=Matricula.Situacao.ATIVA)
        if ativas.filter(ano_letivo=destino.ano_letivo).exists():
            return erro(f'O aluno já tem matrícula ativa em {destino.ano_letivo}.')
        ativas.update(situacao=Matricula.Situacao.ENCERRADA, data_fim=timezone.localdate())
        Matricula.objects.create(aluno=aluno, turma=destino)
        self.log('matricula_criada', f'aluno id={aluno.id}, turma id={destino.id} (rematrícula)')
        return self.responder(aluno)

    @action(detail=True, methods=['post'])
    def vincular(self, request, pk=None):
        aluno = self.get_object()
        dados = ResponsavelSerializer(data=request.data)
        dados.is_valid(raise_exception=True)
        responsavel = dados.validated_data['responsavel']
        _, criado = VinculoResponsavel.objects.get_or_create(responsavel=responsavel, aluno=aluno)
        if not criado:
            return erro('Este responsável já está vinculado ao aluno.')
        self.log('vinculo_criado', f'responsavel id={responsavel.id}, aluno id={aluno.id}')
        return self.responder(aluno)

    @action(detail=True, methods=['post'])
    def desvincular(self, request, pk=None):
        aluno = self.get_object()
        dados = ResponsavelSerializer(data=request.data)
        dados.is_valid(raise_exception=True)
        responsavel = dados.validated_data['responsavel']
        vinculo = VinculoResponsavel.objects.filter(responsavel=responsavel, aluno=aluno).first()
        if vinculo is None:
            return erro('Este responsável não está vinculado ao aluno.')
        if not VinculoResponsavel.objects.filter(aluno=aluno).exclude(pk=vinculo.pk).exists():
            return erro('O aluno precisa ter ao menos um responsável. Vincule outro antes de remover este.')
        ultimo = not VinculoResponsavel.objects.filter(responsavel=responsavel).exclude(pk=vinculo.pk).exists()
        if ultimo and not dados.validated_data['confirmar']:
            return Response(
                {'detail': 'O responsável ficará sem alunos vinculados e perderá o acesso aos dados acadêmicos. '
                           'Confirme para continuar.', 'requer_confirmacao': True},
                status=status.HTTP_409_CONFLICT,
            )
        vinculo.delete()
        self.log('vinculo_removido', f'responsavel id={responsavel.id}, aluno id={aluno.id}')
        return self.responder(aluno)


def erro(mensagem):
    return Response({'detail': mensagem}, status=status.HTTP_400_BAD_REQUEST)
