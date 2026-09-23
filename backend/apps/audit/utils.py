def registrar_log(usuario, acao, detalhes="", request=None):
    from .models import AuditLog

    endereco_ip = request.META.get('REMOTE_ADDR') if request is not None else None

    AuditLog.objects.create(
        usuario=usuario,
        acao=acao,
        detalhes=detalhes,
        endereco_ip=endereco_ip,
    )
