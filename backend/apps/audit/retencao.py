"""Retenção e descarte de dados (RF22), conforme o Plano de Retenção e Descarte de Dados.

RN81: logs de auditoria, 6 meses; links de senha, 7 dias após a criação; avisos, 1 ano após a
publicação; tarefas e seus anexos, 1 ano após o prazo de entrega; eventos do calendário, 1 ano
após o término; contas desligadas, anonimizadas após 1 ano letivo.
RN82: o registro da execução traz só as quantidades, sem dados pessoais.
"""
import calendar
from datetime import timedelta

from django.db import transaction
from django.db.models import Q, Value
from django.db.models.functions import Replace
from django.utils import timezone

from .utils import registrar_log

EMAIL_REMOVIDO = '[e-mail removido]'


def meses_antes(momento, meses):
    """Mesmo dia, `meses` meses antes; em meses mais curtos, o último dia do mês (31/08 -> 28/02)."""
    total = momento.year * 12 + momento.month - 1 - meses
    ano, mes = divmod(total, 12)
    mes += 1
    dia = min(momento.day, calendar.monthrange(ano, mes)[1])
    return momento.replace(year=ano, month=mes, day=dia)


def limites(agora):
    """Data e hora (ou data) antes da qual cada tipo de registro está vencido."""
    hoje = timezone.localdate(agora)
    return {
        'logs_auditoria': meses_antes(agora, 6),
        'links_senha': agora - timedelta(days=7),
        'avisos': meses_antes(agora, 12),
        'tarefas': meses_antes(hoje, 12),
        'eventos': meses_antes(hoje, 12),
        'contas': meses_antes(agora, 12),
    }


def descrever(contagem):
    return ', '.join(f'{tipo}={quantidade}' for tipo, quantidade in contagem.items())


def anonimizar_conta(usuario, agora):
    """O registro continua existindo (notas, avisos e logs apontam para ele), mas sem identificar a pessoa."""
    from apps.accounts.models import PasswordResetToken

    from .models import AuditLog

    email_antigo = usuario.email
    usuario.first_name = 'Usuário'
    usuario.last_name = 'removido'
    usuario.username = f'removido-{usuario.pk}'
    usuario.email = f'removido-{usuario.pk}@anonimizado.invalid'
    usuario.is_active = False
    usuario.termos_versao_aceita = ''
    usuario.termos_aceitos_em = None
    usuario.anonimizado_em = agora
    usuario.set_unusable_password()
    usuario.save()
    PasswordResetToken.objects.filter(usuario=usuario).delete()
    if email_antigo:
        AuditLog.objects.filter(detalhes__contains=email_antigo).update(
            detalhes=Replace('detalhes', Value(email_antigo), Value(EMAIL_REMOVIDO)))


def descartar(agora):
    from apps.accounts.models import PasswordResetToken, User
    from apps.communication.models import AnexoTarefa, Aviso, EventoCalendario, Tarefa

    from .models import AuditLog

    limite = limites(agora)
    contagem = {}
    contagem['logs_auditoria'] = AuditLog.objects.filter(criado_em__lt=limite['logs_auditoria']).delete()[0]
    contagem['links_senha'] = PasswordResetToken.objects.filter(criado_em__lt=limite['links_senha']).delete()[0]
    contagem['avisos'] = Aviso.objects.filter(criado_em__lt=limite['avisos']).delete()[0]

    tarefas = Tarefa.objects.filter(prazo__lt=limite['tarefas'])
    arquivos = [a.arquivo.name for a in AnexoTarefa.objects.filter(tarefa__in=tarefas)]
    contagem['tarefas'] = tarefas.delete()[1].get('communication.Tarefa', 0)
    contagem['anexos'] = len(arquivos)
    contagem['eventos'] = EventoCalendario.objects.filter(fim__lt=limite['eventos']).delete()[0]

    contas = User.objects.filter(is_active=False, anonimizado_em__isnull=True,
                                 desativado_em__lt=limite['contas'])
    contagem['contas_anonimizadas'] = 0
    for usuario in contas:
        anonimizar_conta(usuario, agora)
        contagem['contas_anonimizadas'] += 1
    return contagem, arquivos


def apagar_arquivos(nomes):
    """Os arquivos só saem do disco depois que a exclusão no banco foi confirmada."""
    from apps.communication.models import AnexoTarefa

    armazenamento = AnexoTarefa._meta.get_field('arquivo').storage
    for nome in nomes:
        armazenamento.delete(nome)


def aplicar_retencao(agora=None):
    """Executa o descarte em uma única transação: em caso de erro, nada é alterado (fluxo de exceção)."""
    agora = agora or timezone.now()
    try:
        with transaction.atomic():
            contagem, arquivos = descartar(agora)
            transaction.on_commit(lambda: apagar_arquivos(arquivos))
    except Exception as erro:
        registrar_log(None, 'retencao_falha', detalhes=f'erro: {erro.__class__.__name__}')
        raise
    registrar_log(None, 'retencao_executada', detalhes=descrever(contagem))
    return contagem


CONFIRMACAO_ANONIMIZAR = 'ANONIMIZAR'


def impedimentos_para_anonimizar(usuario, solicitante):
    """Motivos que impedem a anonimização a pedido do titular; lista vazia quando ela pode ser feita."""
    from apps.academic.models import AnoLetivo, Disciplina, Matricula, VinculoResponsavel

    if usuario.pk == solicitante.pk:
        return ['Você não pode anonimizar a própria conta.']
    if usuario.anonimizado_em:
        return ['Esta conta já foi anonimizada.']
    if usuario.is_superuser:
        return ['Contas de administração técnica não podem ser anonimizadas pelo painel.']

    motivos = []
    ano = AnoLetivo.atual()
    disciplinas = Disciplina.objects.filter(professor=usuario, turma__ano_letivo=ano).select_related('turma')
    if ano and disciplinas.exists():
        nomes = ', '.join(f'{d.nome} – {d.turma.nome}' for d in disciplinas.order_by('turma__nome', 'nome'))
        motivos.append(f'Troque o professor das disciplinas do ano letivo atual antes de anonimizar: {nomes}.')

    alunos_ativos = Matricula.objects.filter(situacao=Matricula.Situacao.ATIVA).values('aluno')
    vinculos = VinculoResponsavel.objects.filter(responsavel=usuario, aluno__in=alunos_ativos).select_related('aluno')
    for vinculo in vinculos:
        if not VinculoResponsavel.objects.filter(aluno=vinculo.aluno).exclude(responsavel=usuario).exists():
            nome = vinculo.aluno.get_full_name() or vinculo.aluno.username
            motivos.append(f'Vincule outro responsável a {nome} antes de anonimizar (RN85).')
    return motivos


def anonimizar_a_pedido(usuario, agora=None):
    """Atende o pedido de eliminação do titular (art. 18 da LGPD), feito pela secretaria ou pela direção.

    No aluno, a matrícula ativa é encerrada; as notas e as faltas continuam ligadas ao registro anônimo
    (RN56). Os vínculos entre aluno e responsável da pessoa são removidos; para os alunos ativos, a RN85 já
    foi verificada em impedimentos_para_anonimizar.
    """
    from apps.academic.models import Matricula, VinculoResponsavel

    agora = agora or timezone.now()
    with transaction.atomic():
        Matricula.objects.filter(aluno=usuario, situacao=Matricula.Situacao.ATIVA).update(
            situacao=Matricula.Situacao.ENCERRADA, data_fim=timezone.localdate(agora))
        VinculoResponsavel.objects.filter(Q(aluno=usuario) | Q(responsavel=usuario)).delete()
        anonimizar_conta(usuario, agora)
    return usuario
