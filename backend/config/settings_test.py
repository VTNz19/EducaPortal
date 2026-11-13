"""Configuração usada só pelos testes automatizados.

A chave abaixo é fictícia e só existe para os testes rodarem sem o arquivo .env (por exemplo, no CI).
Ela não é usada em nenhum ambiente real.
"""
import os

os.environ.setdefault('DJANGO_SECRET_KEY', 'chave-ficticia-somente-para-testes-automatizados')

from .settings import *  # noqa: E402,F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

BREVO_API_KEY = 'chave-de-teste'
EMAIL_REMETENTE = 'teste@exemplo.com'
FRONTEND_URL = 'http://localhost:5173'
