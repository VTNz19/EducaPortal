"""Testes de integração da API de ano letivo, turmas e disciplinas (RF13)."""
import pytest

from apps.academic.models import AnoLetivo, Disciplina, Matricula, Turma
from apps.audit.models import AuditLog

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]

BIMESTRES = [
    {'numero': 1, 'inicio': '2026-02-02', 'fim': '2026-04-17'},
    {'numero': 2, 'inicio': '2026-04-20', 'fim': '2026-07-03'},
    {'numero': 3, 'inicio': '2026-07-27', 'fim': '2026-09-30'},
    {'numero': 4, 'inicio': '2026-10-01', 'fim': '2026-12-11'},
]


@pytest.fixture
def ano_2026(db):
    return AnoLetivo.objects.create(ano=2026, ativo=True)


@pytest.fixture
def turma_3a(ano_2026):
    return Turma.objects.create(ano_letivo=ano_2026, nome='3º A', serie='3ª série', turno='manha')


def test_deve_criar_ano_letivo_com_os_quatro_bimestres_e_registrar_no_log(criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('secretaria'))

    response = client.post('/api/v1/anos-letivos/', {'ano': 2027, 'ativo': True, 'bimestres': BIMESTRES}, format='json')

    assert response.status_code == 201
    assert [b['numero'] for b in response.json()['bimestres']] == [1, 2, 3, 4]
    assert AnoLetivo.objects.get(ano=2027).bimestres.count() == 4
    assert AuditLog.objects.filter(acao='ano_letivo_criado').exists()


def test_deve_manter_apenas_um_ano_letivo_ativo(ano_2026, criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('secretaria'))

    client.post('/api/v1/anos-letivos/', {'ano': 2027, 'ativo': True, 'bimestres': BIMESTRES}, format='json')

    ano_2026.refresh_from_db()
    assert ano_2026.ativo is False
    assert AnoLetivo.atual().ano == 2027


def test_deve_recusar_ano_letivo_com_bimestres_sobrepostos(criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('direcao'))
    bimestres = [dict(b) for b in BIMESTRES]
    bimestres[1]['inicio'] = '2026-04-10'

    response = client.post('/api/v1/anos-letivos/', {'ano': 2027, 'bimestres': bimestres}, format='json')

    assert response.status_code == 400
    assert response.json() == {'bimestres': ['O 2º bimestre deve começar depois do fim do 1º bimestre.']}
    assert not AnoLetivo.objects.filter(ano=2027).exists()


def test_deve_recusar_turma_com_nome_repetido_no_mesmo_ano(turma_3a, criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('secretaria'))

    response = client.post('/api/v1/turmas/', {'ano_letivo': turma_3a.ano_letivo_id, 'nome': '3º a',
                                               'serie': '3ª série', 'turno': 'tarde'}, format='json')

    assert response.status_code == 400
    assert response.json() == {'nome': ['Já existe a turma 3º a em 2026.']}


def test_professor_pode_consultar_turmas_mas_nao_criar(turma_3a, criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('professor'))

    lista = client.get('/api/v1/turmas/')
    criacao = client.post('/api/v1/turmas/', {'ano_letivo': turma_3a.ano_letivo_id, 'nome': '3º B',
                                              'serie': '3ª série', 'turno': 'manha'}, format='json')

    assert lista.status_code == 200
    assert [t['nome'] for t in lista.json()] == ['3º A']
    assert criacao.status_code == 403


def test_aluno_nao_pode_consultar_a_estrutura_academica(turma_3a, criar_usuario, cliente_autenticado):
    response = cliente_autenticado(criar_usuario('aluno')).get('/api/v1/turmas/')

    assert response.status_code == 403


def test_deve_criar_disciplina_e_recusar_conta_que_nao_e_de_professor(turma_3a, criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('secretaria'))
    professor = criar_usuario('professor')
    aluno = criar_usuario('aluno')
    dados = {'turma': turma_3a.id, 'nome': 'Matemática', 'carga_horaria': 160}

    valida = client.post('/api/v1/disciplinas/', {**dados, 'professor': professor.id}, format='json')
    invalida = client.post('/api/v1/disciplinas/', {**dados, 'nome': 'Física', 'professor': aluno.id}, format='json')

    assert valida.status_code == 201
    assert valida.json()['professor_nome'] == professor.username
    assert invalida.status_code == 400
    assert invalida.json() == {'professor': ['Selecione uma conta de professor ativa.']}


def test_professor_so_ve_as_disciplinas_atribuidas_a_ele(turma_3a, criar_usuario, cliente_autenticado):
    carla = criar_usuario('professor', email='carla@exemplo.com')
    bruno = criar_usuario('professor', email='bruno@exemplo.com')
    Disciplina.objects.create(turma=turma_3a, nome='Matemática', carga_horaria=160, professor=carla)
    Disciplina.objects.create(turma=turma_3a, nome='História', carga_horaria=80, professor=bruno)

    response = cliente_autenticado(carla).get('/api/v1/disciplinas/')

    assert [d['nome'] for d in response.json()] == ['Matemática']


def test_troca_de_professor_gera_registro_proprio_no_log(turma_3a, criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('secretaria'))
    carla = criar_usuario('professor', email='carla@exemplo.com')
    bruno = criar_usuario('professor', email='bruno@exemplo.com')
    disciplina = Disciplina.objects.create(turma=turma_3a, nome='Matemática', carga_horaria=160, professor=carla)

    response = client.patch(f'/api/v1/disciplinas/{disciplina.id}/', {'professor': bruno.id}, format='json')

    assert response.status_code == 200
    assert AuditLog.objects.filter(acao='professor_alterado').count() == 1


def test_nao_deve_excluir_turma_com_alunos_matriculados(turma_3a, criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('secretaria'))
    Matricula.objects.create(aluno=criar_usuario('aluno'), turma=turma_3a)

    response = client.delete(f'/api/v1/turmas/{turma_3a.id}/')

    assert response.status_code == 400
    assert response.json() == {'detail': 'Esta turma já tem disciplinas, matrículas ou avisos e não pode ser excluída.'}
    assert Turma.objects.filter(id=turma_3a.id).exists()


def test_lista_de_turmas_informa_o_total_de_alunos_ativos(turma_3a, criar_usuario, cliente_autenticado):
    Matricula.objects.create(aluno=criar_usuario('aluno', email='a1@exemplo.com'), turma=turma_3a)
    Matricula.objects.create(aluno=criar_usuario('aluno', email='a2@exemplo.com'), turma=turma_3a)

    response = cliente_autenticado(criar_usuario('secretaria')).get('/api/v1/turmas/')

    assert response.json()[0]['total_alunos'] == 2
