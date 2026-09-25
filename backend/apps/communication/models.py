from django.conf import settings
from django.db import models


class Aviso(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='avisos',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    fixado = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fixado', '-criado_em']

    def __str__(self):
        return self.titulo
