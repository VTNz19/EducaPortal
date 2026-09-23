from rest_framework.permissions import BasePermission


class IsRole(BasePermission):
    """Permite acesso apenas a usuários autenticados com um dos roles definidos."""
    roles: list[str] = []

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.roles
        )


class IsAdmin(IsRole):
    roles = ['admin']


class IsProfessor(IsRole):
    roles = ['professor']


class IsAluno(IsRole):
    roles = ['aluno']


class IsAdminOrProfessor(IsRole):
    roles = ['admin', 'professor']
