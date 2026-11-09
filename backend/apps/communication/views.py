from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.academic.models import Matricula
from apps.accounts.permissions import GESTORES, AceitouTermosVigentes, PodeGerenciarAviso
from apps.audit.utils import registrar_log
from .models import Aviso
from .notificacoes import notificar_aviso
from .serializers import AvisoSerializer


class AvisoViewSet(viewsets.ModelViewSet):
    serializer_class = AvisoSerializer

    def get_queryset(self):
        """RN40: cada perfil vê os avisos gerais e os das suas turmas, dentro do período (RN34).

        Gestores veem tudo; o autor também vê os próprios avisos agendados ou encerrados.
        """
        usuario = self.request.user
        qs = Aviso.objects.select_related('autor', 'turma')
        if usuario.role in GESTORES:
            return qs

        if usuario.role == 'professor':
            turmas = Q(turma__disciplinas__professor=usuario)
        elif usuario.role == 'aluno':
            turmas = Q(turma__matriculas__aluno=usuario, turma__matriculas__situacao=Matricula.Situacao.ATIVA)
        else:
            turmas = Q(turma__matriculas__aluno__vinculos_como_aluno__responsavel=usuario,
                       turma__matriculas__situacao=Matricula.Situacao.ATIVA)

        hoje = timezone.localdate()
        vigente = Q(inicio_exibicao__lte=hoje) & (Q(fim_exibicao__isnull=True) | Q(fim_exibicao__gte=hoje))
        visiveis = (Q(turma__isnull=True) | turmas) & vigente
        return qs.filter(visiveis | Q(autor=usuario)).distinct()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), AceitouTermosVigentes(), PodeGerenciarAviso()]
        return [IsAuthenticated(), AceitouTermosVigentes()]

    def perform_create(self, serializer):
        aviso = serializer.save(autor=self.request.user)
        registrar_log(
            self.request.user,
            'aviso_criado',
            detalhes=f'Aviso "{aviso.titulo}" (id={aviso.id})',
            request=self.request,
        )
        if aviso.notificar_email and aviso.situacao == 'vigente':
            notificar_aviso(aviso, self.request)

    def perform_update(self, serializer):
        aviso = serializer.save()
        registrar_log(
            self.request.user,
            'aviso_editado',
            detalhes=f'Aviso "{aviso.titulo}" (id={aviso.id})',
            request=self.request,
        )

    def perform_destroy(self, instance):
        titulo = instance.titulo
        aviso_id = instance.id
        instance.delete()
        registrar_log(
            self.request.user,
            'aviso_excluido',
            detalhes=f'Aviso "{titulo}" (id={aviso_id})',
            request=self.request,
        )
