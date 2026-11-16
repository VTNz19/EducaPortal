"""Testes de integração do calendário escolar (RF20, RN77 e RN78)."""
from datetime import date

import pytest
from django.utils import timezone

from apps.academic.models import AnoLetivo, Disciplina, Matricula, Turma, VinculoResponsavel
from apps.audit.models import AuditLog
from apps.communication.models import EventoCalendario

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]

ANO = timezone.localdate().year
URL = '/api/v1/eventos/'


@pytest.fixture
def escola(criar_usuario):
    ano = AnoLetivo.objects.create(ano=ANO, ativo=True)
    t3a = Turma.objects.create(ano_letivo=ano, nome='3º A', serie='3ª série', turno='manha')
    t3b = Turma.objects.create(ano_letivo=ano, nome='3º B', serie='3ª série', turno='tarde')
    carla = criar_usuario('professor', email='carla@exemplo.com')
    Disciplina.objects.create(turma=t3a, nome='Matemática', carga_horaria=160, professor=carla)
    ana = criar_usuario('aluno', email='ana@exemplo.com')
    leo = criar_usuario('aluno', email='leo@exemplo.com')
    Matricula.objects.create(aluno=ana, turma=t3a)
    Matricula.objects.create(aluno=leo, turma=t3b)
    rita = criar_usuario('responsavel', email='rita@exemplo.com')
    VinculoResponsavel.objects.create(responsavel=rita, aluno=ana)
    return {'t3a': t3a, 'carla': carla, 'ana': ana, 'leo': leo, 'rita': rita,
            'secretaria': criar_usuario('secretaria')}


def evento(**extras):
    return {'titulo': 'Feriado da Proclamação', 'tipo': 'feriado', 'inicio': f'{ANO}-11-15',
            'fim': f'{ANO}-11-15', **extras}


def test_gestor_cadastra_evento_e_todos_veem(escola, cliente_autenticado):
    response = cliente_autenticado(escola['secretaria']).post(URL, evento(), format='json')

    assert response.status_code == 201
    assert response.json()['tipo_nome'] == 'Feriado'
    assert AuditLog.objects.filter(acao='evento_criado', usuario=escola['secretaria']).exists()
    for perfil in ('ana', 'leo', 'rita', 'carla'):
        assert [e['titulo'] for e in cliente_autenticado(escola[perfil]).get(URL).json()] == [
            'Feriado da Proclamação']


def test_ca01_recusa_termino_anterior_ao_inicio(escola, cliente_autenticado):
    response = cliente_autenticado(escola['secretaria']).post(
        URL, evento(inicio=f'{ANO}-11-20', fim=f'{ANO}-11-19'), format='json')

    assert response.status_code == 400
    assert response.json() == {'fim': ['A data de término não pode ser anterior à data de início.']}
    assert not EventoCalendario.objects.exists()


def test_ca02_evento_do_3a_nao_aparece_para_aluno_do_3b(escola, cliente_autenticado):
    cliente_autenticado(escola['secretaria']).post(
        URL, evento(titulo='Prova de Matemática', tipo='prova', turma=escola['t3a'].id), format='json')

    def titulos(usuario):
        return [e['titulo'] for e in cliente_autenticado(usuario).get(URL).json()]

    assert titulos(escola['ana']) == ['Prova de Matemática']
    assert titulos(escola['rita']) == ['Prova de Matemática']
    assert titulos(escola['carla']) == ['Prova de Matemática']
    assert titulos(escola['leo']) == []


@pytest.mark.parametrize('perfil', ['carla', 'ana', 'rita'])
def test_somente_gestores_cadastram_eventos(escola, cliente_autenticado, perfil):
    assert cliente_autenticado(escola[perfil]).post(URL, evento(), format='json').status_code == 403


def test_filtra_por_mes_incluindo_eventos_que_atravessam_o_mes(escola, cliente_autenticado):
    EventoCalendario.objects.create(titulo='Recesso', tipo='feriado', inicio=date(ANO, 12, 21),
                                    fim=date(ANO + 1, 1, 31))
    EventoCalendario.objects.create(titulo='Reunião de pais', tipo='reuniao', inicio=date(ANO, 11, 21),
                                    fim=date(ANO, 11, 21))
    client = cliente_autenticado(escola['ana'])

    assert [e['titulo'] for e in client.get(URL, {'mes': f'{ANO}-11'}).json()] == ['Reunião de pais']
    assert [e['titulo'] for e in client.get(URL, {'mes': f'{ANO + 1}-01'}).json()] == ['Recesso']
    assert client.get(URL, {'mes': 'novembro'}).status_code == 400


def test_gestor_edita_e_exclui_evento(escola, cliente_autenticado):
    client = cliente_autenticado(escola['secretaria'])
    criado = client.post(URL, evento(), format='json').json()

    editado = client.patch(f'{URL}{criado["id"]}/', {'fim': f'{ANO}-11-16'}, format='json')
    assert editado.status_code == 200 and editado.json()['fim'] == f'{ANO}-11-16'
    assert client.patch(f'{URL}{criado["id"]}/', {'fim': f'{ANO}-11-01'}, format='json').status_code == 400

    assert client.delete(f'{URL}{criado["id"]}/').status_code == 204
    assert set(AuditLog.objects.values_list('acao', flat=True)) == {'evento_criado', 'evento_editado',
                                                                     'evento_excluido'}
