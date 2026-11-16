"""Exclui ou anonimiza os dados com prazo de guarda vencido (RF22). Executar uma vez por dia."""
from django.core.management.base import BaseCommand, CommandError

from apps.audit.retencao import aplicar_retencao, descrever


class Command(BaseCommand):
    help = 'Aplica o Plano de Retenção e Descarte de Dados: exclui ou anonimiza os registros vencidos.'

    def handle(self, *args, **options):
        try:
            contagem = aplicar_retencao()
        except Exception as erro:
            raise CommandError(f'A retenção falhou e nada foi alterado: {erro.__class__.__name__}') from erro
        self.stdout.write(self.style.SUCCESS(f'Retenção aplicada: {descrever(contagem)}.'))
