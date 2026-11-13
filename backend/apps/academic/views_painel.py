"""Painel de indicadores (RF21). Cada perfil só recebe os próprios dados (RN79 e RN80)."""
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.permissions import GESTORES, AceitouTermosVigentes, IsProfessor

from .indicadores import alunos_na_situacao, painel_do_aluno, painel_do_gestor, painel_do_professor
from .models import Disciplina
from .views_diario import alunos_acessiveis


def inteiro_do_parametro(request, nome, opcoes=None):
    valor = request.query_params.get(nome)
    if valor in (None, ''):
        return None
    if not valor.isdigit() or (opcoes and int(valor) not in opcoes):
        raise ValidationError({nome: ['Valor inválido.']})
    return int(valor)


class PainelView(APIView):
    permission_classes = [IsAuthenticated, AceitouTermosVigentes]

    def get(self, request):
        usuario = request.user
        bimestre = inteiro_do_parametro(request, 'bimestre', range(1, 5))
        if usuario.role in GESTORES:
            return Response(painel_do_gestor(bimestre))
        if usuario.role == User.Role.PROFESSOR:
            return Response(painel_do_professor(usuario, bimestre))

        alunos = list(alunos_acessiveis(usuario))
        escolhido = inteiro_do_parametro(request, 'aluno')
        aluno = next((a for a in alunos if a.id == escolhido), None)
        if escolhido is not None and aluno is None:
            raise PermissionDenied('Você não tem acesso aos indicadores deste aluno.')
        return Response(painel_do_aluno(aluno or next(iter(alunos), None), alunos))


class PainelAlunosView(APIView):
    """Lista nominal de uma disciplina, exclusiva do professor responsável por ela (RN80)."""

    permission_classes = [IsAuthenticated, AceitouTermosVigentes, IsProfessor]

    def get(self, request, disciplina_id):
        situacao = request.query_params.get('situacao')
        if situacao not in ('abaixo_media', 'abaixo_frequencia'):
            raise ValidationError({'situacao': ['Informe abaixo_media ou abaixo_frequencia.']})
        disciplina = get_object_or_404(Disciplina.objects.select_related('turma'),
                                       pk=disciplina_id, professor=request.user)
        return Response(alunos_na_situacao(disciplina, situacao))
