"""Testes unitários do IP gravado no log quando o sistema está atrás do proxy da hospedagem."""
from django.conf import settings
from django.test import RequestFactory, override_settings

from apps.audit.utils import ip_do_cliente


def requisicao(remote='10.0.0.5', encaminhado=None):
    extras = {'REMOTE_ADDR': remote}
    if encaminhado is not None:
        extras['HTTP_X_FORWARDED_FOR'] = encaminhado
    return RequestFactory().get('/', **extras)


def com_proxies(quantidade):
    return override_settings(REST_FRAMEWORK={**settings.REST_FRAMEWORK, 'NUM_PROXIES': quantidade})


def test_sem_proxy_configurado_usa_o_endereco_da_conexao():
    with com_proxies(None):
        assert ip_do_cliente(requisicao(encaminhado='200.1.2.3')) == '10.0.0.5'


def test_com_um_proxy_usa_o_endereco_acrescentado_por_ele():
    with com_proxies(1):
        assert ip_do_cliente(requisicao(encaminhado='200.1.2.3')) == '200.1.2.3'


def test_ignora_endereco_forjado_pelo_cliente_no_inicio_da_lista():
    with com_proxies(1):
        assert ip_do_cliente(requisicao(encaminhado='1.1.1.1, 200.1.2.3')) == '200.1.2.3'


def test_valor_invalido_no_cabecalho_nao_e_gravado():
    with com_proxies(1):
        assert ip_do_cliente(requisicao(encaminhado='nao-e-ip')) is None


def test_sem_requisicao_nao_ha_ip():
    assert ip_do_cliente(None) is None
