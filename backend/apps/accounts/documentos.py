"""Versões do Termo de Uso e da Política de Privacidade publicadas pela Direção (RF23).

Enquanto a Direção não publica nenhuma versão pelo portal, valem os textos de docs/*.md, com as versões
definidas em settings (VERSAO_TERMOS e VERSAO_POLITICA). O aceite do usuário guarda as duas versões
juntas: publicar uma nova versão de qualquer um dos documentos exige novo aceite de todos.
"""
import re

from django.conf import settings
from django.db import transaction

from .models import DocumentoLegal

TIPOS = DocumentoLegal.Tipo


def versao_inicial(tipo):
    return settings.VERSAO_TERMOS if tipo == TIPOS.TERMO else settings.VERSAO_POLITICA


def documento_vigente(tipo):
    return DocumentoLegal.objects.filter(tipo=tipo).order_by('-publicado_em', '-id').first()


def versao_de(tipo):
    documento = documento_vigente(tipo)
    return documento.versao if documento else versao_inicial(tipo)


def versao_vigente():
    """Identifica o par de documentos em vigor, por exemplo "2.2+2.1" (termo + política)."""
    return f'{versao_de(TIPOS.TERMO)}+{versao_de(TIPOS.POLITICA)}'


def descrever_versao(versao):
    termo, _, politica = versao.partition('+')
    return f'Termo de Uso e Aceite {termo} e Política de Privacidade {politica}'


def proxima_versao(versao):
    """Sobe o último número da versão: 2.2 -> 2.3, 2.9 -> 2.10. Uma versão fora do padrão vira X.1."""
    partes = versao.split('.')
    if not all(re.fullmatch(r'\d+', p) for p in partes):
        return f'{versao}.1'
    partes[-1] = str(int(partes[-1]) + 1)
    return '.'.join(partes)


@transaction.atomic
def publicar(tipo, conteudo, resumo, autor):
    # trava as versões do tipo para que duas publicações simultâneas não gerem o mesmo número
    list(DocumentoLegal.objects.select_for_update().filter(tipo=tipo).values_list('id', flat=True))
    return DocumentoLegal.objects.create(
        tipo=tipo, versao=proxima_versao(versao_de(tipo)), conteudo=conteudo, resumo=resumo, publicado_por=autor,
    )
