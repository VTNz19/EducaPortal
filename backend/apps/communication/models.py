from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class AvisoQuerySet(models.QuerySet):
    def vigentes(self, data=None):
        """RN34: avisos dentro do período de exibição."""
        data = data or timezone.localdate()
        return self.filter(Q(inicio_exibicao__lte=data), Q(fim_exibicao__isnull=True) | Q(fim_exibicao__gte=data))


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
    turma = models.ForeignKey(
        'academic.Turma',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='avisos',
    )
    inicio_exibicao = models.DateField(default=timezone.localdate)
    fim_exibicao = models.DateField(null=True, blank=True)
    notificar_email = models.BooleanField(default=False)
    notificado_em = models.DateTimeField(null=True, blank=True, editable=False)

    objects = AvisoQuerySet.as_manager()

    class Meta:
        ordering = ['-fixado', '-criado_em']

    def __str__(self):
        return self.titulo

    @property
    def situacao(self):
        hoje = timezone.localdate()
        if self.inicio_exibicao > hoje:
            return 'agendado'
        if self.fim_exibicao and self.fim_exibicao < hoje:
            return 'encerrado'
        return 'vigente'
