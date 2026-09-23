from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs_auditoria',
    )
    acao = models.CharField(max_length=50)
    detalhes = models.TextField(blank=True)
    endereco_ip = models.GenericIPAddressField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.acao} - {self.usuario or 'desconhecido'} ({self.criado_em:%d/%m/%Y %H:%M})"
