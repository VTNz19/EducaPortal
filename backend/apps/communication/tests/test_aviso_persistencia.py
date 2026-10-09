"""Testes de integração da persistência de avisos no banco de teste."""
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.communication.models import Aviso

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]


def test_deve_listar_avisos_fixados_primeiro_e_depois_os_mais_recentes(criar_usuario, cliente_autenticado):
    # Arrange: datas fixadas para a ordem não depender da velocidade do teste
    agora = timezone.now()
    antigo_fixado = Aviso.objects.create(titulo='Calendário do bimestre', conteudo='.', fixado=True)
    recente = Aviso.objects.create(titulo='Reunião de pais', conteudo='.')
    antigo = Aviso.objects.create(titulo='Passeio', conteudo='.')
    Aviso.objects.filter(id=antigo_fixado.id).update(criado_em=agora - timedelta(days=10))
    Aviso.objects.filter(id=recente.id).update(criado_em=agora - timedelta(days=1))
    Aviso.objects.filter(id=antigo.id).update(criado_em=agora - timedelta(days=5))
    client = cliente_autenticado(criar_usuario('aluno'))

    # Act
    response = client.get('/api/v1/avisos/')

    # Assert
    assert response.status_code == 200
    titulos = [aviso['titulo'] for aviso in response.json()['results']]
    assert titulos == ['Calendário do bimestre', 'Reunião de pais', 'Passeio']


def test_deve_manter_o_aviso_sem_autor_quando_a_conta_do_autor_e_excluida(criar_usuario):
    # Arrange
    professor = criar_usuario('professor')
    aviso = Aviso.objects.create(titulo='Horário de aulas', conteudo='Novo horário.', autor=professor)

    # Act
    professor.delete()

    # Assert
    aviso.refresh_from_db()
    assert aviso.autor is None
    assert aviso.titulo == 'Horário de aulas'
