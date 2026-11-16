"""Testes de integração do disparo das rotinas diárias pelo agendador da hospedagem."""
import io
import json
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core.management import CommandError, call_command
from django.test import override_settings
from django.utils import timezone

from apps.audit.models import AuditLog

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]

URL = '/api/v1/rotinas/diarias/'
CHAVE = 'chave-de-teste-com-tamanho-suficiente-123'


@override_settings(ROTINAS_TOKEN=CHAVE)
def test_com_a_chave_certa_executa_a_retencao(api_client, criar_usuario):
    antigo = AuditLog.objects.create(usuario=criar_usuario('aluno'), acao='login_sucesso')
    AuditLog.objects.filter(pk=antigo.pk).update(criado_em=timezone.now() - timedelta(days=200))

    response = api_client.post(URL, HTTP_X_ROTINAS_TOKEN=CHAVE)

    assert response.status_code == 200
    assert response.json()['retencao']['logs_auditoria'] == 1
    assert response.json()['avisos_notificados'] == 0
    assert AuditLog.objects.filter(acao='retencao_executada').exists()


@override_settings(ROTINAS_TOKEN=CHAVE)
def test_chave_errada_ou_ausente_responde_404(api_client):
    assert api_client.post(URL, HTTP_X_ROTINAS_TOKEN='errada').status_code == 404
    assert api_client.post(URL).status_code == 404
    assert not AuditLog.objects.filter(acao='retencao_executada').exists()


@override_settings(ROTINAS_TOKEN='')
def test_sem_chave_configurada_o_endereco_fica_desligado(api_client):
    assert api_client.post(URL, HTTP_X_ROTINAS_TOKEN='').status_code == 404


class RespostaFalsa(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


@override_settings(ROTINAS_TOKEN=CHAVE)
def test_comando_do_agendador_chama_o_servico_principal(monkeypatch):
    monkeypatch.setenv('ROTINAS_URL', 'http://api.interna/api/v1/rotinas/diarias/')
    saida = io.StringIO()
    resposta = RespostaFalsa(json.dumps({'avisos_notificados': 0}).encode())
    with patch('urllib.request.urlopen', return_value=resposta) as abrir:
        call_command('disparar_rotinas', stdout=saida)

    pedido = abrir.call_args.args[0]
    assert pedido.full_url == 'http://api.interna/api/v1/rotinas/diarias/'
    assert pedido.get_header('X-rotinas-token') == CHAVE
    assert 'Rotinas executadas' in saida.getvalue()


@override_settings(ROTINAS_TOKEN=CHAVE)
def test_comando_falha_sem_endereco_configurado(monkeypatch):
    monkeypatch.delenv('ROTINAS_URL', raising=False)
    with pytest.raises(CommandError):
        call_command('disparar_rotinas')
