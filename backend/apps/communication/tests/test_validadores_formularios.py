"""Testes unitários dos validadores dos formulários (RNF07): mural, tarefas, calendário, turmas e disciplinas.
Chamam os validadores diretamente, sem banco de dados."""
from datetime import date, timedelta
from types import SimpleNamespace

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.academic.serializers import DisciplinaSerializer, TurmaSerializer
from apps.accounts.models import User
from apps.communication.serializers import (
    AvisoSerializer,
    EventoCalendarioSerializer,
    TarefaSerializer,
    nome_do_autor,
    texto_obrigatorio,
)

PDF = b'%PDF-1.7\n'


def mensagens(erro):
    return str(erro.value.detail)


@pytest.mark.parametrize('texto', ['', '   ', '\n\t'])
def test_titulo_e_conteudo_em_branco_sao_recusados(texto):
    with pytest.raises(ValidationError, match='O título não pode ser vazio.'):
        texto_obrigatorio(texto, 'O título não pode ser vazio.')
    with pytest.raises(ValidationError, match='O conteúdo não pode ser vazio.'):
        AvisoSerializer().validate_conteudo(texto)


def test_texto_preenchido_e_mantido_como_foi_digitado():
    assert texto_obrigatorio('  Prova de Matemática ', 'erro') == '  Prova de Matemática '
    assert EventoCalendarioSerializer().validate_titulo('Feriado') == 'Feriado'


def test_o_nome_do_autor_usa_o_nome_completo_ou_o_usuario():
    assert nome_do_autor(None) is None
    assert nome_do_autor(SimpleNamespace(get_full_name=lambda: 'Paulo Mendes', username='prof.paulo')) == 'Paulo Mendes'
    assert nome_do_autor(SimpleNamespace(get_full_name=lambda: '', username='prof.paulo')) == 'prof.paulo'


def test_aviso_com_fim_antes_do_inicio_e_recusado():
    hoje = timezone.localdate()

    with pytest.raises(ValidationError) as erro:
        AvisoSerializer().validate({'inicio_exibicao': hoje, 'fim_exibicao': hoje - timedelta(days=1)})

    assert 'A data de fim deve ser igual ou posterior à data de início.' in mensagens(erro)


def test_aviso_de_um_dia_so_e_aceito():
    hoje = timezone.localdate()
    dados = {'inicio_exibicao': hoje, 'fim_exibicao': hoje}

    assert AvisoSerializer().validate(dados) == dados


def test_prazo_da_tarefa_nao_pode_ser_anterior_a_hoje():
    serializer = TarefaSerializer()
    hoje = timezone.localdate()

    assert serializer.validate_prazo(hoje) == hoje
    with pytest.raises(ValidationError, match='anterior a hoje'):
        serializer.validate_prazo(hoje - timedelta(days=1))


def test_professor_so_publica_tarefa_nas_proprias_disciplinas():
    request = SimpleNamespace(user=SimpleNamespace(id=10))
    serializer = TarefaSerializer(context={'request': request})
    propria = SimpleNamespace(professor_id=10)
    de_outro = SimpleNamespace(professor_id=11)

    assert serializer.validate_disciplina(propria) is propria
    with pytest.raises(ValidationError, match='disciplinas atribuídas a você'):
        serializer.validate_disciplina(de_outro)


def test_anexos_validos_sao_aceitos_e_lidos_desde_o_inicio():
    arquivo = SimpleUploadedFile('lista.pdf', PDF + b'conteudo', content_type='application/pdf')

    aceitos = TarefaSerializer().validate_arquivos([arquivo])

    assert aceitos == [arquivo]
    assert arquivo.tell() == 0


def test_anexo_com_extensao_proibida_e_recusado_com_o_nome_do_arquivo():
    valido = SimpleUploadedFile('lista.pdf', PDF, content_type='application/pdf')
    proibido = SimpleUploadedFile('script.exe', b'MZ\x90\x00', content_type='application/octet-stream')

    with pytest.raises(ValidationError) as erro:
        TarefaSerializer().validate_arquivos([valido, proibido])

    assert 'script.exe' in mensagens(erro)
    assert 'lista.pdf' not in mensagens(erro)


def test_evento_com_termino_antes_do_inicio_e_recusado():
    with pytest.raises(ValidationError) as erro:
        EventoCalendarioSerializer().validate({'inicio': date(2026, 11, 20), 'fim': date(2026, 11, 19)})

    assert 'fim' in erro.value.detail


def test_evento_de_um_dia_e_aceito():
    dados = {'inicio': date(2026, 11, 20), 'fim': date(2026, 11, 20)}

    assert EventoCalendarioSerializer().validate(dados) == dados


def test_nomes_de_turma_e_de_disciplina_sao_aparados_e_nao_podem_ficar_vazios():
    assert TurmaSerializer().validate_nome('  3º A ') == '3º A'
    assert DisciplinaSerializer().validate_nome(' Matemática  ') == 'Matemática'
    with pytest.raises(ValidationError, match='nome da turma'):
        TurmaSerializer().validate_nome('   ')
    with pytest.raises(ValidationError, match='nome da disciplina'):
        DisciplinaSerializer().validate_nome('')


def test_carga_horaria_precisa_ter_ao_menos_uma_aula():
    assert DisciplinaSerializer().validate_carga_horaria(1) == 1
    with pytest.raises(ValidationError, match='pelo menos 1 aula'):
        DisciplinaSerializer().validate_carga_horaria(0)


@pytest.mark.parametrize(('role', 'ativo'), [('aluno', True), ('secretaria', True), ('professor', False)])
def test_disciplina_so_aceita_professor_com_conta_ativa(role, ativo):
    with pytest.raises(ValidationError, match='professor ativa'):
        DisciplinaSerializer().validate_professor(User(role=role, is_active=ativo))


def test_disciplina_aceita_professor_ativo():
    professor = User(role='professor', is_active=True)

    assert DisciplinaSerializer().validate_professor(professor) is professor
