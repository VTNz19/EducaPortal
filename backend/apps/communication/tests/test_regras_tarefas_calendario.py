"""Testes unitários das regras de tarefas e do calendário (RN75 a RN77). Não usam o banco."""
from datetime import date

import pytest

from apps.communication.regras import (
    TAMANHO_MAXIMO_ANEXO,
    erro_das_datas_do_evento,
    erro_do_anexo,
    erro_do_prazo,
)

PDF = b'%PDF-1.7'
PNG = b'\x89PNG\r\n\x1a\n'
JPG = b'\xff\xd8\xff\xe0'
DOCX = b'PK\x03\x04'


@pytest.mark.parametrize(('nome', 'inicio'), [
    ('lista.pdf', PDF), ('mapa.PNG', PNG), ('foto.jpg', JPG), ('foto.jpeg', JPG), ('roteiro.docx', DOCX),
])
def test_aceita_os_tipos_permitidos(nome, inicio):
    assert erro_do_anexo(nome, 1024, inicio) is None


def test_aceita_arquivo_de_exatamente_10_mb():
    assert erro_do_anexo('lista.pdf', TAMANHO_MAXIMO_ANEXO, PDF) is None


def test_recusa_arquivo_acima_de_10_mb_informando_o_nome():
    assert erro_do_anexo('lista.pdf', 15 * 1024 * 1024, PDF) == (
        'O arquivo "lista.pdf" foi recusado: o tamanho passa de 10 MB.')


@pytest.mark.parametrize('nome', ['programa.exe', 'planilha.xlsx', 'sem_extensao'])
def test_recusa_tipo_nao_permitido(nome):
    assert erro_do_anexo(nome, 10, PDF) == (
        f'O arquivo "{nome}" foi recusado: tipo não permitido. Envie PDF, DOCX, PNG ou JPG.')


def test_recusa_arquivo_renomeado_cujo_conteudo_nao_bate_com_a_extensao():
    assert erro_do_anexo('lista.pdf', 10, b'MZ\x90\x00') == (
        'O arquivo "lista.pdf" foi recusado: o conteúdo não é de um arquivo PDF.')


def test_prazo_de_hoje_e_aceito_e_o_de_ontem_nao():
    hoje = date(2026, 11, 15)

    assert erro_do_prazo(hoje, hoje) is None
    assert erro_do_prazo(date(2026, 11, 14), hoje) == 'O prazo de entrega não pode ser anterior a hoje.'


def test_evento_de_um_dia_e_aceito_e_termino_antes_do_inicio_nao():
    assert erro_das_datas_do_evento(date(2026, 11, 20), date(2026, 11, 20)) is None
    assert erro_das_datas_do_evento(date(2026, 11, 20), date(2026, 11, 19)) == (
        'A data de término não pode ser anterior à data de início.')
