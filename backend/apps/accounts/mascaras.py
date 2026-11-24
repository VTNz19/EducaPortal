"""Mascaramento de e-mails nas respostas da API (minimização, LGPD art. 6º, III).

O e-mail completo fica só no banco, onde é usado no login e no envio dos e-mails. Nas telas, cada
pessoa vê o próprio e-mail completo e o dos demais mascarado, por exemplo an***@exemplo.com.
"""
import re

PADRAO_EMAIL = re.compile(r'([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})')


def mascarar_email(email):
    if not email or '@' not in email:
        return email
    local, _, dominio = email.rpartition('@')
    visivel = local[:2] if len(local) > 2 else local[:1]
    return f'{visivel}***@{dominio}'


def mascarar_emails_no_texto(texto):
    """Mascara os e-mails que aparecem no meio de um texto, como os detalhes do log de auditoria."""
    if not texto:
        return texto
    return PADRAO_EMAIL.sub(lambda m: mascarar_email(m.group(0)), texto)


def email_para(usuario, quem_ve):
    """O próprio titular vê o e-mail completo; qualquer outra pessoa vê o e-mail mascarado."""
    if quem_ve is not None and getattr(quem_ve, 'pk', None) == usuario.pk:
        return usuario.email
    return mascarar_email(usuario.email)
