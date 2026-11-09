"""Teste de integração do fluxo completo do Mural de Avisos.

Atravessa todas as camadas sem mocks: login real com JWT, aceite do termo,
criação, listagem e exclusão do aviso, conferindo o banco e a auditoria.
"""
import pytest
from django.conf import settings

from apps.audit.models import AuditLog
from apps.communication.models import Aviso
from conftest import SENHA_PADRAO

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]


def test_fluxo_completo_de_login_aceite_do_termo_publicacao_e_exclusao_de_aviso(api_client, criar_usuario):
    professor = criar_usuario('professor', email='carla@exemplo.com', aceitou_termos=False)

    login = api_client.post('/api/v1/auth/login/', {'email': 'carla@exemplo.com', 'password': SENHA_PADRAO}, format='json')
    assert login.status_code == 200
    assert login.json()['role'] == 'professor'
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.json()['access']}")

    assert api_client.get('/api/v1/avisos/').status_code == 403

    aceite = api_client.post('/api/v1/auth/aceitar-termos/', {'versao': settings.VERSAO_TERMOS}, format='json')
    assert aceite.status_code == 200
    assert aceite.json()['precisa_aceitar_termos'] is False

    criado = api_client.post('/api/v1/avisos/', {'titulo': 'Entrega do trabalho', 'conteudo': 'Até sexta.'}, format='json')
    assert criado.status_code == 201
    aviso_id = criado.json()['id']

    lista = api_client.get('/api/v1/avisos/')
    assert [aviso['id'] for aviso in lista.json()['results']] == [aviso_id]

    exclusao = api_client.delete(f'/api/v1/avisos/{aviso_id}/')

    assert exclusao.status_code == 204
    assert not Aviso.objects.filter(id=aviso_id).exists()
    acoes = list(AuditLog.objects.filter(usuario=professor).order_by('id').values_list('acao', flat=True))
    assert acoes == ['login_sucesso', 'termos_aceitos', 'aviso_criado', 'aviso_excluido']
    professor.refresh_from_db()
    assert professor.termos_versao_aceita == settings.VERSAO_TERMOS
