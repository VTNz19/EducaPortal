import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        SECRETARIA = "secretaria", "Secretaria"
        DIRECAO = "direcao", "Direção"
        PROFESSOR = "professor", "Professor"
        ALUNO = "aluno", "Aluno"
        RESPONSAVEL = "responsavel", "Responsável"

    email = models.EmailField("e-mail", unique=True)
    role = models.CharField(
        "papel",
        max_length=20,
        choices=Role.choices,
        default=Role.ALUNO,
    )
    termos_versao_aceita = models.CharField("versão dos documentos aceita", max_length=30, blank=True, default="")
    termos_aceitos_em = models.DateTimeField("termo aceito em", null=True, blank=True)
    desativado_em = models.DateTimeField("desativada em", null=True, blank=True, editable=False)
    anonimizado_em = models.DateTimeField("anonimizada em", null=True, blank=True, editable=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def precisa_aceitar_termos(self):
        from .documentos import versao_vigente

        return self.termos_versao_aceita != versao_vigente()

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"

    def save(self, *args, **kwargs):
        """Guarda a data do desligamento, que conta o prazo de anonimização da conta (RN81)."""
        if self.is_active:
            self.desativado_em = None
        elif self.desativado_em is None:
            self.desativado_em = timezone.now()
        campos = kwargs.get("update_fields")
        if campos is not None and "is_active" in campos:
            kwargs["update_fields"] = {*campos, "desativado_em"}
        super().save(*args, **kwargs)


class PasswordResetToken(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tokens_redefinicao',
    )
    token = models.CharField(max_length=36, unique=True, default=uuid.uuid4, editable=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)

    def __str__(self):
        return f"Token de {self.usuario} ({'usado' if self.usado else 'válido' if self.esta_valido() else 'expirado'})"

    def esta_valido(self):
        expira_em = self.criado_em + timedelta(hours=1)
        return not self.usado and timezone.now() < expira_em


class DocumentoLegal(models.Model):
    """Versão publicada pela Direção do Termo de Uso ou da Política de Privacidade (RF23).

    As versões nunca são editadas nem excluídas: cada publicação cria uma nova e exige novo aceite.
    """

    class Tipo(models.TextChoices):
        TERMO = "termo", "Termo de Uso e Aceite"
        POLITICA = "politica", "Política de Privacidade"

    tipo = models.CharField("documento", max_length=10, choices=Tipo.choices)
    versao = models.CharField("versão", max_length=12)
    conteudo = models.TextField("conteúdo (Markdown)")
    resumo = models.CharField("resumo da alteração", max_length=300)
    publicado_em = models.DateTimeField("publicado em", default=timezone.now)
    publicado_por = models.ForeignKey(
        "accounts.User", verbose_name="publicado por", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )

    class Meta:
        verbose_name = "documento legal"
        verbose_name_plural = "documentos legais"
        ordering = ["-publicado_em", "-id"]
        constraints = [models.UniqueConstraint(fields=["tipo", "versao"], name="documento_versao_unica")]

    def __str__(self):
        return f"{self.get_tipo_display()} {self.versao}"
