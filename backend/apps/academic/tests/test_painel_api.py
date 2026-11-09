"""Testes de integração do painel de indicadores (RF21, RN79, RN80, RN83 e RN84)."""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.academic.models import (
    AnoLetivo, Bimestre, Chamada, Disciplina, Falta, Matricula, Nota, Turma, VinculoResponsavel,
)

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]

URL = '/api/v1/painel/'


@pytest.fixture
def escola(criar_usuario):
    """Turma com Ana (média 5,0 e 50% de frequência) e Bruno (média 8,0 e 100%)."""
    hoje = timezone.localdate()
    ano = AnoLetivo.objects.create(ano=hoje.year, ativo=True)
    primeiro = Bimestre.objects.create(ano_letivo=ano, numero=1, inicio=hoje, fim=hoje)
    for numero in range(2, 5):
        dia = hoje + timedelta(days=numero)
        Bimestre.objects.create(ano_letivo=ano, numero=numero, inicio=dia, fim=dia)
    turma = Turma.objects.create(ano_letivo=ano, nome='3º A', serie='3ª série', turno='manha')
    professor = criar_usuario('professor', email='prof@exemplo.com')
    disciplina = Disciplina.objects.create(turma=turma, nome='Matemática', carga_horaria=160, professor=professor)
    ana = criar_usuario('aluno', email='ana@exemplo.com', first_name='Ana', last_name='Souza')
    bruno = criar_usuario('aluno', email='bruno@exemplo.com', first_name='Bruno', last_name='Lima')
    matricula_ana = Matricula.objects.create(aluno=ana, turma=turma, data_inicio=hoje)
    matricula_bruno = Matricula.objects.create(aluno=bruno, turma=turma, data_inicio=hoje)
    Nota.objects.create(matricula=matricula_ana, disciplina=disciplina, bimestre=primeiro,
                        valor=Decimal('5.0'), publicada=True)
    Nota.objects.create(matricula=matricula_bruno, disciplina=disciplina, bimestre=primeiro,
                        valor=Decimal('8.0'), publicada=True)
    chamada = Chamada.objects.create(disciplina=disciplina, bimestre=primeiro, data=hoje, quantidade_aulas=2)
    Falta.objects.create(chamada=chamada, matricula=matricula_ana, quantidade=1)
    return {'turma': turma, 'professor': professor, 'disciplina': disciplina, 'ana': ana, 'bruno': bruno,
            'primeiro': primeiro, 'matricula_ana': matricula_ana}


def url_lista(escola):
    return f"/api/v1/painel/disciplinas/{escola['disciplina'].id}/alunos/"


def test_aluno_ve_apenas_os_proprios_indicadores(escola, cliente_autenticado):
    dados = cliente_autenticado(escola['ana']).get(URL).json()

    assert dados['aluno']['nome'] == 'Ana Souza'
    assert [a['nome'] for a in dados['alunos']] == ['Ana Souza']
    assert dados['resumo'] == {'media_geral': 5.0, 'frequencia_geral': 50.0, 'disciplinas_abaixo_media': 1,
                               'disciplinas_abaixo_frequencia': 1}
    assert dados['evolucao'][0] == {'bimestre': 1, 'media': 5.0}
    assert 'Bruno' not in str(dados)


def test_painel_do_aluno_traz_os_mesmos_numeros_do_boletim(escola, cliente_autenticado):
    cliente = cliente_autenticado(escola['ana'])

    painel = cliente.get(URL).json()['disciplinas'][0]
    boletim = cliente.get(f"/api/v1/boletim/{escola['ana'].id}/").json()['disciplinas'][0]

    for campo in ('media', 'frequencia', 'faltas'):
        assert float(painel[campo]) == float(boletim[campo])


def test_aluno_nao_escolhe_outro_aluno(escola, cliente_autenticado):
    response = cliente_autenticado(escola['ana']).get(URL, {'aluno': escola['bruno'].id})

    assert response.status_code == 403


def test_responsavel_escolhe_entre_os_alunos_vinculados(escola, criar_usuario, cliente_autenticado):
    responsavel = criar_usuario('responsavel')
    VinculoResponsavel.objects.create(responsavel=responsavel, aluno=escola['ana'])
    VinculoResponsavel.objects.create(responsavel=responsavel, aluno=escola['bruno'])

    dados = cliente_autenticado(responsavel).get(URL, {'aluno': escola['bruno'].id}).json()

    assert len(dados['alunos']) == 2
    assert dados['aluno']['nome'] == 'Bruno Lima'
    assert dados['resumo']['media_geral'] == 8.0


def test_responsavel_nao_ve_aluno_sem_vinculo(escola, criar_usuario, cliente_autenticado):
    responsavel = criar_usuario('responsavel')
    VinculoResponsavel.objects.create(responsavel=responsavel, aluno=escola['ana'])

    response = cliente_autenticado(responsavel).get(URL, {'aluno': escola['bruno'].id})

    assert response.status_code == 403


def test_responsavel_sem_vinculo_recebe_painel_vazio(criar_usuario, cliente_autenticado):
    dados = cliente_autenticado(criar_usuario('responsavel')).get(URL).json()

    assert dados['sem_dados'] is True
    assert dados['aluno'] is None


def test_nota_nao_publicada_fica_fora_do_painel_do_aluno(escola, cliente_autenticado):
    Nota.objects.update(publicada=False)

    dados = cliente_autenticado(escola['ana']).get(URL).json()

    assert dados['resumo']['media_geral'] is None


def test_professor_ve_indicadores_das_suas_disciplinas(escola, cliente_autenticado):
    dados = cliente_autenticado(escola['professor']).get(URL).json()

    assert dados['perfil'] == 'professor'
    assert dados['bimestre']['numero'] == 1
    assert dados['disciplinas'] == [{
        'id': escola['disciplina'].id, 'disciplina': 'Matemática', 'turma': '3º A', 'alunos': 2,
        'media_bimestre': 6.5, 'abaixo_media': 1, 'abaixo_frequencia': 1,
    }]
    assert dados['pendencias'] == []


def test_professor_nao_ve_disciplina_de_outro_professor(escola, criar_usuario, cliente_autenticado):
    colega = criar_usuario('professor', email='colega@exemplo.com')

    dados = cliente_autenticado(colega).get(URL).json()

    assert dados['disciplinas'] == []
    assert dados['sem_dados'] is True


def test_disciplina_com_aluno_sem_nota_publicada_fica_pendente(escola, cliente_autenticado):
    Nota.objects.filter(matricula=escola['matricula_ana']).update(publicada=False)

    dados = cliente_autenticado(escola['professor']).get(URL).json()

    assert dados['pendencias'][0]['disciplina'] == 'Matemática'
    assert dados['pendencias'][0]['sem_nota_publicada'] == 1


def test_bimestre_sem_registros_devolve_sem_dados(escola, cliente_autenticado):
    dados = cliente_autenticado(escola['professor']).get(URL, {'bimestre': 2}).json()

    assert dados['bimestre']['numero'] == 2
    assert dados['sem_dados'] is True


def test_bimestre_invalido_e_recusado(escola, cliente_autenticado):
    response = cliente_autenticado(escola['professor']).get(URL, {'bimestre': 7})

    assert response.status_code == 400


def test_professor_ve_lista_nominal_em_ordem_alfabetica(escola, criar_usuario, cliente_autenticado):
    alvaro = criar_usuario('aluno', email='alvaro@exemplo.com', first_name='Álvaro', last_name='Reis')
    matricula = Matricula.objects.create(aluno=alvaro, turma=escola['turma'], data_inicio=timezone.localdate())
    Nota.objects.create(matricula=matricula, disciplina=escola['disciplina'], bimestre=escola['primeiro'],
                        valor=Decimal('4.0'), publicada=True)

    response = cliente_autenticado(escola['professor']).get(url_lista(escola), {'situacao': 'abaixo_media'})

    assert [a['nome'] for a in response.json()] == ['Álvaro Reis', 'Ana Souza']


def test_outro_professor_nao_ve_lista_nominal(escola, criar_usuario, cliente_autenticado):
    colega = criar_usuario('professor', email='colega@exemplo.com')

    response = cliente_autenticado(colega).get(url_lista(escola), {'situacao': 'abaixo_media'})

    assert response.status_code == 404


@pytest.mark.parametrize('papel', ['secretaria', 'direcao', 'aluno'])
def test_lista_nominal_e_exclusiva_do_professor(papel, escola, criar_usuario, cliente_autenticado):
    usuario = criar_usuario(papel, email=f'{papel}2@exemplo.com')

    response = cliente_autenticado(usuario).get(url_lista(escola), {'situacao': 'abaixo_media'})

    assert response.status_code == 403


def test_lista_nominal_exige_situacao_valida(escola, cliente_autenticado):
    response = cliente_autenticado(escola['professor']).get(url_lista(escola), {'situacao': 'ranking'})

    assert response.status_code == 400


def test_gestor_ve_indicadores_por_turma(escola, criar_usuario, cliente_autenticado):
    secretaria = criar_usuario('secretaria')
    criar_usuario('aluno', email='novo@exemplo.com', aceitou_termos=False)

    dados = cliente_autenticado(secretaria).get(URL).json()

    assert dados['perfil'] == 'gestor'
    assert dados['resumo'] == {'alunos': 2, 'media_geral': 6.5, 'percentual_abaixo_media': 50.0,
                               'percentual_abaixo_frequencia': 50.0}
    assert dados['turmas'] == [{
        'id': escola['turma'].id, 'turma': '3º A', 'alunos': 2, 'media_geral': 6.5,
        'percentual_abaixo_media': 50.0, 'percentual_abaixo_frequencia': 50.0,
    }]
    assert dados['contas_sem_aceite'] == 1
    assert dados['evolucao'] == [{'bimestre': 1, 'media': 6.5}, {'bimestre': 2, 'media': None},
                                 {'bimestre': 3, 'media': None}, {'bimestre': 4, 'media': None}]


def test_gestor_conta_o_aluno_uma_vez_mesmo_com_varias_disciplinas_abaixo(escola, criar_usuario,
                                                                           cliente_autenticado):
    historia = Disciplina.objects.create(turma=escola['turma'], nome='História', carga_horaria=80,
                                         professor=escola['professor'])
    Nota.objects.create(matricula=escola['matricula_ana'], disciplina=historia, bimestre=escola['primeiro'],
                        valor=Decimal('4.0'), publicada=True)

    dados = cliente_autenticado(criar_usuario('direcao')).get(URL).json()

    assert dados['resumo']['percentual_abaixo_media'] == 50.0


def test_gestor_nao_recebe_nomes_de_alunos(escola, criar_usuario, cliente_autenticado):
    dados = cliente_autenticado(criar_usuario('direcao')).get(URL).json()

    assert 'Ana' not in str(dados)
    assert 'Bruno' not in str(dados)


def test_escola_sem_ano_letivo_nao_quebra_o_painel(criar_usuario, cliente_autenticado):
    response = cliente_autenticado(criar_usuario('direcao')).get(URL)

    assert response.status_code == 200
    assert response.json()['sem_dados'] is True


def test_painel_exige_o_aceite_do_termo_vigente(criar_usuario, cliente_autenticado):
    response = cliente_autenticado(criar_usuario('aluno', aceitou_termos=False)).get(URL)

    assert response.status_code == 403
