"""Testes unitários do envio de e-mails pelo Brevo (RN12 a RN14).

A chamada HTTP (requests.post) e o acesso ao banco (PasswordResetToken.objects)
são substituídos por mocks: nenhum e-mail real é enviado.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings

from apps.accounts.emails import BREVO_URL, enviar_email, enviar_link_definir_senha
from apps.accounts.models import User


def resposta(status_code, texto=''):
    return MagicMock(status_code=status_code, text=texto)


# ---------------------------------------------------------------- enviar_email

@patch('apps.accounts.emails.requests.post', return_value=resposta(201))
def test_deve_enviar_email_para_a_api_do_brevo_com_a_chave_e_o_destinatario(mock_post):
    # Act
    enviar_email('ana@exemplo.com', 'Assunto', '<p>Olá</p>')

    # Assert
    mock_post.assert_called_once_with(
        BREVO_URL,
        headers={'api-key': settings.BREVO_API_KEY, 'accept': 'application/json'},
        json={
            'sender': {'name': settings.EMAIL_REMETENTE_NOME, 'email': settings.EMAIL_REMETENTE},
            'to': [{'email': 'ana@exemplo.com'}],
            'subject': 'Assunto',
            'htmlContent': '<p>Olá</p>',
        },
        timeout=10,
    )


@patch('apps.accounts.emails.requests.post', return_value=resposta(401, 'Key not found'))
def test_deve_lancar_erro_com_mensagem_quando_o_brevo_recusa_o_envio(mock_post):
    # Act / Assert
    with pytest.raises(RuntimeError, match='Brevo respondeu 401: Key not found'):
        enviar_email('ana@exemplo.com', 'Assunto', '<p>Olá</p>')


@pytest.mark.parametrize(
    ('status', 'deve_falhar'),
    [
        (399, False),  # último código antes da faixa de erro
        (400, True),   # primeiro código considerado erro
    ],
)
def test_deve_tratar_como_falha_apenas_respostas_a_partir_de_400(status, deve_falhar):
    # Arrange
    with patch('apps.accounts.emails.requests.post', return_value=resposta(status)):
        # Act / Assert
        if deve_falhar:
            with pytest.raises(RuntimeError, match=f'Brevo respondeu {status}'):
                enviar_email('ana@exemplo.com', 'Assunto', '<p>Olá</p>')
        else:
            assert enviar_email('ana@exemplo.com', 'Assunto', '<p>Olá</p>') is None


# ---------------------------------------------------------------- enviar_link_definir_senha

@patch('apps.accounts.emails.enviar_email')
@patch('apps.accounts.emails.PasswordResetToken')
def test_deve_invalidar_links_antigos_e_enviar_convite_de_primeiro_acesso(mock_token, mock_enviar):
    # Arrange
    usuario = User(username='ana', first_name='Ana', last_name='Souza', email='ana@exemplo.com')
    mock_token.objects.create.return_value = SimpleNamespace(token='abc-123')

    # Act
    enviar_link_definir_senha(usuario, primeiro_acesso=True)

    # Assert
    mock_token.objects.filter.assert_called_once_with(usuario=usuario, usado=False)
    mock_token.objects.filter.return_value.update.assert_called_once_with(usado=True)
    destinatario, assunto, html = mock_enviar.call_args.args
    assert destinatario == 'ana@exemplo.com'
    assert assunto == 'Sua conta no EducaPortal foi criada'
    assert f'{settings.FRONTEND_URL}/redefinir-senha?token=abc-123' in html


@patch('apps.accounts.emails.enviar_email')
@patch('apps.accounts.emails.PasswordResetToken')
def test_deve_escapar_html_no_nome_do_usuario_dentro_do_email(mock_token, mock_enviar):
    # Arrange: nome com marcação HTML não pode virar código no e-mail
    usuario = User(username='x', first_name='<script>', last_name='', email='x@exemplo.com')
    mock_token.objects.create.return_value = SimpleNamespace(token='abc-123')

    # Act
    enviar_link_definir_senha(usuario)

    # Assert
    _, assunto, html = mock_enviar.call_args.args
    assert assunto == 'Redefinição de senha - EducaPortal'
    assert '&lt;script&gt;' in html
    assert '<script>' not in html
