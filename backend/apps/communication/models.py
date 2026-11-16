import uuid

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


def caminho_do_anexo(instance, filename):
    """O nome no disco é aleatório; o nome original fica só no banco, para o download."""
    extensao = filename.rsplit('.', 1)[-1].lower()
    return f'tarefas/{timezone.now():%Y/%m}/{uuid.uuid4().hex}.{extensao}'


class Tarefa(models.Model):
    """RF19: tarefa de uma disciplina, publicada pelo professor responsável."""

    disciplina = models.ForeignKey('academic.Disciplina', on_delete=models.PROTECT, related_name='tarefas')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    prazo = models.DateField()
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tarefas',
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['prazo', 'id']

    def __str__(self):
        return f'{self.titulo} ({self.disciplina})'


class AnexoTarefa(models.Model):
    """RN75: PDF, DOCX, PNG ou JPG de até 10 MB."""

    tarefa = models.ForeignKey(Tarefa, on_delete=models.CASCADE, related_name='anexos')
    arquivo = models.FileField(upload_to=caminho_do_anexo)
    nome_original = models.CharField(max_length=255)
    tamanho = models.PositiveIntegerField()

    class Meta:
        ordering = ['id']
        verbose_name = 'anexo de tarefa'
        verbose_name_plural = 'anexos de tarefas'

    def __str__(self):
        return self.nome_original


class EventoCalendario(models.Model):
    """RF20: evento do calendário escolar, geral ou de uma turma. RN78: sem dados pessoais."""

    class Tipo(models.TextChoices):
        PROVA = 'prova', 'Prova'
        FERIADO = 'feriado', 'Feriado'
        REUNIAO = 'reuniao', 'Reunião'
        EVENTO = 'evento', 'Evento escolar'

    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    inicio = models.DateField()
    fim = models.DateField()
    turma = models.ForeignKey(
        'academic.Turma',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='eventos',
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_criados',
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['inicio', 'id']
        verbose_name = 'evento do calendário'
        verbose_name_plural = 'eventos do calendário'
        constraints = [
            models.CheckConstraint(condition=Q(fim__gte=models.F('inicio')), name='evento_fim_depois_do_inicio'),
        ]

    def __str__(self):
        return f'{self.titulo} ({self.inicio:%d/%m/%Y})'
