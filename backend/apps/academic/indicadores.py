"""Indicadores do painel (RF21). Tudo é calculado na consulta (RN70), com as mesmas regras do boletim."""
import unicodedata
from collections import defaultdict

from django.conf import settings
from django.db.models import Avg, Count
from django.utils import timezone

from apps.accounts.models import User
from .calculos import (
    abaixo_da_frequencia,
    abaixo_da_media,
    arredondar,
    calcular_frequencia,
    calcular_media,
)
from .models import AnoLetivo, Bimestre, Chamada, Disciplina, Falta, Matricula, Nota, Turma
from .servicos import bimestre_em_andamento, boletim_da_matricula, matricula_do_boletim

ATIVA = Matricula.Situacao.ATIVA


def numero(valor):
    """Valores decimais seguem como número no JSON, que é o que os gráficos esperam."""
    return None if valor is None else float(valor)


def media_de(valores):
    valores = [v for v in valores if v is not None]
    return arredondar(sum(valores) / len(valores)) if valores else None


def percentual(parte, total):
    return arredondar(parte * 100 / total) if total else None


def nome_de(usuario):
    return usuario.get_full_name() or usuario.username


def chave_alfabetica(texto):
    """Ordena sem separar nomes acentuados dos demais (Álvaro antes de Ana)."""
    return unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode().casefold()


def linhas_por_aluno(turma, disciplinas):
    """Média e frequência de cada aluno ativo em cada disciplina, em poucas consultas ao banco.

    Segue as regras de boletim_da_matricula: só notas publicadas (RN59) e só chamadas do
    período da matrícula.
    """
    matriculas = list(Matricula.objects.filter(turma=turma, situacao=ATIVA).select_related('aluno'))
    ids_disciplinas = [d.id for d in disciplinas]

    notas = defaultdict(list)
    for matricula_id, disciplina_id, valor in Nota.objects.filter(
            matricula__in=matriculas, disciplina__in=ids_disciplinas, publicada=True,
    ).values_list('matricula_id', 'disciplina_id', 'valor'):
        notas[matricula_id, disciplina_id].append(valor)

    chamadas = list(Chamada.objects.filter(disciplina__in=ids_disciplinas).values_list(
        'id', 'disciplina_id', 'data', 'quantidade_aulas'))
    faltas = {
        (matricula_id, chamada_id): quantidade
        for matricula_id, chamada_id, quantidade in Falta.objects.filter(
            matricula__in=matriculas, chamada__disciplina__in=ids_disciplinas,
        ).values_list('matricula_id', 'chamada_id', 'quantidade')
    }

    hoje = timezone.localdate()
    linhas = []
    for matricula in matriculas:
        fim = matricula.data_fim or hoje
        for disciplina in disciplinas:
            aulas = total_faltas = 0
            for chamada_id, disciplina_id, data, quantidade_aulas in chamadas:
                if disciplina_id == disciplina.id and matricula.data_inicio <= data <= fim:
                    aulas += quantidade_aulas
                    total_faltas += faltas.get((matricula.id, chamada_id), 0)
            media, _ = calcular_media(notas[matricula.id, disciplina.id])
            linhas.append({
                'matricula': matricula,
                'disciplina': disciplina,
                'media': media,
                'frequencia': calcular_frequencia(aulas, total_faltas),
            })
    return linhas


def medias_do_bimestre(bimestre, disciplinas):
    """Média das notas publicadas e quantidade de notas por disciplina, só de alunos ativos."""
    return {
        linha['disciplina']: linha
        for linha in Nota.objects.filter(
            bimestre=bimestre, disciplina__in=disciplinas, publicada=True, matricula__situacao=ATIVA,
        ).values('disciplina').annotate(media=Avg('valor'), publicadas=Count('id'))
    }


def alunos_ativos_por_turma(ids_turmas):
    return dict(Matricula.objects.filter(turma__in=ids_turmas, situacao=ATIVA)
                .values_list('turma').annotate(total=Count('id')))


def pendencias_de_publicacao(bimestre, disciplinas):
    """RN84: pendente é a disciplina com aluno ativo ainda sem nota publicada no bimestre."""
    no_bimestre = medias_do_bimestre(bimestre, disciplinas)
    alunos = alunos_ativos_por_turma({d.turma_id for d in disciplinas})
    pendentes = []
    for disciplina in disciplinas:
        total = alunos.get(disciplina.turma_id, 0)
        publicadas = no_bimestre.get(disciplina.id, {}).get('publicadas', 0)
        if publicadas < total:
            pendentes.append({
                'disciplina_id': disciplina.id,
                'disciplina': disciplina.nome,
                'turma': disciplina.turma.nome,
                'professor': nome_de(disciplina.professor),
                'sem_nota_publicada': total - publicadas,
            })
    return pendentes


def tem_registros_no_bimestre(bimestre, disciplinas):
    return (Nota.objects.filter(bimestre=bimestre, disciplina__in=disciplinas, publicada=True).exists()
            or Chamada.objects.filter(bimestre=bimestre, disciplina__in=disciplinas).exists())


def escolher_bimestre(ano, numero_bimestre=None):
    if numero_bimestre is not None:
        return Bimestre.objects.filter(ano_letivo=ano, numero=numero_bimestre).first()
    return bimestre_em_andamento(ano)


def descrever_bimestre(bimestre):
    return {'numero': bimestre.numero, 'inicio': bimestre.inicio, 'fim': bimestre.fim}


def painel_do_aluno(aluno, alunos_disponiveis):
    base = {
        'perfil': 'aluno',
        'alunos': [{'id': a.id, 'nome': nome_de(a)} for a in alunos_disponiveis],
        'aluno': aluno and {'id': aluno.id, 'nome': nome_de(aluno)},
        'sem_dados': True,
    }
    matricula = aluno and matricula_do_boletim(aluno)
    if not matricula:
        return base

    boletim = boletim_da_matricula(matricula)
    linhas = boletim['disciplinas']
    aulas = sum(linha['aulas'] for linha in linhas)
    faltas = sum(linha['faltas'] for linha in linhas)
    medias = [linha['media'] for linha in linhas]
    return {
        **base,
        'ano': boletim['ano'],
        'turma': boletim['turma'],
        'sem_dados': aulas == 0 and all(media is None for media in medias),
        'resumo': {
            'media_geral': numero(media_de(medias)),
            'frequencia_geral': numero(calcular_frequencia(aulas, faltas)),
            'disciplinas_abaixo_media': sum(linha['abaixo_media'] for linha in linhas),
            'disciplinas_abaixo_frequencia': sum(linha['abaixo_frequencia'] for linha in linhas),
        },
        'disciplinas': [{
            'id': linha['disciplina_id'],
            'disciplina': linha['disciplina'],
            'media': numero(linha['media']),
            'media_parcial': linha['media_parcial'],
            'abaixo_media': linha['abaixo_media'],
            'faltas': linha['faltas'],
            'frequencia': numero(linha['frequencia']),
            'abaixo_frequencia': linha['abaixo_frequencia'],
        } for linha in linhas],
        'evolucao': [{
            'bimestre': int(bimestre),
            'media': numero(media_de([linha['notas'][bimestre] for linha in linhas])),
        } for bimestre in ('1', '2', '3', '4')],
    }


def painel_do_professor(professor, numero_bimestre=None):
    base = {'perfil': 'professor', 'sem_dados': True, 'disciplinas': [], 'pendencias': []}
    ano = AnoLetivo.atual()
    bimestre = ano and escolher_bimestre(ano, numero_bimestre)
    if not bimestre:
        return base

    disciplinas = list(Disciplina.objects.filter(professor=professor, turma__ano_letivo=ano)
                       .select_related('turma', 'professor').order_by('turma__nome', 'nome'))
    no_bimestre = medias_do_bimestre(bimestre, disciplinas)
    alunos = alunos_ativos_por_turma({d.turma_id for d in disciplinas})

    por_disciplina = defaultdict(list)
    for turma in {d.turma for d in disciplinas}:
        for linha in linhas_por_aluno(turma, [d for d in disciplinas if d.turma_id == turma.id]):
            por_disciplina[linha['disciplina'].id].append(linha)

    itens = []
    for disciplina in disciplinas:
        linhas = por_disciplina[disciplina.id]
        media = no_bimestre.get(disciplina.id, {}).get('media')
        itens.append({
            'id': disciplina.id,
            'disciplina': disciplina.nome,
            'turma': disciplina.turma.nome,
            'alunos': alunos.get(disciplina.turma_id, 0),
            'media_bimestre': numero(None if media is None else arredondar(media)),
            'abaixo_media': sum(abaixo_da_media(linha['media']) for linha in linhas),
            'abaixo_frequencia': sum(abaixo_da_frequencia(linha['frequencia']) for linha in linhas),
        })
    return {
        **base,
        'ano': ano.ano,
        'bimestre': descrever_bimestre(bimestre),
        'sem_dados': not tem_registros_no_bimestre(bimestre, disciplinas),
        'disciplinas': itens,
        'pendencias': pendencias_de_publicacao(bimestre, disciplinas),
    }


def alunos_na_situacao(disciplina, situacao):
    """RN80: lista nominal da disciplina, em ordem alfabética, sem ranking por nota."""
    abaixo, campo = ((abaixo_da_media, 'media') if situacao == 'abaixo_media'
                     else (abaixo_da_frequencia, 'frequencia'))
    alunos = [{
        'id': linha['matricula'].aluno_id,
        'nome': nome_de(linha['matricula'].aluno),
        'media': numero(linha['media']),
        'frequencia': numero(linha['frequencia']),
    } for linha in linhas_por_aluno(disciplina.turma, [disciplina]) if abaixo(linha[campo])]
    return sorted(alunos, key=lambda aluno: chave_alfabetica(aluno['nome']))


def painel_do_gestor(numero_bimestre=None):
    contas_sem_aceite = (User.objects.filter(is_active=True)
                         .exclude(termos_versao_aceita=settings.VERSAO_TERMOS).count())
    base = {
        'perfil': 'gestor',
        'sem_dados': True,
        'contas_sem_aceite': contas_sem_aceite,
        'turmas': [],
        'pendencias': [],
    }
    ano = AnoLetivo.atual()
    bimestre = ano and escolher_bimestre(ano, numero_bimestre)
    if not bimestre:
        return base

    disciplinas = list(Disciplina.objects.filter(turma__ano_letivo=ano)
                       .select_related('turma', 'professor').order_by('turma__nome', 'nome'))
    alunos_por_turma = alunos_ativos_por_turma(Turma.objects.filter(ano_letivo=ano))

    turmas = []
    total_alunos = total_abaixo_media = total_abaixo_frequencia = 0
    todas_as_medias = []
    for turma in Turma.objects.filter(ano_letivo=ano).order_by('nome'):
        linhas = linhas_por_aluno(turma, [d for d in disciplinas if d.turma_id == turma.id])
        alunos = alunos_por_turma.get(turma.id, 0)
        abaixo_media = len({linha['matricula'].id for linha in linhas if abaixo_da_media(linha['media'])})
        abaixo_frequencia = len({linha['matricula'].id for linha in linhas
                                 if abaixo_da_frequencia(linha['frequencia'])})
        medias = [linha['media'] for linha in linhas]
        total_alunos += alunos
        total_abaixo_media += abaixo_media
        total_abaixo_frequencia += abaixo_frequencia
        todas_as_medias += medias
        turmas.append({
            'id': turma.id,
            'turma': turma.nome,
            'alunos': alunos,
            'media_geral': numero(media_de(medias)),
            'percentual_abaixo_media': numero(percentual(abaixo_media, alunos)),
            'percentual_abaixo_frequencia': numero(percentual(abaixo_frequencia, alunos)),
        })

    por_bimestre = dict(Nota.objects.filter(
        bimestre__ano_letivo=ano, publicada=True, matricula__situacao=ATIVA,
    ).values_list('bimestre__numero').annotate(media=Avg('valor')))
    return {
        **base,
        'ano': ano.ano,
        'bimestre': descrever_bimestre(bimestre),
        'sem_dados': not tem_registros_no_bimestre(bimestre, disciplinas),
        'resumo': {
            'alunos': total_alunos,
            'media_geral': numero(media_de(todas_as_medias)),
            'percentual_abaixo_media': numero(percentual(total_abaixo_media, total_alunos)),
            'percentual_abaixo_frequencia': numero(percentual(total_abaixo_frequencia, total_alunos)),
        },
        'turmas': turmas,
        'pendencias': pendencias_de_publicacao(bimestre, disciplinas),
        'evolucao': [{
            'bimestre': n,
            'media': numero(arredondar(por_bimestre[n]) if n in por_bimestre else None),
        } for n in range(1, 5)],
    }
