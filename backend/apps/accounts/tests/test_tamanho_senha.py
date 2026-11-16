"""RN19: a nova senha tem no mínimo 8 caracteres; senhas antigas mais curtas continuam entrando."""
import pytest

from apps.accounts.models import PasswordResetToken
from apps.accounts.serializers import RedefinirSenhaSerializer

URL = '/api/v1/auth/redefinir-senha/'
MENSAGEM = 'A senha deve ter no mínimo 8 caracteres.'


def test_senha_com_7_caracteres_e_recusada():
    serializer = RedefinirSenhaSerializer(data={'token': 'abc', 'nova_senha': 'Abc@123'})

    assert not serializer.is_valid()
    assert serializer.errors['nova_senha'] == [MENSAGEM]


def test_senha_com_8_caracteres_e_aceita():
    serializer = RedefinirSenhaSerializer(data={'token': 'abc', 'nova_senha': 'Abc@1234'})

    assert serializer.is_valid(), serializer.errors


def test_espacos_contam_e_nao_sao_removidos():
    serializer = RedefinirSenhaSerializer(data={'token': 'abc', 'nova_senha': ' abc 12 '})

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['nova_senha'] == ' abc 12 '


@pytest.mark.django_db
@pytest.mark.integracao
def test_api_recusa_senha_curta_e_o_link_continua_valendo(criar_usuario, api_client):
    usuario = criar_usuario('aluno')
    token = PasswordResetToken.objects.create(usuario=usuario)

    curta = api_client.post(URL, {'token': token.token, 'nova_senha': 'curta12'}, format='json')

    assert curta.status_code == 400
    assert curta.json() == {'nova_senha': [MENSAGEM]}
    token.refresh_from_db()
    assert not token.usado

    certa = api_client.post(URL, {'token': token.token, 'nova_senha': 'NovaSenha#26'}, format='json')

    assert certa.status_code == 200
    usuario.refresh_from_db()
    assert usuario.check_password('NovaSenha#26')


@pytest.mark.django_db
@pytest.mark.integracao
def test_quem_ja_tem_senha_curta_continua_entrando(criar_usuario, api_client):
    usuario = criar_usuario('aluno', email='antiga@exemplo.com')
    usuario.set_password('abc123')
    usuario.save()

    response = api_client.post('/api/v1/auth/login/', {'email': 'antiga@exemplo.com', 'password': 'abc123'},
                               format='json')

    assert response.status_code == 200
