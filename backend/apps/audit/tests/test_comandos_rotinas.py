"""Testes unitários dos comandos das rotinas diárias (RF22): o disparo pelo agendador da hospedagem
e a aplicação da retenção, sem banco de dados e sem rede."""
import io
import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import CommandError, call_command
from django.test import override_settings

from apps.audit.retencao import apagar_arquivos, descrever

URL = 'https://api.exemplo.com/api/v1/rotinas/diarias/'
CHAVE = 'chave-de-teste-com-tamanho-suficiente-123'


def resposta_http(corpo):
    resposta = MagicMock()
    resposta.read.return_value = json.dumps(corpo).encode()
    resposta.__enter__.return_value = resposta
    return resposta


@override_settings(ROTINAS_TOKEN=CHAVE)
def test_o_disparo_envia_a_chave_no_cabecalho_e_mostra_o_resultado(monkeypatch):
    monkeypatch.setenv('ROTINAS_URL', URL)
    saida = io.StringIO()

    with patch('urllib.request.urlopen', return_value=resposta_http({'avisos_notificados': 2})) as abrir:
        call_command('disparar_rotinas', stdout=saida)

    pedido = abrir.call_args.args[0]
    assert pedido.full_url == URL
    assert pedido.get_method() == 'POST'
    assert pedido.get_header('X-rotinas-token') == CHAVE
    assert abrir.call_args.kwargs['timeout'] == 300
    assert "Rotinas executadas: {'avisos_notificados': 2}" in saida.getvalue()


@override_settings(ROTINAS_TOKEN='')
def test_o_disparo_exige_o_endereco_e_a_chave(monkeypatch):
    monkeypatch.setenv('ROTINAS_URL', URL)

    with patch('urllib.request.urlopen') as abrir, pytest.raises(CommandError, match='ROTINAS_URL e ROTINAS_TOKEN'):
        call_command('disparar_rotinas')
    abrir.assert_not_called()


@override_settings(ROTINAS_TOKEN=CHAVE)
def test_o_disparo_sem_endereco_nao_tenta_conectar(monkeypatch):
    monkeypatch.delenv('ROTINAS_URL', raising=False)

    with patch('urllib.request.urlopen') as abrir, pytest.raises(CommandError):
        call_command('disparar_rotinas')
    abrir.assert_not_called()


@override_settings(ROTINAS_TOKEN=CHAVE)
@pytest.mark.parametrize('falha', [urllib.error.URLError('Connection refused'), TimeoutError('timed out')])
def test_uma_falha_de_conexao_faz_o_agendador_registrar_erro(monkeypatch, falha):
    monkeypatch.setenv('ROTINAS_URL', URL)

    with patch('urllib.request.urlopen', side_effect=falha), pytest.raises(CommandError, match='não foram executadas'):
        call_command('disparar_rotinas')


def test_o_comando_de_retencao_mostra_o_que_foi_descartado():
    saida = io.StringIO()

    with patch('apps.audit.management.commands.aplicar_retencao.aplicar_retencao',
               return_value={'logs_auditoria': 3, 'contas_anonimizadas': 1}):
        call_command('aplicar_retencao', stdout=saida)

    assert 'Retenção aplicada: logs_auditoria=3, contas_anonimizadas=1.' in saida.getvalue()


def test_uma_falha_na_retencao_e_informada_sem_expor_detalhes():
    with (
        patch('apps.audit.management.commands.aplicar_retencao.aplicar_retencao',
              side_effect=ValueError('dado pessoal que não pode aparecer')),
        pytest.raises(CommandError) as erro,
    ):
        call_command('aplicar_retencao')

    assert 'ValueError' in str(erro.value)
    assert 'dado pessoal' not in str(erro.value)


def test_deve_descrever_a_contagem_da_retencao():
    assert descrever({'tarefas': 2, 'eventos': 0}) == 'tarefas=2, eventos=0'
    assert descrever({}) == ''


def test_deve_apagar_do_disco_cada_anexo_informado():
    from apps.communication.models import AnexoTarefa

    armazenamento = AnexoTarefa._meta.get_field('arquivo').storage
    with patch.object(armazenamento, 'delete') as apagar:
        apagar_arquivos(['tarefas/1/a.pdf', 'tarefas/1/b.png'])

    assert [c.args[0] for c in apagar.call_args_list] == ['tarefas/1/a.pdf', 'tarefas/1/b.png']
