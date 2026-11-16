"""Testes de integração da API de avisos (/api/v1/avisos/).

A requisição passa por URL, autenticação, permissões, serializer e banco de
teste real (SQLite em memória), sem mocks.
"""
import pytest

from apps.audit.models import AuditLog
from apps.communication.models import Aviso

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]

URL = '/api/v1/avisos/'


def test_deve_criar_aviso_e_devolver_201_com_o_corpo_quando_professor_publica(criar_usuario, cliente_autenticado):
    professor = criar_usuario('professor', first_name='Carla', last_name='Mendes')
    client = cliente_autenticado(professor)

    dados = {'titulo': 'Prova de Matemática', 'conteudo': 'Dia 15, capítulos 1 a 3.'}
    response = client.post(URL, dados, format='json')

    assert response.status_code == 201
    corpo = response.json()
    assert corpo['titulo'] == 'Prova de Matemática'
    assert corpo['conteudo'] == 'Dia 15, capítulos 1 a 3.'
    assert corpo['autor'] == professor.id
    assert corpo['autor_nome'] == 'Carla Mendes'
    assert corpo['fixado'] is False
    assert Aviso.objects.filter(id=corpo['id'], autor=professor).exists()


def test_deve_responder_403_com_mensagem_quando_aluno_tenta_publicar_aviso(criar_usuario, cliente_autenticado):
    aluno = criar_usuario('aluno')
    client = cliente_autenticado(aluno)

    response = client.post(URL, {'titulo': 'Aviso indevido', 'conteudo': 'Texto.'}, format='json')

    assert response.status_code == 403
    assert response.json() == {'detail': 'Você não tem permissão para executar essa ação.'}
    assert Aviso.objects.count() == 0


def test_deve_responder_400_com_erro_no_campo_quando_titulo_esta_em_branco(criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('secretaria'))

    response = client.post(URL, {'titulo': '   ', 'conteudo': 'Texto do aviso.'}, format='json')

    assert response.status_code == 400
    assert response.json() == {'titulo': ['O título não pode ser vazio.']}
    assert Aviso.objects.count() == 0


def test_deve_responder_403_quando_usuario_ainda_nao_aceitou_o_termo_vigente(criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('professor', aceitou_termos=False))

    response = client.get(URL)

    assert response.status_code == 403
    assert response.json() == {'detail': 'É preciso aceitar a versão atual do Termo de Uso e Aceite.'}


def test_deve_responder_401_quando_requisicao_nao_tem_token(api_client):
    response = api_client.get(URL)

    assert response.status_code == 401
    assert 'detail' in response.json()


def test_deve_impedir_professor_de_excluir_aviso_de_outro_professor(criar_usuario, cliente_autenticado):
    autora = criar_usuario('professor', email='autora@exemplo.com')
    outro = criar_usuario('professor', email='outro@exemplo.com')
    aviso = Aviso.objects.create(titulo='Feira de ciências', conteudo='Sábado.', autor=autora)
    client = cliente_autenticado(outro)

    response = client.delete(f'{URL}{aviso.id}/')

    assert response.status_code == 403
    assert Aviso.objects.filter(id=aviso.id).exists()
    assert not AuditLog.objects.filter(acao='aviso_excluido').exists()
