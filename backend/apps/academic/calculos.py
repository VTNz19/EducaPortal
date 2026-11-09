"""Cálculo de médias e frequência (RF17). Funções puras, sem acesso ao banco.

RN70: médias e frequência não são armazenadas; são calculadas a cada consulta.
"""
from decimal import ROUND_HALF_UP, Decimal

MEDIA_MINIMA = Decimal('6.0')
FREQUENCIA_MINIMA = Decimal('75')
TOTAL_BIMESTRES = 4


def arredondar(valor, casas='0.1'):
    return Decimal(valor).quantize(Decimal(casas), rounding=ROUND_HALF_UP)


def calcular_media(notas):
    """RN67: média aritmética das notas publicadas, com uma casa decimal.

    Devolve (media, parcial). A média é None quando não há nota; é parcial
    quando ainda faltam bimestres.
    """
    notas = [Decimal(n) for n in notas if n is not None]
    if not notas:
        return None, False
    media = arredondar(sum(notas) / len(notas))
    return media, len(notas) < TOTAL_BIMESTRES


def calcular_frequencia(aulas, faltas):
    """RN68: (aulas registradas - faltas) / aulas registradas x 100.

    Devolve None quando ainda não há aulas registradas (exibido como "—").
    """
    if aulas <= 0:
        return None
    faltas = min(max(faltas, 0), aulas)
    return arredondar(Decimal(aulas - faltas) * 100 / aulas)


def abaixo_da_media(media):
    return media is not None and media < MEDIA_MINIMA


def abaixo_da_frequencia(frequencia):
    return frequencia is not None and frequencia < FREQUENCIA_MINIMA
