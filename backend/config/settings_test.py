"""Configuração usada só pelos testes automatizados."""
from .settings import *  # noqa: F401,F403

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
