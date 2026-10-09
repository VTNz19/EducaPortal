"""Testes unitários da regra de recuperação de senha na EsqueciSenhaView (RN15).

A busca do usuário, o envio do e-mail e o registro no log são mockados: o teste
verifica só a decisão da view, sem banco e sem serviço externo.
"""
from unittest.mock import ANY, MagicMock, patch

from rest_framework.test import APIRequestFactory

from apps.accounts.views import EsqueciSenhaView

URL = '/api/v1/auth/esqueci-senha/'
MENSAGEM_PADRAO = 'Se o e-mail existir, enviamos um link de redefinição.'


def executar(email):
    request = APIRequestFactory().post(URL, {'email': email}, format='json')
    return EsqueciSenhaView.as_view()(request)


def usuario_mock(tem_senha=True):
    usuario = MagicMock()
    usuario.has_usable_password.return_value = tem_senha
    return usuario


@patch('apps.accounts.views.registrar_log')
@patch('apps.accounts.views.enviar_link_definir_senha')
@patch('apps.accounts.views.User')
def test_deve_enviar_link_de_redefinicao_quando_o_email_existe(mock_user, mock_enviar, mock_log):
    # Arrange
    usuario = usuario_mock(tem_senha=True)
    mock_user.objects.filter.return_value.first.return_value = usuario

    # Act
    response = executar('ana@exemplo.com')

    # Assert
    assert response.status_code == 200
    assert response.data == {'detail': MENSAGEM_PADRAO}
    mock_enviar.assert_called_once_with(usuario, primeiro_acesso=False)
    mock_log.assert_called_once_with(usuario, 'esqueci_senha_solicitado', request=ANY)


@patch('apps.accounts.views.registrar_log')
@patch('apps.accounts.views.enviar_link_definir_senha')
@patch('apps.accounts.views.User')
def test_nunca_deve_enviar_email_nem_revelar_quando_o_email_nao_existe(mock_user, mock_enviar, mock_log):
    # Arrange
    mock_user.objects.filter.return_value.first.return_value = None

    # Act
    response = executar('ninguem@exemplo.com')

    # Assert: mesma resposta do e-mail cadastrado, e nenhum envio
    assert response.status_code == 200
    assert response.data == {'detail': MENSAGEM_PADRAO}
    mock_enviar.assert_not_called()
    mock_log.assert_not_called()


@patch('apps.accounts.views.registrar_log')
@patch('apps.accounts.views.enviar_link_definir_senha', side_effect=RuntimeError('Brevo respondeu 503'))
@patch('apps.accounts.views.User')
def test_deve_responder_503_e_registrar_log_quando_o_envio_falha(mock_user, mock_enviar, mock_log):
    # Arrange
    usuario = usuario_mock()
    mock_user.objects.filter.return_value.first.return_value = usuario

    # Act
    response = executar('ana@exemplo.com')

    # Assert
    assert response.status_code == 503
    mock_log.assert_called_once_with(
        usuario, 'esqueci_senha_falha_envio', detalhes='erro: Brevo respondeu 503', request=ANY,
    )


@patch('apps.accounts.views.registrar_log')
@patch('apps.accounts.views.enviar_link_definir_senha')
@patch('apps.accounts.views.User')
def test_deve_enviar_email_de_primeiro_acesso_quando_a_conta_ainda_nao_tem_senha(mock_user, mock_enviar, mock_log):
    # Arrange: conta criada pela secretaria, sem senha definida
    usuario = usuario_mock(tem_senha=False)
    mock_user.objects.filter.return_value.first.return_value = usuario

    # Act
    executar('novo@exemplo.com')

    # Assert
    mock_enviar.assert_called_once_with(usuario, primeiro_acesso=True)
