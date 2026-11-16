"""Rotinas diárias disparadas pelo agendador da hospedagem (RF22 e RF08).

O agendador roda em um contêiner separado, que não tem acesso ao disco onde ficam os anexos das
tarefas. Por isso ele apenas chama este endereço, e o trabalho acontece no serviço principal.
"""
import hmac

from django.conf import settings
from django.http import Http404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .retencao import aplicar_retencao


def token_valido(recebido):
    esperado = settings.ROTINAS_TOKEN
    return bool(esperado) and hmac.compare_digest(recebido.encode(), esperado.encode())


class RotinasDiariasView(APIView):
    """Responde 404 a quem não envia a chave certa, para não revelar que o endereço existe."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        if not token_valido(request.headers.get('X-Rotinas-Token', '')):
            raise Http404
        from apps.communication.models import Aviso
        from apps.communication.notificacoes import notificar_aviso

        retencao = aplicar_retencao()
        pendentes = Aviso.objects.vigentes().filter(notificar_email=True, notificado_em__isnull=True)
        avisos = sum(1 for aviso in pendentes if notificar_aviso(aviso))
        return Response({'retencao': retencao, 'avisos_notificados': avisos})
