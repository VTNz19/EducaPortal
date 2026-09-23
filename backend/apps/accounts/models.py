from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        PROFESSOR = "professor", "Professor"
        ALUNO = "aluno", "Aluno/Responsável"


    email = models.EmailField("e-mail", unique=True)
    role = models.CharField(
        "papel",
        max_length=20,
        choices=Role.choices,
        default=Role.ALUNO,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"

class PasswordResetToken(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tokens_redefinicao',
    )
    token = models.CharField(max_length=36, unique=True, default=uuid.uuid4, editable=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)

    def esta_valido(self):
        expira_em = self.criado_em + timedelta(hours=1)
        return not self.usado and timezone.now() < expira_em

    def __str__(self):
        return f"Token de {self.usuario} ({'usado' if self.usado else 'válido' if self.esta_valido() else 'expirado'})"
