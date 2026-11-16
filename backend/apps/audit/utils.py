import ipaddress

from django.conf import settings


def ip_do_cliente(request):
    """Endereço IP de quem fez a requisição.

    Atrás de um proxy (como o da hospedagem em nuvem), REMOTE_ADDR é o endereço do proxy. Com
    NUM_PROXIES configurado, o endereço vem do cabeçalho X-Forwarded-For, pela mesma regra que o
    Django REST Framework usa no limite de tentativas: o cliente é o endereço adicionado pelo
    proxy de confiança mais externo, e não o primeiro da lista, que o próprio cliente pode forjar.
    """
    if request is None:
        return None
    endereco = request.META.get('REMOTE_ADDR')
    proxies = settings.REST_FRAMEWORK.get('NUM_PROXIES')
    encaminhado = request.META.get('HTTP_X_FORWARDED_FOR')
    if proxies and encaminhado:
        enderecos = [parte.strip() for parte in encaminhado.split(',') if parte.strip()]
        if enderecos:
            endereco = enderecos[-min(proxies, len(enderecos))]
    try:
        return str(ipaddress.ip_address(endereco))
    except (TypeError, ValueError):
        return None


def registrar_log(usuario, acao, detalhes="", request=None):
    from .models import AuditLog

    AuditLog.objects.create(
        usuario=usuario,
        acao=acao,
        detalhes=detalhes,
        endereco_ip=ip_do_cliente(request),
    )
