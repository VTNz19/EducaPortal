from rest_framework.permissions import BasePermission

GESTORES = ['secretaria', 'direcao']
PODEM_PUBLICAR = GESTORES + ['professor']


class IsRole(BasePermission):
    """Permite acesso apenas a usuários autenticados com um dos papéis definidos."""
    roles: list[str] = []

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.roles
        )


class IsSecretaria(IsRole):
    roles = ['secretaria']


class IsDirecao(IsRole):
    roles = ['direcao']


class IsProfessor(IsRole):
    roles = ['professor']


class IsAluno(IsRole):
    roles = ['aluno']


class IsResponsavel(IsRole):
    roles = ['responsavel']


class IsGestor(IsRole):
    roles = GESTORES


class PodeGerenciarAviso(BasePermission):
    """Secretaria e direção gerenciam qualquer aviso; professor só os que criou."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in PODEM_PUBLICAR
        )

    def has_object_permission(self, request, view, obj):
        if request.user.role in GESTORES:
            return True
        return obj.autor_id == request.user.id

class AceitouTermosVigentes(BasePermission):
    """Bloqueia o uso do sistema até o usuário aceitar a versão atual do termo."""

    message = 'É preciso aceitar a versão atual do Termo de Uso e Aceite.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and not request.user.precisa_aceitar_termos
        )
