"""Configuração usada só pelos testes automatizados."""
from .settings import *  # noqa: F401,F403

# Banco descartável em memória: não depende do PostgreSQL nem de dados cadastrados.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Hash rápido só nos testes (em produção continua o Argon2).
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Valores fictícios: nenhum teste envia e-mail de verdade.
BREVO_API_KEY = 'chave-de-teste'
EMAIL_REMETENTE = 'teste@exemplo.com'
FRONTEND_URL = 'http://localhost:5173'
