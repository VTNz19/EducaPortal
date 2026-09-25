import requests
from django.conf import settings
from django.utils.html import escape

from .models import PasswordResetToken

BREVO_URL = 'https://api.brevo.com/v3/smtp/email'


def enviar_email(destinatario, assunto, html):
    """Envia um e-mail transacional pela API do Brevo. Lança exceção se o envio falhar."""
    resposta = requests.post(
        BREVO_URL,
        headers={'api-key': settings.BREVO_API_KEY, 'accept': 'application/json'},
        json={
            'sender': {'name': settings.EMAIL_REMETENTE_NOME, 'email': settings.EMAIL_REMETENTE},
            'to': [{'email': destinatario}],
            'subject': assunto,
            'htmlContent': html,
        },
        timeout=10,
    )
    if resposta.status_code >= 400:
        raise RuntimeError(f'Brevo respondeu {resposta.status_code}: {resposta.text}')


def enviar_link_definir_senha(usuario, primeiro_acesso=False):
    """Gera um token de uso único e envia por e-mail o link para definir a senha.

    Tokens anteriores ainda não usados deixam de valer. Lança exceção se o
    envio falhar.
    """
    PasswordResetToken.objects.filter(usuario=usuario, usado=False).update(usado=True)
    reset_token = PasswordResetToken.objects.create(usuario=usuario)
    link = f"{settings.FRONTEND_URL}/redefinir-senha?token={reset_token.token}"
    nome = escape(usuario.get_full_name() or usuario.username)

    if primeiro_acesso:
        assunto = "Sua conta no EducaPortal foi criada"
        corpo = (
            f"<p>Olá, {nome}.</p>"
            f"<p>A secretaria da escola criou sua conta no EducaPortal.</p>"
            f'<p><a href="{link}">Clique aqui para definir sua senha</a></p>'
            f"<p>Este link expira em 1 hora. Depois disso, use a opção "
            f"\"Esqueci minha senha\" na tela de login.</p>"
        )
    else:
        assunto = "Redefinição de senha - EducaPortal"
        corpo = (
            f"<p>Olá, {nome}.</p>"
            f"<p>Recebemos um pedido para redefinir sua senha no EducaPortal.</p>"
            f'<p><a href="{link}">Clique aqui para criar uma nova senha</a></p>'
            f"<p>Este link expira em 1 hora. Se você não solicitou isso, ignore este e-mail.</p>"
        )

    enviar_email(usuario.email, assunto, corpo)
