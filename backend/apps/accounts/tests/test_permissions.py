"""Testes unitários da permissão PodeGerenciarAviso (RN36 e RN37).

Usuário, requisição e aviso são objetos simples em memória: a regra de acesso
é verificada sem banco e sem subir a API.
"""
from types import SimpleNamespace

from apps.accounts.permissions import PodeGerenciarAviso


def requisicao(role, user_id=1, autenticado=True):
    usuario = SimpleNamespace(id=user_id, role=role, is_authenticated=autenticado)
    return SimpleNamespace(user=usuario)


def aviso(autor_id):
    return SimpleNamespace(autor_id=autor_id)


def test_deve_permitir_que_o_professor_gerencie_o_proprio_aviso():
    permissao = PodeGerenciarAviso()
    request = requisicao('professor', user_id=7)

    pode = permissao.has_object_permission(request, None, aviso(autor_id=7))

    assert pode is True


def test_deve_negar_que_o_professor_gerencie_aviso_de_outro_autor():
    permissao = PodeGerenciarAviso()
    request = requisicao('professor', user_id=7)

    pode = permissao.has_object_permission(request, None, aviso(autor_id=8))

    assert pode is False


def test_deve_negar_publicacao_de_aviso_para_o_perfil_aluno():
    permissao = PodeGerenciarAviso()
    request = requisicao('aluno')

    pode = permissao.has_permission(request, None)

    assert pode is False


def test_deve_permitir_que_a_secretaria_gerencie_aviso_de_qualquer_autor():
    permissao = PodeGerenciarAviso()
    request = requisicao('secretaria', user_id=2)

    pode = permissao.has_object_permission(request, None, aviso(autor_id=7))

    assert pode is True


def test_deve_negar_que_o_professor_gerencie_aviso_cujo_autor_foi_removido():
    permissao = PodeGerenciarAviso()
    request = requisicao('professor', user_id=7)

    pode = permissao.has_object_permission(request, None, aviso(autor_id=None))

    assert pode is False
