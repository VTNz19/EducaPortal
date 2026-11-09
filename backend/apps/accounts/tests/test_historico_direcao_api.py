"""Testes de integração do acesso ao histórico e à exportação de dados (RF06, RF07, RN25):
somente a Direção, que atua como super usuário, pode consultar e exportar."""
import pytest

from apps.audit.models import AuditLog
from apps.audit.utils import registrar_log

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]


@pytest.fixture
def ana(criar_usuario):
    aluna = criar_usuario('aluno', email='ana@exemplo.com')
    registrar_log(aluna, 'login_sucesso')
    return aluna


@pytest.mark.parametrize('acao', ['logs', 'exportar'])
def test_direcao_pode_consultar_historico_e_exportar_dados(acao, ana, criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('direcao'))

    response = client.get(f'/api/v1/usuarios/{ana.id}/{acao}/')

    assert response.status_code == 200


@pytest.mark.parametrize('acao', ['logs', 'exportar'])
def test_secretaria_nao_pode_consultar_historico_nem_exportar_dados(acao, ana, criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('secretaria'))

    response = client.get(f'/api/v1/usuarios/{ana.id}/{acao}/')

    assert response.status_code == 403
    assert not AuditLog.objects.filter(acao='dados_exportados').exists()


def test_secretaria_continua_vendo_a_lista_e_o_perfil_das_contas(ana, criar_usuario, cliente_autenticado):
    client = cliente_autenticado(criar_usuario('secretaria'))

    lista = client.get('/api/v1/usuarios/')
    perfil = client.get(f'/api/v1/usuarios/{ana.id}/')

    assert lista.status_code == 200
    assert perfil.status_code == 200
    assert perfil.json()['email'] == 'ana@exemplo.com'
