from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import AceitouTermosVigentes, PodeGerenciarAviso
from apps.audit.utils import registrar_log
from .models import Aviso
from .serializers import AvisoSerializer


class AvisoViewSet(viewsets.ModelViewSet):
    queryset = Aviso.objects.select_related('autor')
    serializer_class = AvisoSerializer

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
