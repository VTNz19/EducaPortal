"""Testes de integração da publicação do Termo de Uso e da Política de Privacidade pela Direção (RF23)
e do mascaramento dos e-mails nas telas (RN88)."""
import pytest
from rest_framework.test import APIClient

from apps.accounts.documentos import versao_vigente
from apps.accounts.models import DocumentoLegal
from apps.audit.models import AuditLog

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]

TERMO = '/api/v1/documentos/termo/'
POLITICA = '/api/v1/documentos/politica/'
TEXTO = '# Termo de Uso e Aceite\n\n' + 'Cláusula de teste com texto suficiente para um documento legal. ' * 5


def cliente_de(usuario):
    """Um cliente por pessoa: a fixture cliente_autenticado reaproveita o mesmo objeto."""
    cliente = APIClient()
    cliente.force_authenticate(user=usuario)
    return cliente


def nova_versao(texto=TEXTO, resumo='Inclui a cláusula sobre o uso do calendário escolar.'):
    return {'conteudo': texto, 'resumo': resumo}


def test_qualquer_pessoa_le_o_documento_vigente_mesmo_sem_login(api_client):
    response = api_client.get(TERMO)

    assert response.status_code == 200
    assert response.json()['versao'] == '2.2'
    assert response.json()['conteudo'] is None  # o site usa o texto que acompanha o código


def test_documento_inexistente_responde_404(api_client):
    assert api_client.get('/api/v1/documentos/contrato/').status_code == 404


def test_direcao_publica_nova_versao_e_fica_registrado_no_log(criar_usuario, cliente_autenticado, api_client):
    direcao = criar_usuario('direcao', first_name='Helena', last_name='Barros')

    response = cliente_autenticado(direcao).post(TERMO, nova_versao(), format='json')

    assert response.status_code == 201
    assert response.json()['versao'] == '2.3'
    assert response.json()['publicado_por'] == 'Helena Barros'
    publicado = api_client.get(TERMO).json()
    assert publicado['versao'] == '2.3'
    assert publicado['conteudo'].startswith('# Termo de Uso e Aceite')
    log = AuditLog.objects.get(acao='documento_publicado')
    assert log.usuario == direcao
    assert 'Termo de Uso e Aceite, versão 2.3' in log.detalhes


@pytest.mark.parametrize('papel', ['secretaria', 'professor', 'aluno', 'responsavel'])
def test_somente_a_direcao_publica_documentos(papel, criar_usuario, cliente_autenticado):
    response = cliente_autenticado(criar_usuario(papel)).post(TERMO, nova_versao(), format='json')

    assert response.status_code == 403
    assert not DocumentoLegal.objects.exists()


def test_publicar_sem_login_e_recusado(api_client):
    assert api_client.post(TERMO, nova_versao(), format='json').status_code == 401


def test_nova_versao_exige_novo_aceite_de_todos(criar_usuario):
    direcao = criar_usuario('direcao')
    aluno = criar_usuario('aluno')
    cliente_aluno = cliente_de(aluno)
    assert cliente_aluno.get('/api/v1/avisos/').status_code == 200

    assert cliente_de(direcao).post(POLITICA, nova_versao(), format='json').status_code == 201

    me = cliente_aluno.get('/api/v1/auth/me/').json()
    assert me['precisa_aceitar_termos'] is True
    assert me['versao_termos_atual'] == '2.2+2.2'
    assert cliente_aluno.get('/api/v1/avisos/').status_code == 403
    assert cliente_aluno.post('/api/v1/auth/aceitar-termos/', {'versao': '2.2+2.1'}, format='json').status_code == 400

    aceite = cliente_aluno.post('/api/v1/auth/aceitar-termos/', {'versao': '2.2+2.2'}, format='json')

    assert aceite.status_code == 200
    assert cliente_aluno.get('/api/v1/avisos/').status_code == 200
    assert AuditLog.objects.get(usuario=aluno, acao='termos_aceitos').detalhes == (
        'Termo de Uso e Aceite 2.2 e Política de Privacidade 2.2')


def test_cada_documento_tem_a_propria_numeracao(criar_usuario, cliente_autenticado):
    direcao = cliente_autenticado(criar_usuario('direcao'))

    for url, texto in ((TERMO, TEXTO), (TERMO, TEXTO + 'Nova cláusula.'), (POLITICA, TEXTO)):
        assert direcao.post(url, nova_versao(texto), format='json').status_code == 201
        # quem publicou também precisa aceitar a nova versão antes de continuar usando o sistema
        assert direcao.post(url, nova_versao(texto), format='json').status_code == 403
        direcao.post('/api/v1/auth/aceitar-termos/', {'versao': versao_vigente()}, format='json')

    assert versao_vigente() == '2.4+2.2'


@pytest.mark.parametrize(('dados', 'campo'), [
    ({'conteudo': '', 'resumo': 'Correção'}, 'conteudo'),
    ({'conteudo': 'Texto curto demais.', 'resumo': 'Correção'}, 'conteudo'),
    ({'conteudo': TEXTO, 'resumo': '  '}, 'resumo'),
    ({'conteudo': TEXTO}, 'resumo'),
])
def test_texto_vazio_curto_ou_sem_resumo_e_recusado(dados, campo, criar_usuario, cliente_autenticado):
    response = cliente_autenticado(criar_usuario('direcao')).post(TERMO, dados, format='json')

    assert response.status_code == 400
    assert campo in response.json()
    assert not DocumentoLegal.objects.exists()


def test_publicar_o_mesmo_texto_da_versao_vigente_e_recusado(criar_usuario, cliente_autenticado):
    direcao = cliente_autenticado(criar_usuario('direcao'))
    direcao.post(TERMO, nova_versao(), format='json')
    direcao.post('/api/v1/auth/aceitar-termos/', {'versao': versao_vigente()}, format='json')

    response = direcao.post(TERMO, nova_versao(resumo='Nada mudou'), format='json')

    assert response.status_code == 400
    assert 'igual ao da versão vigente' in str(response.json())
    assert DocumentoLegal.objects.count() == 1


def test_direcao_consulta_o_historico_de_versoes(criar_usuario, cliente_autenticado):
    direcao = cliente_autenticado(criar_usuario('direcao'))
    direcao.post(TERMO, nova_versao(resumo='Primeira revisão'), format='json')
    direcao.post('/api/v1/auth/aceitar-termos/', {'versao': versao_vigente()}, format='json')
    direcao.post(TERMO, nova_versao(TEXTO + 'Mais uma cláusula.', resumo='Segunda revisão'), format='json')
    direcao.post('/api/v1/auth/aceitar-termos/', {'versao': versao_vigente()}, format='json')

    response = direcao.get(TERMO + 'versoes/')

    assert response.status_code == 200
    assert [(v['versao'], v['resumo']) for v in response.json()] == [('2.4', 'Segunda revisão'),
                                                                     ('2.3', 'Primeira revisão')]
    assert 'conteudo' not in response.json()[0]


def test_secretaria_nao_consulta_o_historico_de_versoes(criar_usuario, cliente_autenticado):
    assert cliente_autenticado(criar_usuario('secretaria')).get(TERMO + 'versoes/').status_code == 403


def test_o_titular_ve_o_proprio_e_mail_completo_e_os_demais_mascarados(criar_usuario, cliente_autenticado):
    direcao = criar_usuario('direcao', email='helena.barros@exemplo.com')
    criar_usuario('aluno', email='ana.souza@exemplo.com')
    cliente = cliente_autenticado(direcao)

    me = cliente.get('/api/v1/auth/me/').json()
    proprio_perfil = cliente.get(f'/api/v1/usuarios/{direcao.id}/').json()
    lista = cliente.get('/api/v1/usuarios/').json()['results']

    assert me['email'] == 'helena.barros@exemplo.com'
    assert proprio_perfil['email'] == 'helena.barros@exemplo.com'
    emails = {u['email'] for u in lista}
    assert 'an***@exemplo.com' in emails
    assert 'ana.souza@exemplo.com' not in emails


def test_logs_na_tela_mascaram_e_exportacao_ao_titular_mantem_o_e_mail(criar_usuario, cliente_autenticado):
    direcao = criar_usuario('direcao')
    ana = criar_usuario('aluno', email='ana.souza@exemplo.com')
    AuditLog.objects.create(usuario=ana, acao='login_falha', detalhes='tentativa de login: ana.souza@exemplo.com')
    cliente = cliente_autenticado(direcao)

    logs = cliente.get(f'/api/v1/usuarios/{ana.id}/logs/').json()
    exportacao = cliente.get(f'/api/v1/usuarios/{ana.id}/exportar/').json()

    assert logs[0]['detalhes'] == 'tentativa de login: an***@exemplo.com'
    assert exportacao['usuario']['email'] == 'ana.souza@exemplo.com'
    assert exportacao['logs'][0]['detalhes'] == 'tentativa de login: ana.souza@exemplo.com'
