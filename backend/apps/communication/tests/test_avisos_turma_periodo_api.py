"""Testes de integração dos avisos por turma, com período de exibição e aviso por e-mail
(RF08 a RF10, RN33 a RN35 e RN40). O envio de e-mails é substituído por um mock."""
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.academic.models import AnoLetivo, Disciplina, Matricula, Turma, VinculoResponsavel
from apps.audit.models import AuditLog
from apps.communication.models import Aviso

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]

HOJE = timezone.localdate()
URL = '/api/v1/avisos/'


@pytest.fixture
def email():
    with patch('apps.academic.servicos.enviar_email_em_lote') as mock:
        yield mock


@pytest.fixture
def escola(criar_usuario):
    ano = AnoLetivo.objects.create(ano=HOJE.year, ativo=True)
    t3a = Turma.objects.create(ano_letivo=ano, nome='3º A', serie='3ª série', turno='manha')
    t3b = Turma.objects.create(ano_letivo=ano, nome='3º B', serie='3ª série', turno='tarde')
    carla = criar_usuario('professor', email='carla@exemplo.com')
    Disciplina.objects.create(turma=t3a, nome='Matemática', carga_horaria=160, professor=carla)
    ana = criar_usuario('aluno', email='ana@exemplo.com')
    leo = criar_usuario('aluno', email='leo@exemplo.com')
    Matricula.objects.create(aluno=ana, turma=t3a)
    Matricula.objects.create(aluno=leo, turma=t3b)
    rita = criar_usuario('responsavel', email='rita@exemplo.com')
    VinculoResponsavel.objects.create(responsavel=rita, aluno=ana)
    return {'t3a': t3a, 't3b': t3b, 'carla': carla, 'ana': ana, 'leo': leo, 'rita': rita}


def titulos(client):
    return sorted(a['titulo'] for a in client.get(URL).json()['results'])


def test_aviso_da_turma_aparece_so_para_a_turma_e_seus_responsaveis(escola, cliente_autenticado):
    Aviso.objects.create(titulo='Geral', conteudo='.')
    Aviso.objects.create(titulo='Prova do 3º A', conteudo='.', turma=escola['t3a'])

    assert titulos(cliente_autenticado(escola['ana'])) == ['Geral', 'Prova do 3º A']
    assert titulos(cliente_autenticado(escola['rita'])) == ['Geral', 'Prova do 3º A']
    assert titulos(cliente_autenticado(escola['leo'])) == ['Geral']


def test_aviso_fora_do_periodo_some_para_o_aluno_mas_nao_para_o_autor(escola, criar_usuario, cliente_autenticado):
    Aviso.objects.create(titulo='Agendado', conteudo='.', autor=escola['carla'],
                         inicio_exibicao=HOJE + timedelta(days=3))
    Aviso.objects.create(titulo='Encerrado', conteudo='.', fim_exibicao=HOJE - timedelta(days=1))

    assert titulos(cliente_autenticado(escola['ana'])) == []
    assert titulos(cliente_autenticado(escola['carla'])) == ['Agendado']
    situacoes = {a['titulo']: a['situacao'] for a in
                 cliente_autenticado(criar_usuario('secretaria')).get(URL).json()['results']}
    assert situacoes == {'Agendado': 'agendado', 'Encerrado': 'encerrado'}


def test_deve_recusar_data_de_fim_anterior_ao_inicio(escola, cliente_autenticado):
    response = cliente_autenticado(escola['carla']).post(URL, {
        'titulo': 'Feira', 'conteudo': '.', 'inicio_exibicao': HOJE.isoformat(),
        'fim_exibicao': (HOJE - timedelta(days=1)).isoformat()}, format='json')

    assert response.status_code == 400
    assert response.json() == {'fim_exibicao': ['A data de fim deve ser igual ou posterior à data de início.']}


def test_professor_so_publica_para_turma_em_que_leciona(escola, cliente_autenticado):
    client = cliente_autenticado(escola['carla'])

    propria = client.post(URL, {'titulo': 'A', 'conteudo': '.', 'turma': escola['t3a'].id}, format='json')
    alheia = client.post(URL, {'titulo': 'B', 'conteudo': '.', 'turma': escola['t3b'].id}, format='json')

    assert propria.status_code == 201
    assert propria.json()['turma_nome'] == '3º A'
    assert alheia.status_code == 400
    assert alheia.json() == {'turma': ['Você só pode publicar avisos para turmas em que leciona.']}


def test_deve_avisar_por_email_a_turma_com_titulo_e_sem_o_conteudo(escola, cliente_autenticado, email):
    response = cliente_autenticado(escola['carla']).post(URL, {
        'titulo': 'Prova sexta', 'conteudo': 'Conteúdo reservado', 'turma': escola['t3a'].id,
        'notificar_email': True}, format='json')

    assert response.status_code == 201
    destinatarios, assunto, html = email.call_args.args
    assert set(destinatarios) == {'ana@exemplo.com', 'rita@exemplo.com'}
    assert 'Prova sexta' in assunto
    assert 'Conteúdo reservado' not in html
    assert AuditLog.objects.filter(acao='aviso_notificado').exists()


def test_aviso_agendado_so_e_enviado_pelo_comando_diario(escola, criar_usuario, cliente_autenticado, email):
    cliente_autenticado(criar_usuario('secretaria')).post(URL, {
        'titulo': 'Reunião', 'conteudo': '.', 'notificar_email': True,
        'inicio_exibicao': (HOJE + timedelta(days=2)).isoformat()}, format='json')
    email.assert_not_called()
    Aviso.objects.update(inicio_exibicao=HOJE)

    saida = StringIO()
    call_command('enviar_avisos_agendados', stdout=saida)

    email.assert_called_once()
    assert '1 aviso(s) notificado(s)' in saida.getvalue()
    assert Aviso.objects.get().notificado_em is not None


def test_falha_no_email_do_aviso_nao_impede_a_publicacao(escola, cliente_autenticado, email):
    email.side_effect = RuntimeError('Brevo respondeu 503')

    response = cliente_autenticado(escola['carla']).post(URL, {
        'titulo': 'Prova', 'conteudo': '.', 'notificar_email': True}, format='json')

    assert response.status_code == 201
    assert Aviso.objects.filter(titulo='Prova').exists()
    assert AuditLog.objects.filter(acao='aviso_falha_envio').exists()


def test_professor_edita_o_proprio_aviso(escola, cliente_autenticado):
    aviso = Aviso.objects.create(titulo='Antigo', conteudo='.', autor=escola['carla'])

    response = cliente_autenticado(escola['carla']).patch(f'{URL}{aviso.id}/', {
        'titulo': 'Novo', 'fim_exibicao': (HOJE + timedelta(days=5)).isoformat()}, format='json')

    assert response.status_code == 200
    aviso.refresh_from_db()
    assert aviso.titulo == 'Novo'
    assert AuditLog.objects.filter(acao='aviso_editado').exists()
