"""Serviços do módulo acadêmico que consultam o banco: bimestres, boletim e notificações."""
from django.conf import settings
from django.db.models import Sum
from django.utils.html import escape
from django.utils import timezone

from apps.accounts.emails import enviar_email_em_lote
from apps.audit.utils import registrar_log
from .calculos import abaixo_da_frequencia, abaixo_da_media, calcular_frequencia, calcular_media
from .models import Bimestre, Chamada, Falta, Matricula, Nota, VinculoResponsavel


def bimestre_da_data(ano_letivo, data):
    """RN64: devolve o bimestre que contém a data, ou None."""
    return Bimestre.objects.filter(ano_letivo=ano_letivo, inicio__lte=data, fim__gte=data).first()


def bimestre_em_andamento(ano_letivo):
    """Bimestre que contém a data de hoje; fora do período, o último já iniciado (ou o 1º)."""
    hoje = timezone.localdate()
    atual = bimestre_da_data(ano_letivo, hoje)
    if atual:
        return atual
    iniciados = Bimestre.objects.filter(ano_letivo=ano_letivo, inicio__lte=hoje).order_by('-numero')
    return iniciados.first() or Bimestre.objects.filter(ano_letivo=ano_letivo).order_by('numero').first()


def boletim_da_matricula(matricula, somente_publicadas=True):
    """Notas por bimestre, média, faltas e frequência de cada disciplina da turma."""
    disciplinas = matricula.turma.disciplinas.select_related('professor').order_by('nome')
    notas = Nota.objects.filter(matricula=matricula).select_related('bimestre')
    if somente_publicadas:
        notas = notas.filter(publicada=True)
    por_disciplina = {}
    for nota in notas:
        por_disciplina.setdefault(nota.disciplina_id, {})[nota.bimestre.numero] = nota.valor

    fim = matricula.data_fim or timezone.localdate()
    linhas = []
    for disciplina in disciplinas:
        notas_bim = por_disciplina.get(disciplina.id, {})
        media, parcial = calcular_media(notas_bim.values())
        chamadas = Chamada.objects.filter(disciplina=disciplina, data__gte=matricula.data_inicio, data__lte=fim)
        aulas = chamadas.aggregate(total=Sum('quantidade_aulas'))['total'] or 0
        faltas = Falta.objects.filter(chamada__in=chamadas, matricula=matricula).aggregate(
            total=Sum('quantidade'))['total'] or 0
        frequencia = calcular_frequencia(aulas, faltas)
        linhas.append({
            'disciplina_id': disciplina.id,
            'disciplina': disciplina.nome,
            'professor': disciplina.professor.get_full_name() or disciplina.professor.username,
            'notas': {str(n): notas_bim.get(n) for n in range(1, 5)},
            'media': media,
            'media_parcial': parcial,
            'abaixo_media': abaixo_da_media(media),
            'aulas': aulas,
            'faltas': faltas,
            'frequencia': frequencia,
            'abaixo_frequencia': abaixo_da_frequencia(frequencia),
        })
    aluno = matricula.aluno
    return {
        'aluno': {'id': aluno.id, 'nome': aluno.get_full_name() or aluno.username},
        'ano': matricula.ano_letivo.ano,
        'turma': matricula.turma.nome,
        'situacao_matricula': matricula.situacao,
        'disciplinas': linhas,
    }


def matricula_do_boletim(aluno, ano=None):
    """Matrícula ativa do aluno ou, informado o ano, a mais recente daquele ano."""
    matriculas = Matricula.objects.filter(aluno=aluno).select_related('turma', 'ano_letivo')
    if ano:
        return matriculas.filter(ano_letivo__ano=ano).order_by('-data_inicio', '-id').first()
    return (matriculas.filter(situacao=Matricula.Situacao.ATIVA).order_by('-ano_letivo__ano').first()
            or matriculas.order_by('-ano_letivo__ano', '-data_inicio').first())


def emails_do_aluno_e_responsaveis(alunos):
    emails = [a.email for a in alunos]
    emails += VinculoResponsavel.objects.filter(aluno__in=alunos).values_list('responsavel__email', flat=True)
    return [e for e in emails if e]


def notificar(destinatarios, assunto, texto, caminho, usuario, request, acao_falha='notificacao_falha_envio'):
    """Envia o aviso por e-mail sem dados acadêmicos (RN61, RN66). Uma falha no envio é
    registrada no log e não desfaz a operação (RNF09)."""
    link = f'{settings.FRONTEND_URL}{caminho}'
    html = (
        f'<p>Olá.</p><p>{escape(texto)}</p>'
        f'<p><a href="{link}">Acesse o EducaPortal para ver os detalhes</a>.</p>'
        f'<p>Este é um aviso automático. Por segurança, ele não traz notas nem faltas.</p>'
    )
    try:
        enviar_email_em_lote(destinatarios, assunto, html)
        return True
    except Exception as erro:
        registrar_log(usuario, acao_falha, detalhes=f'{assunto} | erro: {erro}', request=request)
        return False
