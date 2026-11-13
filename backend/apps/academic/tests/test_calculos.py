"""Testes unitários do cálculo de médias e frequência (RF17, RN67 a RN69), sem banco de dados."""
from decimal import Decimal

import pytest

from apps.academic.calculos import abaixo_da_frequencia, abaixo_da_media, calcular_frequencia, calcular_media


def test_deve_calcular_a_media_aritmetica_dos_quatro_bimestres():
    media, parcial = calcular_media([Decimal('6.0'), Decimal('7.0'), Decimal('8.0'), Decimal('9.0')])

    assert media == Decimal('7.5')
    assert parcial is False


def test_deve_arredondar_a_media_para_uma_casa_decimal_para_cima_no_meio():
    notas = [Decimal('5.0'), Decimal('6.0'), Decimal('5.5'), Decimal('6.5')]

    media, _ = calcular_media(notas)

    assert media == Decimal('5.8')
    assert abaixo_da_media(media) is True


def test_deve_marcar_a_media_como_parcial_quando_faltam_bimestres():
    media, parcial = calcular_media([Decimal('8.0'), None, Decimal('6.0')])

    assert media == Decimal('7.0')
    assert parcial is True


def test_deve_devolver_media_vazia_quando_nao_ha_nota():
    media, parcial = calcular_media([None, None])

    assert media is None
    assert parcial is False
    assert abaixo_da_media(media) is False


def test_deve_calcular_a_frequencia_e_destacar_abaixo_de_75_por_cento():
    frequencia = calcular_frequencia(40, 12)

    assert frequencia == Decimal('70.0')
    assert abaixo_da_frequencia(frequencia) is True


def test_deve_devolver_frequencia_vazia_quando_ainda_nao_ha_aulas():
    frequencia = calcular_frequencia(0, 0)

    assert frequencia is None
    assert abaixo_da_frequencia(frequencia) is False


@pytest.mark.parametrize(
    ('aulas', 'faltas', 'abaixo'),
    [
        (100, 25, False),
        (100, 26, True),
    ],
)
def test_deve_respeitar_a_fronteira_de_75_por_cento(aulas, faltas, abaixo):
    frequencia = calcular_frequencia(aulas, faltas)

    assert abaixo_da_frequencia(frequencia) is abaixo


@pytest.mark.parametrize(
    ('media', 'abaixo'),
    [
        (Decimal('6.0'), False),
        (Decimal('5.9'), True),
    ],
)
def test_deve_respeitar_a_fronteira_da_media_6(media, abaixo):
    assert abaixo_da_media(media) is abaixo
