"""Envia o e-mail dos avisos cuja exibição começou hoje (RF08). Executar uma vez por dia."""
from django.core.management.base import BaseCommand

from apps.communication.models import Aviso
from apps.communication.notificacoes import notificar_aviso


class Command(BaseCommand):
    help = 'Envia por e-mail os avisos agendados cujo período de exibição já começou.'

    def handle(self, *args, **options):
        pendentes = Aviso.objects.vigentes().filter(notificar_email=True, notificado_em__isnull=True)
        enviados = sum(1 for aviso in pendentes if notificar_aviso(aviso))
        self.stdout.write(f'{enviados} aviso(s) notificado(s).')
