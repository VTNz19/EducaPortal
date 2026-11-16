"""Testes de integração das tarefas com anexos (RF19, RN74 a RN76). O envio de e-mails é um mock."""
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.academic.models import AnoLetivo, Disciplina, Matricula, Turma, VinculoResponsavel
from apps.audit.models import AuditLog
from apps.communication.models import AnexoTarefa, Tarefa

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]

HOJE = timezone.localdate()
URL = '/api/v1/tarefas/'


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
    bruno = criar_usuario('professor', email='bruno@exemplo.com')
    mat_a = Disciplina.objects.create(turma=t3a, nome='Matemática', carga_horaria=160, professor=carla)
    mat_b = Disciplina.objects.create(turma=t3b, nome='Matemática', carga_horaria=160, professor=bruno)
    ana = criar_usuario('aluno', email='ana@exemplo.com')
    leo = criar_usuario('aluno', email='leo@exemplo.com')
    Matricula.objects.create(aluno=ana, turma=t3a)
    Matricula.objects.create(aluno=leo, turma=t3b)
    rita = criar_usuario('responsavel', email='rita@exemplo.com')
    VinculoResponsavel.objects.create(responsavel=rita, aluno=ana)
    return {'carla': carla, 'bruno': bruno, 'mat_a': mat_a, 'mat_b': mat_b, 'ana': ana, 'leo': leo, 'rita': rita}


def pdf(nome='lista.pdf', tamanho=100):
    return SimpleUploadedFile(nome, b'%PDF-1.7' + b'0' * tamanho, content_type='application/pdf')


def dados(disciplina, **extras):
    return {'disciplina': disciplina.id, 'titulo': 'Lista de funções', 'descricao': 'Exercícios 1 a 10.',
            'prazo': (HOJE + timedelta(days=3)).isoformat(), **extras}


def test_professor_publica_tarefa_com_anexo_e_avisa_alunos_e_responsaveis(escola, cliente_autenticado, email):
    response = cliente_autenticado(escola['carla']).post(
        URL, dados(escola['mat_a'], arquivos=[pdf(), pdf('mapa.pdf')]), format='multipart')

    assert response.status_code == 201
    corpo = response.json()
    assert [a['nome'] for a in corpo['anexos']] == ['lista.pdf', 'mapa.pdf']
    assert corpo['turma_nome'] == '3º A'
    assert corpo['email_enviado'] is True
    destinatarios, assunto, html = email.call_args.args
    assert sorted(destinatarios) == ['ana@exemplo.com', 'rita@exemplo.com']
    assert 'Lista de funções' in assunto
    assert 'Exercícios' not in html
    log = AuditLog.objects.get(acao='tarefa_criada')
    assert log.usuario == escola['carla'] and '2 anexo(s)' in log.detalhes


def test_ca01_recusa_anexo_de_15_mb_e_nao_publica(escola, cliente_autenticado, email):
    grande = pdf('apostila.pdf', 15 * 1024 * 1024)

    response = cliente_autenticado(escola['carla']).post(URL, dados(escola['mat_a'], arquivos=[grande]),
                                                         format='multipart')

    assert response.status_code == 400
    assert response.json() == {'arquivos': ['O arquivo "apostila.pdf" foi recusado: o tamanho passa de 10 MB.']}
    assert not Tarefa.objects.exists()
    email.assert_not_called()


def test_recusa_tipo_nao_permitido(escola, cliente_autenticado, email):
    exe = SimpleUploadedFile('jogo.exe', b'MZ\x90\x00', content_type='application/octet-stream')

    response = cliente_autenticado(escola['carla']).post(URL, dados(escola['mat_a'], arquivos=[exe]),
                                                         format='multipart')

    assert response.status_code == 400
    assert 'jogo.exe' in response.json()['arquivos'][0]


def test_recusa_prazo_anterior_a_hoje(escola, cliente_autenticado, email):
    ontem = (HOJE - timedelta(days=1)).isoformat()

    response = cliente_autenticado(escola['carla']).post(URL, dados(escola['mat_a'], prazo=ontem), format='json')

    assert response.status_code == 400
    assert response.json() == {'prazo': ['O prazo de entrega não pode ser anterior a hoje.']}


def test_professor_so_publica_nas_proprias_disciplinas(escola, cliente_autenticado, email):
    response = cliente_autenticado(escola['carla']).post(URL, dados(escola['mat_b']), format='json')

    assert response.status_code == 400
    assert response.json() == {'disciplina': ['Você só pode publicar tarefas nas disciplinas atribuídas a você.']}


@pytest.mark.parametrize('perfil', ['ana', 'rita'])
def test_rn74_aluno_e_responsavel_nao_publicam(escola, cliente_autenticado, email, perfil):
    response = cliente_autenticado(escola[perfil]).post(URL, dados(escola['mat_a']), format='json')

    assert response.status_code == 403


def test_ca02_tarefa_do_3a_nao_aparece_para_aluno_do_3b(escola, cliente_autenticado):
    Tarefa.objects.create(disciplina=escola['mat_a'], titulo='Do 3º A', prazo=HOJE, autor=escola['carla'])
    Tarefa.objects.create(disciplina=escola['mat_b'], titulo='Do 3º B', prazo=HOJE, autor=escola['bruno'])

    def titulos(usuario):
        return [t['titulo'] for t in cliente_autenticado(usuario).get(URL).json()]

    assert titulos(escola['ana']) == ['Do 3º A']
    assert titulos(escola['rita']) == ['Do 3º A']
    assert titulos(escola['leo']) == ['Do 3º B']
    assert titulos(escola['carla']) == ['Do 3º A']


def test_lista_com_prazo_mais_proximo_primeiro_e_encerradas_no_fim(escola, cliente_autenticado):
    for titulo, dias in [('Daqui a 5 dias', 5), ('Encerrada', -2), ('Amanhã', 1)]:
        Tarefa.objects.create(disciplina=escola['mat_a'], titulo=titulo, prazo=HOJE + timedelta(days=dias))

    tarefas = cliente_autenticado(escola['ana']).get(URL).json()

    assert [t['titulo'] for t in tarefas] == ['Amanhã', 'Daqui a 5 dias', 'Encerrada']
    assert [t['encerrada'] for t in tarefas] == [False, False, True]


def test_anexo_so_e_baixado_por_quem_ve_a_tarefa(escola, cliente_autenticado, email):
    criada = cliente_autenticado(escola['carla']).post(
        URL, dados(escola['mat_a'], arquivos=[pdf()]), format='multipart').json()
    caminho = f'{URL}{criada["id"]}/anexos/{criada["anexos"][0]["id"]}/'

    baixado = cliente_autenticado(escola['ana']).get(caminho)
    assert baixado.status_code == 200
    assert 'lista.pdf' in baixado['Content-Disposition']
    assert b''.join(baixado.streaming_content).startswith(b'%PDF')
    baixado.close()

    assert cliente_autenticado(escola['leo']).get(caminho).status_code == 404


def test_professor_exclui_a_propria_tarefa_e_o_arquivo_some_do_disco(escola, cliente_autenticado, email):
    criada = cliente_autenticado(escola['carla']).post(
        URL, dados(escola['mat_a'], arquivos=[pdf()]), format='multipart').json()
    anexo = AnexoTarefa.objects.get()
    armazenamento, nome = anexo.arquivo.storage, anexo.arquivo.name

    assert cliente_autenticado(escola['bruno']).delete(f'{URL}{criada["id"]}/').status_code == 404
    assert cliente_autenticado(escola['carla']).delete(f'{URL}{criada["id"]}/').status_code == 204

    assert not Tarefa.objects.exists()
    assert not armazenamento.exists(nome)
    assert AuditLog.objects.filter(acao='tarefa_excluida').exists()


def test_falha_no_email_mantem_a_tarefa_e_registra_no_log(escola, cliente_autenticado, email):
    email.side_effect = RuntimeError('Brevo fora do ar')

    response = cliente_autenticado(escola['carla']).post(URL, dados(escola['mat_a']), format='json')

    assert response.status_code == 201
    assert response.json()['email_enviado'] is False
    assert Tarefa.objects.count() == 1
    assert AuditLog.objects.filter(acao='notificacao_falha_envio').exists()
