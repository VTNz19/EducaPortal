"""Quem vê cada tarefa e cada evento (CA02 do RF19 e do RF20) e a agenda do painel do aluno (RF21)."""
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from apps.academic.models import Matricula, Turma
from apps.accounts.permissions import GESTORES

from .models import EventoCalendario, Tarefa

ATIVA = Matricula.Situacao.ATIVA
DIAS_DA_AGENDA = 7
EVENTOS_NO_PAINEL = 5


def turmas_do_usuario(usuario):
    """Turmas que o usuário acompanha; None para os gestores, que veem todas."""
    if usuario.role in GESTORES:
        return None
    if usuario.role == 'professor':
        return Turma.objects.filter(disciplinas__professor=usuario).values('id')
    if usuario.role == 'aluno':
        return Matricula.objects.filter(aluno=usuario, situacao=ATIVA).values('turma')
    return Matricula.objects.filter(aluno__vinculos_como_aluno__responsavel=usuario, situacao=ATIVA).values('turma')


def tarefas_visiveis(usuario):
    """O professor vê as tarefas das suas disciplinas; aluno e responsável, as das turmas que acompanham."""
    qs = Tarefa.objects.select_related('disciplina__turma', 'autor').prefetch_related('anexos')
    if usuario.role in GESTORES:
        return qs
    if usuario.role == 'professor':
        return qs.filter(disciplina__professor=usuario)
    return qs.filter(disciplina__turma__in=turmas_do_usuario(usuario))


def eventos_visiveis(usuario):
    """Eventos gerais para todos; eventos de turma só para quem acompanha a turma."""
    qs = EventoCalendario.objects.select_related('turma')
    turmas = turmas_do_usuario(usuario)
    if turmas is None:
        return qs
    return qs.filter(Q(turma__isnull=True) | Q(turma__in=turmas))


def agenda_do_aluno(aluno):
    """Tarefas com prazo nos próximos 7 dias e próximos eventos da turma do aluno."""
    if aluno is None:
        return {'tarefas_proximas': [], 'proximos_eventos': []}
    hoje = timezone.localdate()
    turmas = Matricula.objects.filter(aluno=aluno, situacao=ATIVA).values('turma')
    tarefas = (Tarefa.objects.filter(disciplina__turma__in=turmas, prazo__gte=hoje,
                                     prazo__lte=hoje + timedelta(days=DIAS_DA_AGENDA))
               .select_related('disciplina').order_by('prazo', 'id'))
    eventos = (EventoCalendario.objects.filter(Q(turma__isnull=True) | Q(turma__in=turmas), fim__gte=hoje)
               .select_related('turma').order_by('inicio', 'id')[:EVENTOS_NO_PAINEL])
    return {
        'tarefas_proximas': [{
            'id': t.id, 'titulo': t.titulo, 'disciplina': t.disciplina.nome, 'prazo': t.prazo,
        } for t in tarefas],
        'proximos_eventos': [{
            'id': e.id, 'titulo': e.titulo, 'tipo': e.tipo, 'tipo_nome': e.get_tipo_display(),
            'inicio': e.inicio, 'fim': e.fim, 'turma': e.turma.nome if e.turma else None,
        } for e in eventos],
    }
