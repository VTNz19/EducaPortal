"""Testes de integração do cadastro com matrícula e vínculo (RF03), das alterações
de matrícula e vínculos (RF14) e dos filtros da lista de contas (RF06).

O envio do convite por e-mail é substituído por um mock: nenhum e-mail real é enviado.
"""
from unittest.mock import patch

import pytest

from apps.academic.models import AnoLetivo, Matricula, Turma, VinculoResponsavel
from apps.accounts.models import User
from apps.audit.models import AuditLog

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]


@pytest.fixture(autouse=True)
def sem_email():
    with patch('apps.accounts.views.enviar_link_definir_senha') as mock:
        yield mock


@pytest.fixture
def ano_2026(db):
    return AnoLetivo.objects.create(ano=2026, ativo=True)


@pytest.fixture
def turma_3a(ano_2026):
    return Turma.objects.create(ano_letivo=ano_2026, nome='3º A', serie='3ª série', turno='manha')


@pytest.fixture
def turma_3b(ano_2026):
    return Turma.objects.create(ano_letivo=ano_2026, nome='3º B', serie='3ª série', turno='tarde')


@pytest.fixture
def secretaria(criar_usuario, cliente_autenticado):
    return cliente_autenticado(criar_usuario('secretaria'))


def novo_aluno(criar_usuario, turma, email='ana@exemplo.com'):
    aluno = criar_usuario('aluno', email=email)
    Matricula.objects.create(aluno=aluno, turma=turma)
    return aluno


def test_deve_cadastrar_aluno_ja_matriculado_na_turma(turma_3a, criar_usuario, secretaria):
    rita = criar_usuario('responsavel', email='rita@exemplo.com')

    response = secretaria.post('/api/v1/usuarios/', {'first_name': 'Ana', 'last_name': 'Souza',
                                                     'email': 'ana@exemplo.com', 'role': 'aluno',
                                                     'turma': turma_3a.id, 'responsaveis': [rita.id]}, format='json')

    assert response.status_code == 201
    assert response.json()['turma'] == '3º A'
    aluno = User.objects.get(email='ana@exemplo.com')
    assert aluno.matriculas.get().turma == turma_3a
    assert AuditLog.objects.filter(acao='matricula_criada').count() == 1


def test_deve_recusar_aluno_sem_turma_e_nao_criar_a_conta(turma_3a, secretaria):
    response = secretaria.post('/api/v1/usuarios/', {'first_name': 'Ana', 'last_name': 'Souza',
                                                     'email': 'ana@exemplo.com', 'role': 'aluno'}, format='json')

    assert response.status_code == 400
    assert response.json() == {'turma': ['Selecione a turma do aluno.']}
    assert not User.objects.filter(email='ana@exemplo.com').exists()


def test_deve_pedir_o_cadastro_de_turma_quando_o_ano_nao_tem_turmas(ano_2026, secretaria):
    response = secretaria.post('/api/v1/usuarios/', {'first_name': 'Ana', 'last_name': 'Souza',
                                                     'email': 'ana@exemplo.com', 'role': 'aluno'}, format='json')

    assert response.json() == {'turma': ['Cadastre uma turma antes de cadastrar alunos.']}


def cadastrar_aluno(cliente, turma, **extras):
    return cliente.post('/api/v1/usuarios/', {'first_name': 'Ana', 'last_name': 'Souza', 'email': 'ana@exemplo.com',
                                              'role': 'aluno', 'turma': turma.id, **extras}, format='json')


def test_deve_cadastrar_aluno_ja_vinculado_aos_responsaveis(turma_3a, criar_usuario, secretaria):
    rita = criar_usuario('responsavel', email='rita@exemplo.com')
    joao = criar_usuario('responsavel', email='joao@exemplo.com')

    response = cadastrar_aluno(secretaria, turma_3a, responsaveis=[rita.id, joao.id])

    assert response.status_code == 201
    ana = User.objects.get(email='ana@exemplo.com')
    assert set(ana.vinculos_como_aluno.values_list('responsavel_id', flat=True)) == {rita.id, joao.id}
    assert AuditLog.objects.filter(acao='vinculo_criado').count() == 2


def test_deve_recusar_aluno_sem_responsavel_selecionado(turma_3a, criar_usuario, secretaria):
    criar_usuario('responsavel', email='rita@exemplo.com')

    response = cadastrar_aluno(secretaria, turma_3a, responsaveis=[])

    assert response.status_code == 400
    assert response.json() == {'responsaveis': ['Selecione ao menos um responsável.']}
    assert not User.objects.filter(email='ana@exemplo.com').exists()


def test_deve_pedir_o_cadastro_do_responsavel_quando_nao_ha_nenhum(turma_3a, secretaria):
    response = cadastrar_aluno(secretaria, turma_3a)

    assert response.status_code == 400
    assert response.json() == {'responsaveis': ['Cadastre um responsável antes de cadastrar alunos.']}


def test_responsavel_inativo_nao_conta_para_o_cadastro_do_aluno(turma_3a, criar_usuario, secretaria):
    rita = criar_usuario('responsavel', email='rita@exemplo.com', is_active=False)

    response = cadastrar_aluno(secretaria, turma_3a, responsaveis=[rita.id])

    assert response.status_code == 400
    assert response.json() == {'responsaveis': ['Responsável não encontrado.']}


def test_deve_cadastrar_responsavel_sem_aluno(secretaria):
    response = secretaria.post('/api/v1/usuarios/', {'first_name': 'Rita', 'last_name': 'Souza',
                                                     'email': 'rita@exemplo.com', 'role': 'responsavel'}, format='json')

    assert response.status_code == 201
    assert not User.objects.get(email='rita@exemplo.com').vinculos_como_responsavel.exists()


def test_deve_recusar_vinculo_com_conta_que_nao_e_de_responsavel(turma_3a, criar_usuario, secretaria):
    professor = criar_usuario('professor')

    response = cadastrar_aluno(secretaria, turma_3a, responsaveis=[professor.id])

    assert response.status_code == 400
    assert response.json() == {'responsaveis': ['Responsável não encontrado.']}
    assert not User.objects.filter(email='ana@exemplo.com').exists()


def test_deve_transferir_aluno_mantendo_o_historico(turma_3a, turma_3b, criar_usuario, secretaria):
    ana = novo_aluno(criar_usuario, turma_3a)

    response = secretaria.post(f'/api/v1/alunos/{ana.id}/transferir/', {'turma': turma_3b.id}, format='json')

    assert response.status_code == 200
    situacoes = {m['turma']: m['situacao'] for m in response.json()['matriculas']}
    assert situacoes == {'3º B': 'ativa', '3º A': 'transferida'}
    assert AuditLog.objects.filter(acao='matricula_transferida').exists()


def test_deve_recusar_rematricula_no_ano_em_que_o_aluno_ja_esta_matriculado(turma_3a, turma_3b, criar_usuario,
                                                                            secretaria):
    ana = novo_aluno(criar_usuario, turma_3a)

    response = secretaria.post(f'/api/v1/alunos/{ana.id}/rematricular/', {'turma': turma_3b.id}, format='json')

    assert response.status_code == 400
    assert response.json() == {'detail': 'O aluno já tem matrícula ativa em 2026.'}


def test_deve_rematricular_no_novo_ano_e_encerrar_a_matricula_anterior(turma_3a, criar_usuario, secretaria):
    ana = novo_aluno(criar_usuario, turma_3a)
    ano_2027 = AnoLetivo.objects.create(ano=2027)
    turma_2027 = Turma.objects.create(ano_letivo=ano_2027, nome='3º A', serie='3ª série', turno='manha')

    response = secretaria.post(f'/api/v1/alunos/{ana.id}/rematricular/', {'turma': turma_2027.id}, format='json')

    assert response.status_code == 200
    assert Matricula.objects.get(aluno=ana, ano_letivo__ano=2026).situacao == 'encerrada'
    assert Matricula.objects.get(aluno=ana, ano_letivo__ano=2027).situacao == 'ativa'


def test_deve_vincular_responsavel_e_recusar_vinculo_repetido(turma_3a, criar_usuario, secretaria):
    ana = novo_aluno(criar_usuario, turma_3a)
    rita = criar_usuario('responsavel', email='rita@exemplo.com')

    primeiro = secretaria.post(f'/api/v1/alunos/{ana.id}/vincular/', {'responsavel': rita.id}, format='json')
    repetido = secretaria.post(f'/api/v1/alunos/{ana.id}/vincular/', {'responsavel': rita.id}, format='json')

    assert primeiro.status_code == 200
    assert primeiro.json()['vinculos'][0]['email'] == 'rita@exemplo.com'
    assert repetido.json() == {'detail': 'Este responsável já está vinculado ao aluno.'}


def test_deve_pedir_confirmacao_ao_desvincular_o_ultimo_aluno_do_responsavel(turma_3a, criar_usuario, secretaria):
    ana = novo_aluno(criar_usuario, turma_3a)
    rita = criar_usuario('responsavel', email='rita@exemplo.com')
    joao = criar_usuario('responsavel', email='joao@exemplo.com')
    VinculoResponsavel.objects.create(responsavel=rita, aluno=ana)
    VinculoResponsavel.objects.create(responsavel=joao, aluno=ana)
    url = f'/api/v1/alunos/{ana.id}/desvincular/'

    sem_confirmar = secretaria.post(url, {'responsavel': rita.id}, format='json')
    confirmado = secretaria.post(url, {'responsavel': rita.id, 'confirmar': True}, format='json')

    assert sem_confirmar.status_code == 409
    assert sem_confirmar.json()['requer_confirmacao'] is True
    assert confirmado.status_code == 200
    assert list(VinculoResponsavel.objects.values_list('responsavel_id', flat=True)) == [joao.id]
    assert AuditLog.objects.filter(acao='vinculo_removido').count() == 1


def test_nao_deve_remover_o_ultimo_responsavel_do_aluno(turma_3a, criar_usuario, secretaria):
    ana = novo_aluno(criar_usuario, turma_3a)
    rita = criar_usuario('responsavel', email='rita@exemplo.com')
    VinculoResponsavel.objects.create(responsavel=rita, aluno=ana)

    response = secretaria.post(f'/api/v1/alunos/{ana.id}/desvincular/',
                               {'responsavel': rita.id, 'confirmar': True}, format='json')

    assert response.status_code == 400
    assert response.json() == {'detail': 'O aluno precisa ter ao menos um responsável. '
                                         'Vincule outro antes de remover este.'}
    assert VinculoResponsavel.objects.count() == 1
    assert not AuditLog.objects.filter(acao='vinculo_removido').exists()


def test_deve_trocar_o_responsavel_vinculando_o_novo_antes_de_remover_o_antigo(turma_3a, criar_usuario, secretaria):
    ana = novo_aluno(criar_usuario, turma_3a)
    rita = criar_usuario('responsavel', email='rita@exemplo.com')
    joao = criar_usuario('responsavel', email='joao@exemplo.com')
    VinculoResponsavel.objects.create(responsavel=rita, aluno=ana)

    secretaria.post(f'/api/v1/alunos/{ana.id}/vincular/', {'responsavel': joao.id}, format='json')
    response = secretaria.post(f'/api/v1/alunos/{ana.id}/desvincular/',
                               {'responsavel': rita.id, 'confirmar': True}, format='json')

    assert response.status_code == 200
    assert list(VinculoResponsavel.objects.values_list('responsavel_id', flat=True)) == [joao.id]


def test_professor_nao_pode_alterar_matriculas(turma_3a, turma_3b, criar_usuario, cliente_autenticado):
    ana = novo_aluno(criar_usuario, turma_3a)
    client = cliente_autenticado(criar_usuario('professor'))

    response = client.post(f'/api/v1/alunos/{ana.id}/transferir/', {'turma': turma_3b.id}, format='json')

    assert response.status_code == 403
    assert ana.matriculas.get().turma == turma_3a


def test_deve_filtrar_contas_por_perfil_e_turma(turma_3a, turma_3b, criar_usuario, secretaria):
    novo_aluno(criar_usuario, turma_3a, 'ana@exemplo.com')
    novo_aluno(criar_usuario, turma_3b, 'leo@exemplo.com')
    criar_usuario('professor', email='carla@exemplo.com')

    response = secretaria.get('/api/v1/usuarios/', {'role': 'aluno', 'turma': turma_3a.id})

    resultados = response.json()['results']
    assert [(u['email'], u['turma']) for u in resultados] == [('ana@exemplo.com', '3º A')]


def test_deve_buscar_contas_por_nome_ou_email(criar_usuario, secretaria):
    criar_usuario('professor', email='carla@exemplo.com', first_name='Carla', last_name='Mendes')
    criar_usuario('professor', email='bruno@exemplo.com', first_name='Bruno', last_name='Lima')

    por_nome = secretaria.get('/api/v1/usuarios/', {'busca': 'mendes'}).json()['results']
    por_email = secretaria.get('/api/v1/usuarios/', {'busca': 'bruno@'}).json()['results']

    assert [u['email'] for u in por_nome] == ['carla@exemplo.com']
    assert [u['email'] for u in por_email] == ['bruno@exemplo.com']
