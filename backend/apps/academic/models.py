from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class AnoLetivo(models.Model):
    ano = models.PositiveIntegerField(unique=True)
    ativo = models.BooleanField(default=False)

    class Meta:
        ordering = ['-ano']
        verbose_name = 'ano letivo'
        verbose_name_plural = 'anos letivos'

    def __str__(self):
        return str(self.ano)

    @classmethod
    def atual(cls):
        return cls.objects.filter(ativo=True).first()


class Bimestre(models.Model):
    ano_letivo = models.ForeignKey(AnoLetivo, on_delete=models.CASCADE, related_name='bimestres')
    numero = models.PositiveSmallIntegerField(choices=[(i, f'{i}º bimestre') for i in range(1, 5)])
    inicio = models.DateField()
    fim = models.DateField()

    class Meta:
        ordering = ['ano_letivo', 'numero']
        constraints = [
            models.UniqueConstraint(fields=['ano_letivo', 'numero'], name='bimestre_unico_no_ano'),
        ]

    def __str__(self):
        return f'{self.numero}º bimestre de {self.ano_letivo}'


class Turma(models.Model):
    class Turno(models.TextChoices):
        MANHA = 'manha', 'Manhã'
        TARDE = 'tarde', 'Tarde'
        NOITE = 'noite', 'Noite'
        INTEGRAL = 'integral', 'Integral'

    ano_letivo = models.ForeignKey(AnoLetivo, on_delete=models.PROTECT, related_name='turmas')
    nome = models.CharField(max_length=20)
    serie = models.CharField(max_length=30)
    turno = models.CharField(max_length=10, choices=Turno.choices)

    class Meta:
        ordering = ['ano_letivo', 'nome']
        constraints = [
            models.UniqueConstraint(fields=['ano_letivo', 'nome'], name='turma_unica_no_ano'),
        ]

    def __str__(self):
        return f'{self.nome} ({self.ano_letivo})'


class Disciplina(models.Model):
    """RN52: cada disciplina pertence a uma única turma e tem um único professor."""

    turma = models.ForeignKey(Turma, on_delete=models.PROTECT, related_name='disciplinas')
    nome = models.CharField(max_length=80)
    carga_horaria = models.PositiveIntegerField()
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='disciplinas',
        limit_choices_to={'role': 'professor'},
    )

    class Meta:
        ordering = ['turma', 'nome']
        constraints = [
            models.UniqueConstraint(fields=['turma', 'nome'], name='disciplina_unica_na_turma'),
        ]

    def __str__(self):
        return f'{self.nome} – {self.turma.nome}'


class Matricula(models.Model):
    class Situacao(models.TextChoices):
        ATIVA = 'ativa', 'Ativa'
        TRANSFERIDA = 'transferida', 'Transferida'
        ENCERRADA = 'encerrada', 'Encerrada'

    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='matriculas',
        limit_choices_to={'role': 'aluno'},
    )
    turma = models.ForeignKey(Turma, on_delete=models.PROTECT, related_name='matriculas')
    ano_letivo = models.ForeignKey(AnoLetivo, on_delete=models.PROTECT, related_name='matriculas', editable=False)
    data_inicio = models.DateField(default=timezone.localdate)
    data_fim = models.DateField(null=True, blank=True)
    situacao = models.CharField(max_length=12, choices=Situacao.choices, default=Situacao.ATIVA)

    class Meta:
        ordering = ['-data_inicio']
        constraints = [
            models.UniqueConstraint(
                fields=['aluno', 'ano_letivo'],
                condition=Q(situacao='ativa'),
                name='uma_matricula_ativa_por_ano',
            ),
        ]

    def __str__(self):
        return f'{self.aluno} em {self.turma}'

    def save(self, *args, **kwargs):
        self.ano_letivo_id = self.turma.ano_letivo_id
        super().save(*args, **kwargs)


class VinculoResponsavel(models.Model):
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vinculos_como_responsavel',
        limit_choices_to={'role': 'responsavel'},
    )
    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vinculos_como_aluno',
        limit_choices_to={'role': 'aluno'},
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'vínculo de responsável'
        verbose_name_plural = 'vínculos de responsáveis'
        constraints = [
            models.UniqueConstraint(fields=['responsavel', 'aluno'], name='vinculo_unico'),
        ]

    def __str__(self):
        return f'{self.responsavel} responde por {self.aluno}'


class Nota(models.Model):
    """RN57: uma nota de 0 a 10 por aluno, disciplina e bimestre. RN59: só aparece para
    aluno e responsáveis depois de publicada pelo professor."""

    matricula = models.ForeignKey(Matricula, on_delete=models.PROTECT, related_name='notas')
    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT, related_name='notas')
    bimestre = models.ForeignKey(Bimestre, on_delete=models.PROTECT, related_name='notas')
    valor = models.DecimalField(max_digits=3, decimal_places=1)
    publicada = models.BooleanField(default=False)
    publicada_em = models.DateTimeField(null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['matricula', 'disciplina', 'bimestre'], name='nota_unica_por_bimestre'),
            models.CheckConstraint(condition=Q(valor__gte=0) & Q(valor__lte=10), name='nota_entre_0_e_10'),
        ]

    def __str__(self):
        return f'{self.matricula.aluno} – {self.disciplina.nome} – {self.bimestre.numero}º bim.: {self.valor}'


class Chamada(models.Model):
    """RN62: uma chamada por disciplina e data. RN64: a data define o bimestre."""

    disciplina = models.ForeignKey(Disciplina, on_delete=models.PROTECT, related_name='chamadas')
    bimestre = models.ForeignKey(Bimestre, on_delete=models.PROTECT, related_name='chamadas')
    data = models.DateField()
    quantidade_aulas = models.PositiveSmallIntegerField()
    registrada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='chamadas_registradas',
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data']
        constraints = [
            models.UniqueConstraint(fields=['disciplina', 'data'], name='chamada_unica_por_dia'),
            models.CheckConstraint(
                condition=Q(quantidade_aulas__gte=1) & Q(quantidade_aulas__lte=4), name='chamada_de_1_a_4_aulas',
            ),
        ]

    def __str__(self):
        return f'{self.disciplina} em {self.data:%d/%m/%Y}'


class Falta(models.Model):
    """RN63: a ausência conta para todas as aulas da chamada."""

    chamada = models.ForeignKey(Chamada, on_delete=models.CASCADE, related_name='faltas')
    matricula = models.ForeignKey(Matricula, on_delete=models.PROTECT, related_name='faltas')
    quantidade = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['chamada', 'matricula'], name='falta_unica_por_chamada'),
        ]

    def __str__(self):
        return f'{self.matricula.aluno} faltou {self.quantidade} aula(s) em {self.chamada}'
