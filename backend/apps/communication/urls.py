from rest_framework.routers import DefaultRouter

from .views import AvisoViewSet, EventoCalendarioViewSet, TarefaViewSet

router = DefaultRouter()
router.register('avisos', AvisoViewSet, basename='aviso')
router.register('tarefas', TarefaViewSet, basename='tarefa')
router.register('eventos', EventoCalendarioViewSet, basename='evento')

urlpatterns = router.urls
