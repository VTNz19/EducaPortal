"""Testes unitários da regra dos bimestres do ano letivo (RN50), sem banco de dados."""
from datetime import date

import pytest

from apps.academic.regras import erros_dos_bimestres


def bimestres_validos():
    return [
        {'numero': 1, 'inicio': date(2026, 2, 2), 'fim': date(2026, 4, 17)},
        {'numero': 2, 'inicio': date(2026, 4, 20), 'fim': date(2026, 7, 3)},
        {'numero': 3, 'inicio': date(2026, 7, 27), 'fim': date(2026, 9, 30)},
        {'numero': 4, 'inicio': date(2026, 10, 1), 'fim': date(2026, 12, 11)},
    ]


def test_deve_aceitar_quatro_bimestres_em_ordem_e_sem_sobreposicao():
    erros = erros_dos_bimestres(bimestres_validos())

    assert erros == []


def test_deve_recusar_bimestre_que_comeca_antes_do_fim_do_anterior():
    bimestres = bimestres_validos()
    bimestres[1]['inicio'] = date(2026, 4, 10)

    erros = erros_dos_bimestres(bimestres)

    assert erros == ['O 2º bimestre deve começar depois do fim do 1º bimestre.']


def test_deve_recusar_bimestre_com_fim_anterior_ao_inicio():
    bimestres = bimestres_validos()
    bimestres[3]['fim'] = date(2026, 9, 1)

    erros = erros_dos_bimestres(bimestres)

    assert 'O fim do 4º bimestre não pode ser anterior ao início.' in erros


@pytest.mark.parametrize(
    'numeros',
    [
        [1, 2, 3],
        [1, 2, 3, 3],
        [1, 2, 3, 5],
    ],
)
def test_deve_exigir_exatamente_os_bimestres_de_1_a_4(numeros):
    bimestres = [{'numero': n, 'inicio': date(2026, n, 1), 'fim': date(2026, n, 20)} for n in numeros]

    erros = erros_dos_bimestres(bimestres)

    assert erros == ['Informe os 4 bimestres do ano letivo, numerados de 1 a 4.']


def test_deve_aceitar_bimestre_que_comeca_no_dia_seguinte_ao_fim_do_anterior():
    bimestres = bimestres_validos()
    bimestres[1]['inicio'] = date(2026, 4, 18)

    erros = erros_dos_bimestres(bimestres)

    assert erros == []
