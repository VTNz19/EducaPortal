"""Testes unitários da regra de validade do link de definição de senha (RN16).

Nenhum teste acessa o banco: o token é criado só em memória e o relógio é fixado
com mock, para que a fronteira de 1 hora seja verificada sem depender do tempo real.
"""
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest

from apps.accounts.models import PasswordResetToken, User

AGORA = datetime(2026, 10, 9, 14, 0, tzinfo=UTC)


def criar_token(minutos_atras, usado=False):
    usuario = User(username='ana', email='ana@exemplo.com')
    return PasswordResetToken(usuario=usuario, criado_em=AGORA - timedelta(minutes=minutos_atras), usado=usado)


@patch('apps.accounts.models.timezone.now', return_value=AGORA)
def test_deve_considerar_valido_token_recem_criado_e_nao_usado(mock_now):
    token = criar_token(minutos_atras=5)

    valido = token.esta_valido()

    assert valido is True


@patch('apps.accounts.models.timezone.now', return_value=AGORA)
def test_deve_considerar_invalido_token_ja_usado_mesmo_dentro_do_prazo(mock_now):
    token = criar_token(minutos_atras=5, usado=True)

    valido = token.esta_valido()

    assert valido is False


@pytest.mark.parametrize(
    ('minutos_atras', 'esperado'),
    [
        (59, True),
        (60, False),
        (61, False),
    ],
)
@patch('apps.accounts.models.timezone.now', return_value=AGORA)
def test_deve_respeitar_a_fronteira_de_uma_hora_de_validade(mock_now, minutos_atras, esperado):
    token = criar_token(minutos_atras=minutos_atras)

    valido = token.esta_valido()

    assert valido is esperado
