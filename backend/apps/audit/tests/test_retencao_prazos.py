"""Testes unitários do cálculo dos prazos de retenção (RN81). Não usam o banco."""
from datetime import UTC, date, datetime

from apps.audit.retencao import descrever, limites, meses_antes


def test_meses_antes_mantem_o_dia():
    assert meses_antes(date(2026, 11, 15), 6) == date(2026, 5, 15)


def test_meses_antes_atravessa_o_ano():
    assert meses_antes(date(2026, 3, 10), 6) == date(2025, 9, 10)


def test_meses_antes_usa_o_ultimo_dia_quando_o_mes_e_mais_curto():
    assert meses_antes(date(2026, 8, 31), 6) == date(2026, 2, 28)
    assert meses_antes(date(2028, 8, 31), 6) == date(2028, 2, 29)


def test_limites_de_cada_tipo_de_registro():
    agora = datetime(2026, 11, 15, 15, 0, tzinfo=UTC)

    limite = limites(agora)

    assert limite['logs_auditoria'] == datetime(2026, 5, 15, 15, 0, tzinfo=UTC)
    assert limite['links_senha'] == datetime(2026, 11, 8, 15, 0, tzinfo=UTC)
    assert limite['avisos'] == datetime(2025, 11, 15, 15, 0, tzinfo=UTC)
    assert limite['contas'] == datetime(2025, 11, 15, 15, 0, tzinfo=UTC)
    assert limite['tarefas'] == limite['eventos'] == date(2025, 11, 15)


def test_descricao_da_execucao_tem_so_quantidades():
    assert descrever({'logs_auditoria': 3, 'avisos': 0}) == 'logs_auditoria=3, avisos=0'
