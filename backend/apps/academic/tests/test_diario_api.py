"""Testes de integração do diário de classe: notas (RF15), chamada (RF16) e boletim (RF17).

Os bimestres são montados a partir da data de hoje, para que o teste não dependa do
dia em que é executado. O envio de e-mails é substituído por um mock.
"""
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.academic.models import AnoLetivo, Bimestre, Chamada, Disciplina, Falta, Matricula, Nota, Turma, VinculoResponsavel
from apps.audit.models import AuditLog

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]

HOJE = timezone.localdate()


@pytest.fixture
def email():
    with patch('apps.academic.servicos.enviar_email_em_lote') as mock:
        yield mock


@pytest.fixture
def escola(criar_usuario):
    """Ano letivo com o 4º bimestre em andamento, uma turma, duas disciplinas e dois alunos."""
    ano = AnoLetivo.objects.create(ano=HOJE.year, ativo=True)
    inicio = HOJE - timedelta(days=200)
    for numero in range(1, 4):
        Bimestre.objects.create(ano_letivo=ano, numero=numero, inicio=inicio + timedelta(days=(numero - 1) * 60),
                                fim=inicio + timedelta(days=(numero - 1) * 60 + 50))
    Bimestre.objects.create(ano_letivo=ano, numero=4, inicio=HOJE - timedelta(days=10), fim=HOJE + timedelta(days=30))
    turma = Turma.objects.create(ano_letivo=ano, nome='3º A', serie='3ª série', turno='manha')
    carla = criar_usuario('professor', email='carla@exemplo.com', first_name='Carla', last_name='Mendes')
    bruno = criar_usuario('professor', email='bruno@exemplo.com', first_name='Bruno', last_name='Lima')
    ana = criar_usuario('aluno', email='ana@exemplo.com', first_name='Ana', last_name='Souza')
    leo = criar_usuario('aluno', email='leo@exemplo.com', first_name='Leo', last_name='Costa')
    rita = criar_usuario('responsavel', email='rita@exemplo.com')
    VinculoResponsavel.objects.create(responsavel=rita, aluno=ana)
    return {
        'turma': turma, 'carla': carla, 'bruno': bruno, 'ana': ana, 'leo': leo, 'rita': rita,
        'mat': Disciplina.objects.create(turma=turma, nome='Matemática', carga_horaria=160, professor=carla),
        'hist': Disciplina.objects.create(turma=turma, nome='História', carga_horaria=80, professor=bruno),
        'm_ana': Matricula.objects.create(aluno=ana, turma=turma, data_inicio=inicio),
        'm_leo': Matricula.objects.create(aluno=leo, turma=turma, data_inicio=inicio),
    }


def url(disciplina, rota):
    return f'/api/v1/diario/{disciplina.id}/{rota}/'


def test_deve_listar_os_alunos_da_turma_no_bimestre_em_andamento(escola, cliente_autenticado):
    response = cliente_autenticado(escola['carla']).get(url(escola['mat'], 'notas'))

    assert response.status_code == 200
    corpo = response.json()
    assert corpo['bimestre']['numero'] == 4
    assert [a['nome'] for a in corpo['alunos']] == ['Ana Souza', 'Leo Costa']
    assert corpo['sem_nota'] == 2


def test_deve_salvar_notas_como_rascunho_invisivel_para_o_aluno(escola, cliente_autenticado):
    dados = {'bimestre': 4, 'notas': [{'matricula': escola['m_ana'].id, 'valor': '8.5'}]}

    salvar = cliente_autenticado(escola['carla']).post(url(escola['mat'], 'notas'), dados, format='json')
    boletim = cliente_autenticado(escola['ana']).get(f'/api/v1/boletim/{escola["ana"].id}/')

    assert salvar.status_code == 200
    assert Nota.objects.get(matricula=escola['m_ana']).publicada is False
    matematica = next(d for d in boletim.json()['disciplinas'] if d['disciplina'] == 'Matemática')
    assert matematica['notas']['4'] is None
    assert AuditLog.objects.filter(acao='notas_lancadas').exists()


def test_deve_recusar_nota_fora_da_faixa_com_mensagem(escola, cliente_autenticado):
    response = cliente_autenticado(escola['carla']).post(
        url(escola['mat'], 'notas'), {'bimestre': 4, 'notas': [{'matricula': escola['m_ana'].id, 'valor': '11'}]},
        format='json')

    assert response.status_code == 400
    assert response.json() == {'notas': ['A nota deve estar entre 0 e 10, com até uma casa decimal.']}
    assert not Nota.objects.exists()


def test_professor_nao_acessa_disciplina_de_outro_professor(escola, cliente_autenticado):
    response = cliente_autenticado(escola['carla']).get(url(escola['hist'], 'notas'))

    assert response.status_code == 404


def test_secretaria_consulta_mas_nao_lanca_notas(escola, criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('secretaria'))

    consulta = client.get(url(escola['mat'], 'notas'))
    lancamento = client.post(url(escola['mat'], 'notas'),
                             {'bimestre': 4, 'notas': [{'matricula': escola['m_ana'].id, 'valor': '7'}]}, format='json')

    assert consulta.status_code == 200
    assert lancamento.status_code == 403


def test_deve_pedir_confirmacao_para_publicar_com_alunos_sem_nota(escola, cliente_autenticado, email):
    client = cliente_autenticado(escola['carla'])
    client.post(url(escola['mat'], 'notas'), {'bimestre': 4, 'notas': [{'matricula': escola['m_ana'].id, 'valor': '9'}]},
                format='json')

    sem_confirmar = client.post(url(escola['mat'], 'publicar-notas'), {'bimestre': 4}, format='json')

    assert sem_confirmar.status_code == 409
    assert sem_confirmar.json()['detail'].startswith('1 aluno(s) ainda estão sem nota.')
    email.assert_not_called()


def test_deve_publicar_e_avisar_aluno_e_responsavel_sem_mostrar_a_nota(escola, cliente_autenticado, email):
    client = cliente_autenticado(escola['carla'])
    client.post(url(escola['mat'], 'notas'), {'bimestre': 4, 'notas': [
        {'matricula': escola['m_ana'].id, 'valor': '9.5'}, {'matricula': escola['m_leo'].id, 'valor': '4.0'}]},
        format='json')

    response = client.post(url(escola['mat'], 'publicar-notas'), {'bimestre': 4}, format='json')

    assert response.status_code == 200
    assert response.json()['email_enviado'] is True
    assert Nota.objects.filter(publicada=True).count() == 2
    destinatarios, assunto, html = email.call_args.args
    assert set(destinatarios) == {'ana@exemplo.com', 'leo@exemplo.com', 'rita@exemplo.com'}
    assert '9.5' not in html and '9,5' not in html and '4.0' not in html
    assert AuditLog.objects.filter(acao='notas_publicadas').exists()


def test_deve_registrar_valor_anterior_ao_corrigir_nota_publicada(escola, cliente_autenticado, email):
    nota = Nota.objects.create(matricula=escola['m_ana'], disciplina=escola['mat'],
                               bimestre=Bimestre.objects.get(numero=4), valor=Decimal('5.0'), publicada=True)
    client = cliente_autenticado(escola['carla'])

    response = client.post(url(escola['mat'], 'notas'),
                           {'bimestre': 4, 'notas': [{'matricula': escola['m_ana'].id, 'valor': '6.5'}]}, format='json')

    assert response.status_code == 200
    nota.refresh_from_db()
    assert nota.valor == Decimal('6.5') and nota.publicada is True
    assert AuditLog.objects.get(acao='nota_alterada').detalhes.endswith('5.0 -> 6.5')
    email.assert_called_once()


def test_falha_no_email_nao_desfaz_a_publicacao(escola, cliente_autenticado, email):
    email.side_effect = RuntimeError('Brevo respondeu 503')
    Nota.objects.create(matricula=escola['m_ana'], disciplina=escola['mat'],
                        bimestre=Bimestre.objects.get(numero=4), valor=Decimal('7.0'))
    Nota.objects.create(matricula=escola['m_leo'], disciplina=escola['mat'],
                        bimestre=Bimestre.objects.get(numero=4), valor=Decimal('8.0'))

    response = cliente_autenticado(escola['carla']).post(url(escola['mat'], 'publicar-notas'), {'bimestre': 4},
                                                         format='json')

    assert response.status_code == 200
    assert response.json()['email_enviado'] is False
    assert Nota.objects.filter(publicada=True).count() == 2
    assert AuditLog.objects.filter(acao='notificacao_falha_envio').exists()


def test_chamada_nova_vem_com_todos_presentes(escola, cliente_autenticado):
    response = cliente_autenticado(escola['carla']).get(url(escola['mat'], 'chamada'))

    corpo = response.json()
    assert corpo['existente'] is False
    assert all(a['presente'] for a in corpo['alunos'])


def test_deve_registrar_falta_em_todas_as_aulas_e_avisar_so_o_responsavel_do_ausente(escola, cliente_autenticado,
                                                                                      email):
    response = cliente_autenticado(escola['carla']).post(url(escola['mat'], 'chamada'), {
        'data': HOJE.isoformat(), 'quantidade_aulas': 2, 'ausentes': [escola['m_ana'].id]}, format='json')

    assert response.status_code == 200
    assert Falta.objects.get(matricula=escola['m_ana']).quantidade == 2
    destinatarios, _, html = email.call_args.args
    assert destinatarios == ['rita@exemplo.com']
    assert 'Matemática' not in html
    assert AuditLog.objects.filter(acao='chamada_registrada').exists()


def test_deve_corrigir_a_chamada_do_mesmo_dia_sem_duplicar(escola, cliente_autenticado, email):
    client = cliente_autenticado(escola['carla'])
    dados = {'data': HOJE.isoformat(), 'quantidade_aulas': 2, 'ausentes': [escola['m_ana'].id]}
    client.post(url(escola['mat'], 'chamada'), dados, format='json')

    response = client.post(url(escola['mat'], 'chamada'), {**dados, 'ausentes': [escola['m_leo'].id]}, format='json')

    assert response.status_code == 200
    assert Chamada.objects.count() == 1
    assert list(Falta.objects.values_list('matricula_id', flat=True)) == [escola['m_leo'].id]
    assert AuditLog.objects.filter(acao='chamada_alterada').exists()


def test_deve_recusar_chamada_em_data_futura(escola, cliente_autenticado):
    response = cliente_autenticado(escola['carla']).post(url(escola['mat'], 'chamada'), {
        'data': (HOJE + timedelta(days=1)).isoformat(), 'quantidade_aulas': 1}, format='json')

    assert response.status_code == 400
    assert response.json() == {'data': ['Escolha uma data entre o início do ano letivo e hoje.']}


def test_professor_nao_registra_chamada_de_bimestre_encerrado(escola, cliente_autenticado):
    data_antiga = Bimestre.objects.get(numero=1).inicio

    response = cliente_autenticado(escola['carla']).post(url(escola['mat'], 'chamada'), {
        'data': data_antiga.isoformat(), 'quantidade_aulas': 1}, format='json')

    assert response.status_code == 400
    assert response.json() == {'data': ['O 1º bimestre está encerrado. Solicite a correção à secretaria.']}


def test_secretaria_pode_corrigir_chamada_de_bimestre_encerrado(escola, criar_usuario, cliente_autenticado):
    data_antiga = Bimestre.objects.get(numero=1).inicio

    response = cliente_autenticado(criar_usuario('secretaria')).post(url(escola['mat'], 'chamada'), {
        'data': data_antiga.isoformat(), 'quantidade_aulas': 1}, format='json')

    assert response.status_code == 200


def test_boletim_calcula_media_parcial_e_frequencia_com_destaques(escola, cliente_autenticado):
    for numero, valor in [(1, '5.0'), (2, '6.0')]:
        Nota.objects.create(matricula=escola['m_ana'], disciplina=escola['mat'],
                            bimestre=Bimestre.objects.get(numero=numero), valor=Decimal(valor), publicada=True)
    bimestre = Bimestre.objects.get(numero=4)
    chamada = Chamada.objects.create(disciplina=escola['mat'], bimestre=bimestre, data=HOJE, quantidade_aulas=4)
    Falta.objects.create(chamada=chamada, matricula=escola['m_ana'], quantidade=2)

    response = cliente_autenticado(escola['rita']).get(f'/api/v1/boletim/{escola["ana"].id}/')

    assert response.status_code == 200
    mat = next(d for d in response.json()['disciplinas'] if d['disciplina'] == 'Matemática')
    assert mat['media'] == 5.5 and mat['media_parcial'] is True and mat['abaixo_media'] is True
    assert (mat['aulas'], mat['faltas'], mat['frequencia']) == (4, 2, 50.0)
    assert mat['abaixo_frequencia'] is True


def test_responsavel_nao_ve_boletim_de_aluno_nao_vinculado(escola, cliente_autenticado):
    response = cliente_autenticado(escola['rita']).get(f'/api/v1/boletim/{escola["leo"].id}/')

    assert response.status_code == 403


def test_aluno_so_ve_o_proprio_boletim(escola, cliente_autenticado):
    client = cliente_autenticado(escola['ana'])

    proprio = client.get(f'/api/v1/boletim/{escola["ana"].id}/')
    outro = client.get(f'/api/v1/boletim/{escola["leo"].id}/')
    lista = client.get('/api/v1/boletim/alunos/')

    assert proprio.status_code == 200
    assert outro.status_code == 403
    assert lista.json() == [{'id': escola['ana'].id, 'nome': 'Ana Souza'}]
