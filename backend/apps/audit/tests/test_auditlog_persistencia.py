"""Testes de integração do registro de auditoria no banco de teste."""
from types import SimpleNamespace

import pytest

from apps.audit.models import AuditLog
from apps.audit.utils import registrar_log

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]


def test_deve_gravar_log_com_usuario_acao_e_ip_da_requisicao(criar_usuario):
    # Arrange
    usuario = criar_usuario('secretaria')
    request = SimpleNamespace(META={'REMOTE_ADDR': '192.168.0.10'})

    # Act
    registrar_log(usuario, 'usuario_criado', detalhes='usuario id=99', request=request)

    # Assert
    log = AuditLog.objects.get()
    assert log.usuario == usuario
    assert log.acao == 'usuario_criado'
    assert log.detalhes == 'usuario id=99'
    assert log.endereco_ip == '192.168.0.10'


def test_deve_preservar_o_log_quando_o_usuario_e_excluido(criar_usuario):
    # Arrange
    usuario = criar_usuario('professor')
    registrar_log(usuario, 'login_sucesso')

    # Act
    usuario.delete()

    # Assert: o histórico continua, só perde o vínculo com a conta
    log = AuditLog.objects.get(acao='login_sucesso')
    assert log.usuario is None
