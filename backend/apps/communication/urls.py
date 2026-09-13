from rest_framework.routers import DefaultRouter

from .views import AvisoViewSet

router = DefaultRouter()
router.register('avisos', AvisoViewSet)

urlpatterns = router.urls
