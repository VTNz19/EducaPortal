from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsAdminOrProfessor
from apps.audit.utils import registrar_log
from .models import Aviso
from .serializers import AvisoSerializer


class AvisoViewSet(viewsets.ModelViewSet):
    queryset = Aviso.objects.all()
    serializer_class = AvisoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrProfessor()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        aviso = serializer.save()
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
