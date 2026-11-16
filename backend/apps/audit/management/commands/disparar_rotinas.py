"""Chama as rotinas diárias no serviço principal. É o comando do agendador (cron) da hospedagem.

Usa as variáveis ROTINAS_URL (endereço interno do serviço, terminado em /api/v1/rotinas/diarias/)
e ROTINAS_TOKEN (a mesma chave configurada no serviço principal).
"""
import json
import os
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Dispara a retenção de dados e o envio dos avisos agendados no serviço principal.'

    def handle(self, *args, **options):
        url = os.environ.get('ROTINAS_URL', '')
        if not url or not settings.ROTINAS_TOKEN:
            raise CommandError('Defina ROTINAS_URL e ROTINAS_TOKEN.')
        pedido = urllib.request.Request(url, data=b'{}', method='POST', headers={
            'X-Rotinas-Token': settings.ROTINAS_TOKEN, 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(pedido, timeout=300) as resposta:
                resultado = json.loads(resposta.read())
        except (urllib.error.URLError, TimeoutError, ValueError) as erro:
            raise CommandError(f'As rotinas não foram executadas: {erro}') from erro
        self.stdout.write(self.style.SUCCESS(f'Rotinas executadas: {resultado}'))
