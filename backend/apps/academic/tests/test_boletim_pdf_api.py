"""Testes de integração do boletim em PDF (RF18, RN71 a RN73)."""
from decimal import Decimal

import pytest

from apps.academic.models import AnoLetivo, Bimestre, Disciplina, Matricula, Nota, Turma
from apps.academic.pdf import gerar_boletim_pdf
from apps.audit.models import AuditLog

pytestmark = [pytest.mark.django_db, pytest.mark.integracao]


@pytest.fixture
def ana_com_nota(criar_usuario):
    ano = AnoLetivo.objects.create(ano=2026, ativo=True)
    bimestre = Bimestre.objects.create(ano_letivo=ano, numero=1, inicio='2026-02-02', fim='2026-04-17')
    turma = Turma.objects.create(ano_letivo=ano, nome='3º A', serie='3ª série', turno='manha')
    disciplina = Disciplina.objects.create(turma=turma, nome='Matemática', carga_horaria=160,
                                           professor=criar_usuario('professor'))
    ana = criar_usuario('aluno', email='ana@exemplo.com', first_name='Ana', last_name='Souza')
    matricula = Matricula.objects.create(aluno=ana, turma=turma)
    Nota.objects.create(matricula=matricula, disciplina=disciplina, bimestre=bimestre, valor=Decimal('5.5'),
                        publicada=True)
    return ana


def test_aluno_baixa_o_proprio_boletim_em_pdf(ana_com_nota, cliente_autenticado):
    response = cliente_autenticado(ana_com_nota).get(f'/api/v1/boletim/{ana_com_nota.id}/pdf/')

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert response['Content-Disposition'] == f'attachment; filename="boletim-2026-{ana_com_nota.id}.pdf"'
    assert response.content.startswith(b'%PDF')
    assert AuditLog.objects.filter(acao='boletim_emitido').exists()


def test_outro_aluno_nao_baixa_o_boletim_em_pdf(ana_com_nota, criar_usuario, cliente_autenticado):
    response = cliente_autenticado(criar_usuario('aluno', email='leo@exemplo.com')).get(
        f'/api/v1/boletim/{ana_com_nota.id}/pdf/')

    assert response.status_code == 403


def test_nao_gera_pdf_sem_notas_publicadas(ana_com_nota, cliente_autenticado):
    Nota.objects.update(publicada=False)

    response = cliente_autenticado(ana_com_nota).get(f'/api/v1/boletim/{ana_com_nota.id}/pdf/')

    assert response.status_code == 400
    assert response.json() == {'detail': 'Ainda não há notas publicadas neste ano letivo.'}


def test_pdf_aceita_nome_com_caracteres_especiais_sem_quebrar():
    boletim = {
        'aluno': {'id': 1, 'nome': 'Ana <Souza> & Cia'}, 'ano': 2026, 'turma': '3º A',
        'disciplinas': [{'disciplina': 'Matemática', 'notas': {'1': 5.5, '2': None, '3': None, '4': None},
                         'media': Decimal('5.5'), 'media_parcial': True, 'abaixo_media': True, 'aulas': 0,
                         'faltas': 0, 'frequencia': None, 'abaixo_frequencia': False}],
    }

    pdf = gerar_boletim_pdf(boletim)

    assert pdf.startswith(b'%PDF')
