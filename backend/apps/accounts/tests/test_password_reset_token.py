"""Testes unitários da regra de validade do link de definição de senha (RN13).

Nenhum teste acessa o banco: o token é criado só em memória e o relógio é fixado
com mock, para que a fronteira de 1 hora seja verificada sem depender do tempo real.
"""
from datetime import datetime, timedelta, timezone as dt_timezone
from unittest.mock import patch

import pytest

from apps.accounts.models import PasswordResetToken, User

AGORA = datetime(2026, 10, 9, 14, 0, tzinfo=dt_timezone.utc)


def criar_token(minutos_atras, usado=False):
    usuario = User(username='ana', email='ana@exemplo.com')
    return PasswordResetToken(usuario=usuario, criado_em=AGORA - timedelta(minutes=minutos_atras), usado=usado)


@patch('apps.accounts.models.timezone.now', return_value=AGORA)
def test_deve_considerar_valido_token_recem_criado_e_nao_usado(mock_now):
    # Arrange
    token = criar_token(minutos_atras=5)

    # Act
    valido = token.esta_valido()

    # Assert
    assert valido is True


@patch('apps.accounts.models.timezone.now', return_value=AGORA)
def test_deve_considerar_invalido_token_ja_usado_mesmo_dentro_do_prazo(mock_now):
    # Arrange
    token = criar_token(minutos_atras=5, usado=True)

    # Act
    valido = token.esta_valido()

    # Assert
    assert valido is False


@pytest.mark.parametrize(
    ('minutos_atras', 'esperado'),
    [
        (59, True),   # último minuto antes do fim do prazo
        (60, False),  # exatamente 1 hora: já expirou
        (61, False),  # depois do prazo
    ],
)
@patch('apps.accounts.models.timezone.now', return_value=AGORA)
def test_deve_respeitar_a_fronteira_de_uma_hora_de_validade(mock_now, minutos_atras, esperado):
    # Arrange
    token = criar_token(minutos_atras=minutos_atras)

    # Act
    valido = token.esta_valido()

    # Assert
    assert valido is esperado
