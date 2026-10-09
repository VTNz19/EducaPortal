"""Fixtures compartilhadas pelos testes de integração.

Só os testes marcados com django_db usam estas fixtures de banco; os testes
unitários continuam sem acesso a ele.
"""
import pytest
from django.conf import settings
from rest_framework.test import APIClient

from apps.accounts.models import User

SENHA_PADRAO = 'SenhaForte#2026'


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def criar_usuario(db):
    """Cria um usuário real no banco de teste, por padrão já com o termo vigente aceito."""

    def _criar(role, email=None, aceitou_termos=True, **extras):
        email = email or f'{role}@exemplo.com'
        return User.objects.create_user(
            username=email.split('@')[0],
            email=email,
            password=SENHA_PADRAO,
            role=role,
            termos_versao_aceita=settings.VERSAO_TERMOS if aceitou_termos else '',
            **extras,
        )

    return _criar


@pytest.fixture
def cliente_autenticado(api_client):
    """Devolve um APIClient autenticado como o usuário informado."""

    def _autenticar(usuario):
        api_client.force_authenticate(user=usuario)
        return api_client

    return _autenticar
