"""Testes de integração da anonimização a pedido do titular (Plano de Retenção, seção 5; art. 18 da LGPD)."""
import pytest
from django.utils import timezone

from apps.academic.models import AnoLetivo, Disciplina, Matricula, Nota, Turma, VinculoResponsavel
from apps.accounts.models import User
from apps.audit.models import AuditLog

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]

CONFIRMAR = {'confirmacao': 'ANONIMIZAR'}


def url(usuario):
    return f'/api/v1/usuarios/{usuario.pk}/anonimizar/'


@pytest.fixture
def escola(criar_usuario):
    ano = AnoLetivo.objects.create(ano=timezone.localdate().year, ativo=True)
    turma = Turma.objects.create(ano_letivo=ano, nome='3º A', serie='3ª série', turno='manha')
    carla = criar_usuario('professor', email='carla@exemplo.com')
    ana = criar_usuario('aluno', email='ana@exemplo.com', first_name='Ana', last_name='Souza')
    rita = criar_usuario('responsavel', email='rita@exemplo.com')
    Matricula.objects.create(aluno=ana, turma=turma)
    VinculoResponsavel.objects.create(responsavel=rita, aluno=ana)
    return {'turma': turma, 'carla': carla, 'ana': ana, 'rita': rita, 'secretaria': criar_usuario('secretaria'),
            'direcao': criar_usuario('direcao')}


def test_secretaria_anonimiza_aluno_e_encerra_matricula_e_vinculos(escola, cliente_autenticado):
    ana = escola['ana']
    AuditLog.objects.create(acao='login_falha', detalhes='E-mail informado: ana@exemplo.com')

    response = cliente_autenticado(escola['secretaria']).post(url(ana), CONFIRMAR, format='json')

    assert response.status_code == 200
    corpo = response.json()
    assert corpo['nome'] == 'Usuário removido'
    assert corpo['email'] == 're***@anonimizado.invalid'
    assert corpo['is_active'] is False and corpo['anonimizado_em']
    ana.refresh_from_db()
    assert ana.email == f'removido-{ana.pk}@anonimizado.invalid'
    assert not ana.has_usable_password()
    assert Matricula.objects.get(aluno=ana).situacao == 'encerrada'
    assert not VinculoResponsavel.objects.filter(aluno=ana).exists()
    assert AuditLog.objects.get(acao='login_falha').detalhes == 'E-mail informado: [e-mail removido]'
    log = AuditLog.objects.get(acao='conta_anonimizada')
    assert log.usuario == escola['secretaria']
    assert log.detalhes == f'usuario id={ana.pk}, a pedido do titular'


def test_notas_continuam_ligadas_ao_registro_anonimo(escola, cliente_autenticado):
    from apps.academic.models import Bimestre

    hoje = timezone.localdate()
    bimestre = Bimestre.objects.create(ano_letivo=escola['turma'].ano_letivo, numero=1, inicio=hoje, fim=hoje)
    disciplina = Disciplina.objects.create(turma=escola['turma'], nome='Física', carga_horaria=80,
                                           professor=escola['carla'])
    Nota.objects.create(matricula=Matricula.objects.get(aluno=escola['ana']), disciplina=disciplina,
                        bimestre=bimestre, valor=8)

    response = cliente_autenticado(escola['direcao']).post(url(escola['ana']), CONFIRMAR, format='json')

    assert response.status_code == 200
    assert Nota.objects.filter(matricula__aluno=escola['ana']).count() == 1


def test_exige_digitar_a_confirmacao(escola, cliente_autenticado):
    response = cliente_autenticado(escola['secretaria']).post(url(escola['ana']), {'confirmacao': 'sim'},
                                                              format='json')

    assert response.status_code == 400
    assert response.json() == {'confirmacao': ['Digite ANONIMIZAR para confirmar.']}
    assert User.objects.get(pk=escola['ana'].pk).anonimizado_em is None


def test_nao_anonimiza_a_propria_conta(escola, cliente_autenticado):
    response = cliente_autenticado(escola['secretaria']).post(url(escola['secretaria']), CONFIRMAR, format='json')

    assert response.status_code == 400
    assert response.json() == {'detail': ['Você não pode anonimizar a própria conta.']}


def test_nao_anonimiza_duas_vezes(escola, cliente_autenticado):
    client = cliente_autenticado(escola['secretaria'])
    assert client.post(url(escola['ana']), CONFIRMAR, format='json').status_code == 200

    response = client.post(url(escola['ana']), CONFIRMAR, format='json')

    assert response.status_code == 400
    assert response.json() == {'detail': ['Esta conta já foi anonimizada.']}


def test_rn85_nao_anonimiza_o_unico_responsavel_de_um_aluno_ativo(escola, criar_usuario, cliente_autenticado):
    client = cliente_autenticado(escola['secretaria'])

    bloqueado = client.post(url(escola['rita']), CONFIRMAR, format='json')
    assert bloqueado.status_code == 400
    assert bloqueado.json() == {'detail': ['Vincule outro responsável a Ana Souza antes de anonimizar (RN85).']}

    joao = criar_usuario('responsavel', email='joao@exemplo.com')
    VinculoResponsavel.objects.create(responsavel=joao, aluno=escola['ana'])
    assert client.post(url(escola['rita']), CONFIRMAR, format='json').status_code == 200
    assert list(VinculoResponsavel.objects.filter(aluno=escola['ana']).values_list('responsavel', flat=True)) == [
        joao.pk]


def test_professor_com_disciplinas_do_ano_atual_nao_e_anonimizado(escola, cliente_autenticado):
    Disciplina.objects.create(turma=escola['turma'], nome='Física', carga_horaria=80, professor=escola['carla'])

    response = cliente_autenticado(escola['secretaria']).post(url(escola['carla']), CONFIRMAR, format='json')

    assert response.status_code == 400
    assert response.json() == {'detail': [
        'Troque o professor das disciplinas do ano letivo atual antes de anonimizar: Física – 3º A.']}


def test_conta_de_administracao_tecnica_nao_e_anonimizada(escola, criar_usuario, cliente_autenticado):
    tecnico = criar_usuario('secretaria', email='tecnico@exemplo.com', is_superuser=True, is_staff=True)

    response = cliente_autenticado(escola['secretaria']).post(url(tecnico), CONFIRMAR, format='json')

    assert response.status_code == 400


@pytest.mark.parametrize('perfil', ['carla', 'ana', 'rita'])
def test_somente_gestores_anonimizam(escola, cliente_autenticado, perfil):
    alvo = escola['rita'] if perfil != 'rita' else escola['carla']

    response = cliente_autenticado(escola[perfil]).post(url(alvo), CONFIRMAR, format='json')

    assert response.status_code == 403


def test_conta_anonimizada_nao_pode_ser_rematriculada(escola, cliente_autenticado):
    client = cliente_autenticado(escola['secretaria'])
    client.post(url(escola['ana']), CONFIRMAR, format='json')

    response = client.post(f'/api/v1/alunos/{escola["ana"].pk}/rematricular/', {'turma': escola['turma'].pk},
                           format='json')

    assert response.status_code == 400
    assert response.json() == {'detail': ['Esta conta foi anonimizada e não pode mais ser alterada.']}
