"""Testes de integração da rotina de retenção e descarte (RF22, RN81 e RN82)."""
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core.files.base import ContentFile
from django.core.management import CommandError, call_command
from django.utils import timezone

from apps.academic.models import AnoLetivo, Disciplina, Turma
from apps.accounts.models import PasswordResetToken, User
from apps.audit.models import AuditLog
from apps.audit.retencao import aplicar_retencao
from apps.communication.models import AnexoTarefa, Aviso, EventoCalendario, Tarefa

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]

AGORA = timezone.now()
HOJE = timezone.localdate()


def envelhecer(modelo, objeto, dias, campo='criado_em'):
    """auto_now_add ignora o valor informado na criação; por isso a data é ajustada depois."""
    modelo.objects.filter(pk=objeto.pk).update(**{campo: AGORA - timedelta(days=dias)})


def test_ca01_log_com_mais_de_6_meses_deixa_de_existir(criar_usuario):
    usuario = criar_usuario('secretaria')
    antigo = AuditLog.objects.create(usuario=usuario, acao='login_sucesso')
    recente = AuditLog.objects.create(usuario=usuario, acao='login_sucesso')
    envelhecer(AuditLog, antigo, 190)
    envelhecer(AuditLog, recente, 170)

    contagem = aplicar_retencao()

    assert contagem['logs_auditoria'] == 1
    assert not AuditLog.objects.filter(pk=antigo.pk).exists()
    assert AuditLog.objects.filter(pk=recente.pk).exists()


def test_exclui_links_de_senha_avisos_e_eventos_vencidos(criar_usuario):
    usuario = criar_usuario('aluno')
    link_velho = PasswordResetToken.objects.create(usuario=usuario)
    link_novo = PasswordResetToken.objects.create(usuario=usuario)
    envelhecer(PasswordResetToken, link_velho, 8)
    aviso_velho = Aviso.objects.create(titulo='Antigo', conteudo='.')
    Aviso.objects.create(titulo='Atual', conteudo='.')
    envelhecer(Aviso, aviso_velho, 370)
    EventoCalendario.objects.create(titulo='Feira antiga', tipo='evento', inicio=HOJE - timedelta(days=400),
                                    fim=HOJE - timedelta(days=380))
    EventoCalendario.objects.create(titulo='Feira atual', tipo='evento', inicio=HOJE, fim=HOJE)

    contagem = aplicar_retencao()

    assert (contagem['links_senha'], contagem['avisos'], contagem['eventos']) == (1, 1, 1)
    assert list(PasswordResetToken.objects.values_list('pk', flat=True)) == [link_novo.pk]
    assert list(Aviso.objects.values_list('titulo', flat=True)) == ['Atual']
    assert list(EventoCalendario.objects.values_list('titulo', flat=True)) == ['Feira atual']


def test_exclui_tarefa_vencida_ha_1_ano_com_o_arquivo_do_anexo(criar_usuario, django_capture_on_commit_callbacks):
    ano = AnoLetivo.objects.create(ano=HOJE.year, ativo=True)
    turma = Turma.objects.create(ano_letivo=ano, nome='3º A', serie='3ª série', turno='manha')
    disciplina = Disciplina.objects.create(turma=turma, nome='Física', carga_horaria=80,
                                           professor=criar_usuario('professor'))
    velha = Tarefa.objects.create(disciplina=disciplina, titulo='Velha', prazo=HOJE - timedelta(days=400))
    Tarefa.objects.create(disciplina=disciplina, titulo='Recente', prazo=HOJE - timedelta(days=30))
    anexo = AnexoTarefa(tarefa=velha, nome_original='lista.pdf', tamanho=8)
    anexo.arquivo.save('lista.pdf', ContentFile(b'%PDF-1.7'))
    armazenamento, nome = anexo.arquivo.storage, anexo.arquivo.name

    with django_capture_on_commit_callbacks(execute=True):
        contagem = aplicar_retencao()

    assert (contagem['tarefas'], contagem['anexos']) == (1, 1)
    assert list(Tarefa.objects.values_list('titulo', flat=True)) == ['Recente']
    assert not armazenamento.exists(nome)


def test_anonimiza_conta_desligada_ha_mais_de_1_ano_e_apaga_o_email_dos_logs(criar_usuario):
    antiga = criar_usuario('responsavel', email='marta@exemplo.com', first_name='Marta', last_name='Lima')
    recente = criar_usuario('responsavel', email='joao@exemplo.com')
    for usuario in (antiga, recente):
        usuario.is_active = False
        usuario.save(update_fields=['is_active'])
    User.objects.filter(pk=antiga.pk).update(desativado_em=AGORA - timedelta(days=400))
    AuditLog.objects.create(acao='login_falha', detalhes='E-mail informado: marta@exemplo.com')

    contagem = aplicar_retencao()

    antiga.refresh_from_db()
    recente.refresh_from_db()
    assert contagem['contas_anonimizadas'] == 1
    assert antiga.get_full_name() == 'Usuário removido'
    assert antiga.email == f'removido-{antiga.pk}@anonimizado.invalid'
    assert not antiga.has_usable_password() and antiga.anonimizado_em is not None
    assert recente.email == 'joao@exemplo.com' and recente.anonimizado_em is None
    assert AuditLog.objects.get(acao='login_falha').detalhes == 'E-mail informado: [e-mail removido]'


def test_desativar_conta_guarda_a_data_e_reativar_limpa(criar_usuario):
    usuario = criar_usuario('aluno')
    assert usuario.desativado_em is None

    usuario.is_active = False
    usuario.save(update_fields=['is_active'])
    usuario.refresh_from_db()
    assert usuario.desativado_em is not None

    usuario.is_active = True
    usuario.save()
    usuario.refresh_from_db()
    assert usuario.desativado_em is None


def test_rn82_registra_a_execucao_so_com_quantidades(criar_usuario):
    antigo = AuditLog.objects.create(usuario=criar_usuario('aluno', email='ana@exemplo.com'), acao='login_sucesso')
    envelhecer(AuditLog, antigo, 200)

    call_command('aplicar_retencao')

    registro = AuditLog.objects.get(acao='retencao_executada')
    assert registro.usuario is None
    assert 'logs_auditoria=1' in registro.detalhes
    assert '@' not in registro.detalhes


def test_erro_desfaz_tudo_e_registra_a_falha(criar_usuario):
    antigo = AuditLog.objects.create(usuario=criar_usuario('aluno'), acao='login_sucesso')
    envelhecer(AuditLog, antigo, 200)
    desligada = criar_usuario('responsavel', is_active=False)
    User.objects.filter(pk=desligada.pk).update(desativado_em=AGORA - timedelta(days=400))

    with patch('apps.audit.retencao.anonimizar_conta', side_effect=RuntimeError('disco cheio')), \
            pytest.raises(CommandError):
        call_command('aplicar_retencao')

    assert AuditLog.objects.filter(pk=antigo.pk).exists()
    assert AuditLog.objects.get(acao='retencao_falha').detalhes == 'erro: RuntimeError'
