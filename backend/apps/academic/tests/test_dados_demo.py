"""Testes do comando de dados de demonstração."""
from datetime import date, timedelta

import pytest
from django.core.management import CommandError, call_command
from django.utils import timezone

from apps.accounts.models import User
from apps.academic.models import AnoLetivo, Bimestre, Matricula, Nota, Turma, VinculoResponsavel

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]


def test_cria_contas_de_todos_os_perfis_com_responsavel_para_cada_aluno():
    call_command('criar_dados_demo')

    perfis = set(User.objects.values_list('role', flat=True))
    assert perfis == {'secretaria', 'direcao', 'professor', 'aluno', 'responsavel'}
    assert not User.objects.exclude(email__endswith='@exemplo.com').exists()
    alunos = User.objects.filter(role='aluno')
    assert Matricula.objects.filter(situacao='ativa').count() == alunos.count() == 18
    assert all(VinculoResponsavel.objects.filter(aluno=a).exists() for a in alunos)
    assert Nota.objects.filter(publicada=True).exists()


def test_nao_roda_duas_vezes():
    call_command('criar_dados_demo')

    with pytest.raises(CommandError):
        call_command('criar_dados_demo')


def test_reaproveita_o_ano_letivo_existente_e_estende_o_4o_bimestre_encerrado():
    hoje = timezone.localdate()
    if hoje < date(hoje.year, 2, 10):
        pytest.skip('O teste precisa de bimestres encerrados antes da data de hoje.')
    ano = AnoLetivo.objects.create(ano=hoje.year, ativo=True)
    inicio = date(hoje.year, 1, 2)
    for numero in range(1, 4):
        Bimestre.objects.create(ano_letivo=ano, numero=numero, inicio=inicio + timedelta(days=10 * (numero - 1)),
                                fim=inicio + timedelta(days=10 * numero - 2))
    Bimestre.objects.create(ano_letivo=ano, numero=4, inicio=inicio + timedelta(days=30), fim=hoje - timedelta(days=1))
    Turma.objects.create(ano_letivo=ano, nome='Segundo A', serie='2', turno='manha')

    call_command('criar_dados_demo')

    assert AnoLetivo.objects.count() == 1
    assert Turma.objects.filter(nome='Segundo A').exists()
    assert Bimestre.objects.get(ano_letivo=ano, numero=4).fim >= hoje
