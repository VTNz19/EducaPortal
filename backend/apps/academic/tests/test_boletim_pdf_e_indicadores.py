"""Testes unitários do boletim em PDF (RF18, RN72), dos auxiliares do painel (RF21) e do aviso por e-mail
sem dados acadêmicos (RN61, RN66), sem banco de dados."""
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.test import override_settings

from apps.academic.indicadores import (
    chave_alfabetica,
    descrever_bimestre,
    media_de,
    nome_de,
    numero,
    percentual,
)
from apps.academic.pdf import _numero, gerar_boletim_pdf
from apps.academic.servicos import notificar


def linha_do_boletim(nome, notas, media, parcial=False, frequencia=Decimal('90.0'), faltas=2):
    return {
        'disciplina': nome,
        'notas': {str(b): notas[b - 1] for b in range(1, 5)},
        'media': media,
        'media_parcial': parcial,
        'abaixo_media': media is not None and media < 6,
        'aulas': 20,
        'faltas': faltas,
        'frequencia': frequencia,
        'abaixo_frequencia': frequencia is not None and frequencia < 75,
    }


def boletim_de_exemplo():
    return {
        'aluno': {'id': 1, 'nome': 'Ana Souza & Filhos <teste>'},
        'ano': 2026,
        'turma': '1º A',
        'disciplinas': [
            linha_do_boletim('Matemática', [Decimal('5.0'), Decimal('7.0'), None, None], Decimal('6.0'), parcial=True),
            linha_do_boletim('Português', [Decimal('4.0'), Decimal('5.0'), Decimal('5.5'), Decimal('6.0')],
                             Decimal('5.1'), frequencia=Decimal('70.0'), faltas=6),
            linha_do_boletim('Artes', [None, None, None, None], None, frequencia=None, faltas=0),
        ],
    }


def test_deve_gerar_o_boletim_como_um_pdf_valido_em_memoria():
    conteudo = gerar_boletim_pdf(boletim_de_exemplo())

    assert isinstance(conteudo, bytes)
    assert conteudo.startswith(b'%PDF')
    assert conteudo.rstrip().endswith(b'%%EOF')


def test_deve_gerar_o_pdf_mesmo_sem_nenhuma_disciplina():
    boletim = boletim_de_exemplo()
    boletim['disciplinas'] = []

    assert gerar_boletim_pdf(boletim).startswith(b'%PDF')


def test_deve_formatar_os_numeros_do_pdf_com_virgula_e_traco_quando_vazio():
    assert _numero(Decimal('7.5')) == '7,5'
    assert _numero(Decimal('8.0')) == '8,0'
    assert _numero(Decimal('82.5'), '%') == '82,5%'
    assert _numero(None) == '—'


def test_deve_converter_decimal_em_numero_para_os_graficos():
    assert numero(Decimal('6.5')) == 6.5
    assert numero(None) is None


def test_deve_calcular_a_media_ignorando_valores_vazios():
    assert media_de([Decimal('6.0'), None, Decimal('8.0')]) == Decimal('7.0')
    assert media_de([None, None]) is None
    assert media_de([]) is None


def test_deve_calcular_o_percentual_e_nao_dividir_por_zero():
    assert percentual(1, 4) == Decimal('25.0')
    assert percentual(1, 3) == Decimal('33.3')
    assert percentual(0, 0) is None


def test_deve_ordenar_nomes_acentuados_junto_com_os_demais():
    nomes = ['Bruno', 'Ana', 'Álvaro', 'ana clara']

    assert sorted(nomes, key=chave_alfabetica) == ['Álvaro', 'Ana', 'ana clara', 'Bruno']


def test_deve_usar_o_nome_completo_ou_o_usuario_quando_nao_ha_nome():
    com_nome = SimpleNamespace(get_full_name=lambda: 'Ana Souza', username='ana.souza')
    sem_nome = SimpleNamespace(get_full_name=lambda: '', username='ana.souza')

    assert nome_de(com_nome) == 'Ana Souza'
    assert nome_de(sem_nome) == 'ana.souza'


def test_deve_descrever_o_bimestre_com_numero_e_periodo():
    bimestre = SimpleNamespace(numero=2, inicio=date(2026, 4, 20), fim=date(2026, 7, 3))

    assert descrever_bimestre(bimestre) == {'numero': 2, 'inicio': date(2026, 4, 20), 'fim': date(2026, 7, 3)}


@override_settings(FRONTEND_URL='https://portal.exemplo.com')
def test_o_email_de_aviso_leva_so_o_link_e_nunca_a_nota():
    with patch('apps.academic.servicos.enviar_email_em_lote') as enviar:
        ok = notificar(['ana@exemplo.com'], 'Notas novas no EducaPortal', 'Há notas novas em <Matemática>.',
                       '/boletim', usuario=None, request=None)

    assert ok is True
    destinatarios, assunto, html = enviar.call_args.args
    assert destinatarios == ['ana@exemplo.com']
    assert assunto == 'Notas novas no EducaPortal'
    assert 'href="https://portal.exemplo.com/boletim"' in html
    assert '&lt;Matemática&gt;' in html
    assert 'não traz notas nem faltas' in html


def test_uma_falha_no_envio_fica_no_log_e_nao_interrompe_a_operacao():
    with (
        patch('apps.academic.servicos.enviar_email_em_lote', side_effect=RuntimeError('Brevo fora do ar')),
        patch('apps.academic.servicos.registrar_log') as registrar,
    ):
        ok = notificar(['ana@exemplo.com'], 'Assunto', 'Texto', '/painel', usuario='professor', request=None)

    assert ok is False
    usuario, acao = registrar.call_args.args
    assert usuario == 'professor'
    assert acao == 'notificacao_falha_envio'
    assert 'Brevo fora do ar' in registrar.call_args.kwargs['detalhes']
