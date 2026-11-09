"""Geração do boletim em PDF (RF18) com ReportLab.

RN72: o arquivo é montado em memória a cada pedido e nunca é gravado no servidor.
"""
from io import BytesIO
from xml.sax.saxutils import escape

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

VERDE = colors.HexColor('#1F4B43')
VERMELHO = colors.HexColor('#C0392B')


def _numero(valor, sufixo=''):
    if valor is None:
        return '—'
    return f'{valor:.1f}'.replace('.', ',') + sufixo


def gerar_boletim_pdf(boletim):
    """Recebe o dicionário de servicos.boletim_da_matricula e devolve os bytes do PDF."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                            title=f'Boletim {boletim["ano"]} - {boletim["aluno"]["nome"]}', author='EducaPortal')
    estilos = getSampleStyleSheet()
    titulo = estilos['Title'].clone('titulo', textColor=VERDE)
    texto = estilos['Normal']

    cabecalho = ['Disciplina', '1º bim.', '2º bim.', '3º bim.', '4º bim.', 'Média', 'Aulas', 'Faltas', 'Frequência']
    linhas = [cabecalho]
    destaques = []
    for i, d in enumerate(boletim['disciplinas'], start=1):
        media = _numero(d['media']) + (' (parcial)' if d['media_parcial'] else '')
        linhas.append([
            d['disciplina'], *(_numero(d['notas'][str(b)]) for b in range(1, 5)),
            media, str(d['aulas']), str(d['faltas']), _numero(d['frequencia'], '%'),
        ])
        if d['abaixo_media']:
            destaques.append(('TEXTCOLOR', (5, i), (5, i), VERMELHO))
        if d['abaixo_frequencia']:
            destaques.append(('TEXTCOLOR', (8, i), (8, i), VERMELHO))
        for b in range(1, 5):
            nota = d['notas'][str(b)]
            if nota is not None and nota < 6:
                destaques.append(('TEXTCOLOR', (b, i), (b, i), VERMELHO))

    tabela = Table(linhas, colWidths=[7 * cm, 2 * cm, 2 * cm, 2 * cm, 2 * cm, 3.2 * cm, 1.8 * cm, 1.8 * cm, 2.6 * cm],
                   repeatRows=1)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), VERDE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BBBBBB')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F6F5')]),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        *destaques,
    ]))

    gerado = timezone.localtime().strftime('%d/%m/%Y às %H:%M')
    conteudo = [
        Paragraph('EducaPortal – Boletim escolar', titulo),
        Paragraph(f'<b>Aluno:</b> {escape(boletim["aluno"]["nome"])} &nbsp;&nbsp; <b>Turma:</b> {escape(boletim["turma"])} '
                  f'&nbsp;&nbsp; <b>Ano letivo:</b> {boletim["ano"]}', texto),
        Spacer(1, 0.4 * cm),
        tabela,
        Spacer(1, 0.4 * cm),
        Paragraph('Média mínima 6,0 e frequência mínima de 75% (LDB, art. 24, VI); valores abaixo do mínimo aparecem '
                  'em vermelho. Constam apenas as notas publicadas pelos professores. Médias de ano em andamento são '
                  'parciais.', texto),
        Paragraph(f'Documento gerado em {gerado}. Este boletim não substitui os documentos oficiais da escola.', texto),
    ]
    doc.build(conteudo)
    return buffer.getvalue()
