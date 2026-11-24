"""Testes unitários das rotas da API: cada endereço aponta para a view e a ação certas, sem banco de dados."""
import pytest
from django.urls import Resolver404, resolve, reverse

from apps.academic.views import AlunoMatriculaViewSet, AnoLetivoViewSet, DisciplinaViewSet, TurmaViewSet
from apps.academic.views_diario import BoletimAlunosView, BoletimPdfView, BoletimView, DiarioViewSet
from apps.academic.views_painel import PainelAlunosView, PainelView
from apps.accounts.views import (
    AceitarTermosView,
    CustomTokenObtainPairView,
    EsqueciSenhaView,
    MeView,
    RedefinirSenhaView,
    UsuarioViewSet,
)
from apps.audit.views import RotinasDiariasView
from apps.communication.views import AvisoViewSet, EventoCalendarioViewSet, TarefaViewSet

ROTAS_SIMPLES = [
    ('/api/v1/auth/login/', CustomTokenObtainPairView),
    ('/api/v1/auth/me/', MeView),
    ('/api/v1/auth/aceitar-termos/', AceitarTermosView),
    ('/api/v1/auth/esqueci-senha/', EsqueciSenhaView),
    ('/api/v1/auth/redefinir-senha/', RedefinirSenhaView),
    ('/api/v1/painel/', PainelView),
    ('/api/v1/painel/disciplinas/3/alunos/', PainelAlunosView),
    ('/api/v1/boletim/alunos/', BoletimAlunosView),
    ('/api/v1/boletim/7/', BoletimView),
    ('/api/v1/boletim/7/pdf/', BoletimPdfView),
    ('/api/v1/rotinas/diarias/', RotinasDiariasView),
]

ROTAS_DE_VIEWSET = [
    ('/api/v1/avisos/', AvisoViewSet, 'get', 'list'),
    ('/api/v1/avisos/', AvisoViewSet, 'post', 'create'),
    ('/api/v1/avisos/1/', AvisoViewSet, 'patch', 'partial_update'),
    ('/api/v1/avisos/1/', AvisoViewSet, 'delete', 'destroy'),
    ('/api/v1/tarefas/', TarefaViewSet, 'post', 'create'),
    ('/api/v1/tarefas/1/anexos/2/', TarefaViewSet, 'get', 'anexo'),
    ('/api/v1/eventos/', EventoCalendarioViewSet, 'get', 'list'),
    ('/api/v1/usuarios/', UsuarioViewSet, 'post', 'create'),
    ('/api/v1/usuarios/1/anonimizar/', UsuarioViewSet, 'post', 'anonimizar'),
    ('/api/v1/usuarios/1/exportar/', UsuarioViewSet, 'get', 'exportar'),
    ('/api/v1/usuarios/1/logs/', UsuarioViewSet, 'get', 'logs'),
    ('/api/v1/anos-letivos/', AnoLetivoViewSet, 'post', 'create'),
    ('/api/v1/turmas/1/', TurmaViewSet, 'delete', 'destroy'),
    ('/api/v1/disciplinas/', DisciplinaViewSet, 'get', 'list'),
    ('/api/v1/alunos/1/transferir/', AlunoMatriculaViewSet, 'post', 'transferir'),
    ('/api/v1/alunos/1/rematricular/', AlunoMatriculaViewSet, 'post', 'rematricular'),
    ('/api/v1/alunos/1/vincular/', AlunoMatriculaViewSet, 'post', 'vincular'),
    ('/api/v1/alunos/1/desvincular/', AlunoMatriculaViewSet, 'post', 'desvincular'),
    ('/api/v1/diario/1/notas/', DiarioViewSet, 'post', 'notas'),
    ('/api/v1/diario/1/publicar-notas/', DiarioViewSet, 'post', 'publicar_notas'),
    ('/api/v1/diario/1/chamada/', DiarioViewSet, 'post', 'chamada'),
]


@pytest.mark.parametrize(('caminho', 'view'), ROTAS_SIMPLES)
def test_deve_ligar_cada_endereco_a_sua_view(caminho, view):
    assert resolve(caminho).func.view_class is view


@pytest.mark.parametrize(('caminho', 'viewset', 'metodo', 'acao'), ROTAS_DE_VIEWSET)
def test_deve_ligar_cada_endereco_e_metodo_a_acao_do_viewset(caminho, viewset, metodo, acao):
    funcao = resolve(caminho).func

    assert funcao.cls is viewset
    assert funcao.actions[metodo] == acao


def test_deve_montar_os_enderecos_com_os_parametros_da_rota():
    assert reverse('boletim-pdf', kwargs={'aluno_id': 5}) == '/api/v1/boletim/5/pdf/'
    assert reverse('painel-alunos', kwargs={'disciplina_id': 2}) == '/api/v1/painel/disciplinas/2/alunos/'
    assert reverse('tarefa-anexo', kwargs={'pk': 1, 'anexo_id': 9}) == '/api/v1/tarefas/1/anexos/9/'


def test_nao_deve_expor_a_listagem_de_alunos_nem_a_do_diario():
    """Matrículas e diário só são acessados por ações específicas: não existe rota de listagem geral."""
    assert 'get' not in resolve('/api/v1/alunos/1/transferir/').func.actions
    with pytest.raises(Resolver404):
        resolve('/api/v1/alunos/')
    with pytest.raises(Resolver404):
        resolve('/api/v1/diario/')
