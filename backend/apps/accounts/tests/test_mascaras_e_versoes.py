"""Testes unitários do mascaramento de e-mails (RN88) e da numeração das versões dos documentos (RF23)."""
from types import SimpleNamespace

import pytest

from apps.accounts.documentos import descrever_versao, proxima_versao
from apps.accounts.mascaras import email_para, mascarar_email, mascarar_emails_no_texto


@pytest.mark.parametrize(('email', 'mascarado'), [
    ('ana.souza@exemplo.com', 'an***@exemplo.com'),
    ('ana@exemplo.com', 'an***@exemplo.com'),
    ('al@exemplo.com', 'a***@exemplo.com'),
    ('a@exemplo.com', 'a***@exemplo.com'),
    ('removido-12@anonimizado.invalid', 're***@anonimizado.invalid'),
])
def test_deve_mascarar_o_e_mail_mantendo_so_o_inicio_e_o_dominio(email, mascarado):
    assert mascarar_email(email) == mascarado


@pytest.mark.parametrize('vazio', ['', None, 'sem-arroba'])
def test_deve_devolver_sem_alterar_o_que_nao_e_e_mail(vazio):
    assert mascarar_email(vazio) == vazio


def test_deve_mascarar_todos_os_e_mails_no_meio_de_um_texto():
    texto = 'tentativa de login: ana.souza@exemplo.com; aviso para bruno@exemplo.com.'

    assert mascarar_emails_no_texto(texto) == 'tentativa de login: an***@exemplo.com; aviso para br***@exemplo.com.'
    assert mascarar_emails_no_texto('usuario id=3, papel=aluno') == 'usuario id=3, papel=aluno'
    assert mascarar_emails_no_texto('') == ''


def test_so_o_proprio_titular_ve_o_e_mail_completo():
    ana = SimpleNamespace(pk=1, email='ana@exemplo.com')
    secretaria = SimpleNamespace(pk=2, email='secretaria@exemplo.com')

    assert email_para(ana, ana) == 'ana@exemplo.com'
    assert email_para(ana, secretaria) == 'an***@exemplo.com'
    assert email_para(ana, None) == 'an***@exemplo.com'


@pytest.mark.parametrize(('atual', 'proxima'), [
    ('2.2', '2.3'),
    ('2.9', '2.10'),
    ('3', '4'),
    ('1.0.9', '1.0.10'),
    ('beta', 'beta.1'),
])
def test_cada_publicacao_sobe_o_ultimo_numero_da_versao(atual, proxima):
    assert proxima_versao(atual) == proxima


def test_deve_descrever_o_par_de_versoes_aceito():
    assert descrever_versao('2.3+2.1') == 'Termo de Uso e Aceite 2.3 e Política de Privacidade 2.1'
