from rest_framework import viewsets

from .models import Aviso
from .serializers import AvisoSerializer


class AvisoViewSet(viewsets.ModelViewSet):
    queryset = Aviso.objects.all()
    serializer_class = AvisoSerializer
