"""Notificação de avisos por e-mail (RF08, RN35)."""
from django.utils import timezone

from apps.academic.models import Matricula, VinculoResponsavel
from apps.academic.servicos import notificar
from apps.accounts.models import User
from apps.audit.utils import registrar_log


def destinatarios_do_aviso(aviso):
    """Toda a escola, ou alunos, responsáveis e professores da turma (RN40)."""
    if aviso.turma_id is None:
        emails = User.objects.filter(is_active=True).exclude(pk=aviso.autor_id).values_list('email', flat=True)
        return [e for e in emails if e]
    alunos = Matricula.objects.filter(turma_id=aviso.turma_id, situacao=Matricula.Situacao.ATIVA).values('aluno')
    emails = list(User.objects.filter(pk__in=alunos, is_active=True).values_list('email', flat=True))
    emails += VinculoResponsavel.objects.filter(aluno__in=alunos).values_list('responsavel__email', flat=True)
    emails += User.objects.filter(disciplinas__turma_id=aviso.turma_id).values_list('email', flat=True)
    autor = aviso.autor.email if aviso.autor else None
    return [e for e in set(emails) if e and e != autor]


def notificar_aviso(aviso, request=None):
    """Envia o e-mail com o título e o link (sem o conteúdo) e marca o aviso como notificado."""
    destinatarios = destinatarios_do_aviso(aviso)
    ok = notificar(destinatarios, f'Novo aviso no EducaPortal: {aviso.titulo}',
                   f'Foi publicado o aviso "{aviso.titulo}".', '/mural', aviso.autor, request,
                   acao_falha='aviso_falha_envio')
    if ok:
        aviso.notificado_em = timezone.now()
        aviso.save(update_fields=['notificado_em'])
        registrar_log(aviso.autor, 'aviso_notificado',
                      detalhes=f'aviso id={aviso.id}, {len(destinatarios)} destinatário(s)', request=request)
    return ok
