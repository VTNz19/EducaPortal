import calendar
from datetime import date

from django.db import transaction
from django.db.models import BooleanField, Case, Q, Value, When
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.academic.models import Matricula
from apps.accounts.permissions import (
    GESTORES,
    AceitouTermosVigentes,
    IsGestor,
    IsProfessor,
    PodeGerenciarAviso,
    PodeGerenciarTarefa,
)
from apps.audit.utils import registrar_log

from .consultas import eventos_visiveis, tarefas_visiveis
from .models import AnexoTarefa, Aviso
from .notificacoes import notificar_aviso, notificar_tarefa
from .serializers import AvisoSerializer, EventoCalendarioSerializer, TarefaSerializer


class AvisoViewSet(viewsets.ModelViewSet):
    serializer_class = AvisoSerializer

    def get_queryset(self):
        """RN40: cada perfil vê os avisos gerais e os das suas turmas, dentro do período (RN34).

        Gestores veem tudo; o autor também vê os próprios avisos agendados ou encerrados.
        """
        usuario = self.request.user
        qs = Aviso.objects.select_related('autor', 'turma')
        if usuario.role in GESTORES:
            return qs

        if usuario.role == 'professor':
            turmas = Q(turma__disciplinas__professor=usuario)
        elif usuario.role == 'aluno':
            turmas = Q(turma__matriculas__aluno=usuario, turma__matriculas__situacao=Matricula.Situacao.ATIVA)
        else:
            turmas = Q(turma__matriculas__aluno__vinculos_como_aluno__responsavel=usuario,
                       turma__matriculas__situacao=Matricula.Situacao.ATIVA)

        hoje = timezone.localdate()
        vigente = Q(inicio_exibicao__lte=hoje) & (Q(fim_exibicao__isnull=True) | Q(fim_exibicao__gte=hoje))
        visiveis = (Q(turma__isnull=True) | turmas) & vigente
        return qs.filter(visiveis | Q(autor=usuario)).distinct()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), AceitouTermosVigentes(), PodeGerenciarAviso()]
        return [IsAuthenticated(), AceitouTermosVigentes()]

    def perform_create(self, serializer):
        aviso = serializer.save(autor=self.request.user)
        registrar_log(
            self.request.user,
            'aviso_criado',
            detalhes=f'Aviso "{aviso.titulo}" (id={aviso.id})',
            request=self.request,
        )
        if aviso.notificar_email and aviso.situacao == 'vigente':
            notificar_aviso(aviso, self.request)

    def perform_update(self, serializer):
        aviso = serializer.save()
        registrar_log(
            self.request.user,
            'aviso_editado',
            detalhes=f'Aviso "{aviso.titulo}" (id={aviso.id})',
            request=self.request,
        )

    def perform_destroy(self, instance):
        titulo = instance.titulo
        aviso_id = instance.id
        instance.delete()
        registrar_log(
            self.request.user,
            'aviso_excluido',
            detalhes=f'Aviso "{titulo}" (id={aviso_id})',
            request=self.request,
        )


class TarefaViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                    mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """RF19: o professor publica e exclui; aluno e responsável consultam e baixam os anexos."""

    serializer_class = TarefaSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = None

    def get_queryset(self):
        hoje = timezone.localdate()
        encerrada = Case(When(prazo__lt=hoje, then=Value(True)), default=Value(False), output_field=BooleanField())
        return tarefas_visiveis(self.request.user).annotate(encerrada_ordem=encerrada).order_by(
            'encerrada_ordem', 'prazo', 'id')

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), AceitouTermosVigentes(), IsProfessor()]
        if self.action == 'destroy':
            return [IsAuthenticated(), AceitouTermosVigentes(), PodeGerenciarTarefa()]
        return [IsAuthenticated(), AceitouTermosVigentes()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        arquivos = serializer.validated_data.pop('arquivos', [])
        with transaction.atomic():
            tarefa = serializer.save(autor=request.user)
            for arquivo in arquivos:
                AnexoTarefa.objects.create(tarefa=tarefa, arquivo=arquivo, nome_original=arquivo.name[:255],
                                           tamanho=arquivo.size)
        registrar_log(request.user, 'tarefa_criada',
                      detalhes=f'Tarefa "{tarefa.titulo}" (id={tarefa.id}), disciplina id={tarefa.disciplina_id}, '
                               f'{len(arquivos)} anexo(s)', request=request)
        enviado = notificar_tarefa(tarefa, request)
        dados = self.get_serializer(self.get_queryset().get(pk=tarefa.pk)).data
        return Response({**dados, 'email_enviado': enviado}, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        titulo, tarefa_id = instance.titulo, instance.id
        arquivos = [a.arquivo for a in instance.anexos.all()]
        instance.delete()
        for arquivo in arquivos:
            arquivo.delete(save=False)
        registrar_log(self.request.user, 'tarefa_excluida', detalhes=f'Tarefa "{titulo}" (id={tarefa_id})',
                      request=self.request)

    @action(detail=True, methods=['get'], url_path=r'anexos/(?P<anexo_id>\d+)')
    def anexo(self, request, pk=None, anexo_id=None):
        """O arquivo só é entregue a quem vê a tarefa; não há link público para os anexos."""
        anexo = get_object_or_404(self.get_object().anexos, pk=anexo_id)
        return FileResponse(anexo.arquivo.open('rb'), as_attachment=True, filename=anexo.nome_original)


def intervalo_do_mes(texto):
    """Converte "2026-11" no primeiro e no último dia do mês."""
    try:
        ano, mes = (int(parte) for parte in texto.split('-'))
        ultimo = calendar.monthrange(ano, mes)[1]
        return date(ano, mes, 1), date(ano, mes, ultimo)
    except ValueError:
        raise ValidationError({'mes': ['Informe o mês no formato AAAA-MM.']}) from None


class EventoCalendarioViewSet(viewsets.ModelViewSet):
    """RF20: os gestores cadastram eventos; todos consultam os que podem ver."""

    serializer_class = EventoCalendarioSerializer
    pagination_class = None

    def get_queryset(self):
        qs = eventos_visiveis(self.request.user)
        mes = self.request.query_params.get('mes')
        if mes:
            primeiro, ultimo = intervalo_do_mes(mes)
            qs = qs.filter(inicio__lte=ultimo, fim__gte=primeiro)
        return qs.order_by('inicio', 'id')

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), AceitouTermosVigentes(), IsGestor()]
        return [IsAuthenticated(), AceitouTermosVigentes()]

    def log(self, acao, evento_id, titulo):
        registrar_log(self.request.user, acao, detalhes=f'Evento "{titulo}" (id={evento_id})', request=self.request)

    def perform_create(self, serializer):
        evento = serializer.save(criado_por=self.request.user)
        self.log('evento_criado', evento.id, evento.titulo)

    def perform_update(self, serializer):
        evento = serializer.save()
        self.log('evento_editado', evento.id, evento.titulo)

    def perform_destroy(self, instance):
        evento_id, titulo = instance.id, instance.titulo
        instance.delete()
        self.log('evento_excluido', evento_id, titulo)
