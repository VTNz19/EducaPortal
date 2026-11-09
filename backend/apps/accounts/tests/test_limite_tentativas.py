"""Testes do limite de tentativas nas rotas públicas de autenticação."""
import pytest

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]


def test_login_bloqueia_apos_10_tentativas_por_minuto(api_client, criar_usuario):
    criar_usuario('aluno', email='aluno@exemplo.com')
    dados = {'email': 'aluno@exemplo.com', 'password': 'senha-errada'}

    respostas = [api_client.post('/api/v1/auth/login/', dados, format='json').status_code for _ in range(11)]

    assert respostas[:10] == [401] * 10
    assert respostas[10] == 429


def test_esqueci_senha_bloqueia_apos_5_pedidos_por_minuto(api_client):
    respostas = [api_client.post('/api/v1/auth/esqueci-senha/', {'email': 'ninguem@exemplo.com'},
                                 format='json').status_code for _ in range(6)]

    assert respostas[:5] == [200] * 5
    assert respostas[5] == 429
