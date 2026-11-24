from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AceitarTermosView,
    CustomTokenObtainPairView,
    DocumentoLegalView,
    EsqueciSenhaView,
    MeView,
    RedefinirSenhaView,
    UsuarioViewSet,
    VersoesDocumentoView,
)

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/aceitar-termos/', AceitarTermosView.as_view(), name='auth-aceitar-termos'),
    path('auth/esqueci-senha/', EsqueciSenhaView.as_view(), name='auth-esqueci-senha'),
    path('auth/redefinir-senha/', RedefinirSenhaView.as_view(), name='auth-redefinir-senha'),
    path('documentos/<str:tipo>/', DocumentoLegalView.as_view(), name='documento-legal'),
    path('documentos/<str:tipo>/versoes/', VersoesDocumentoView.as_view(), name='documento-versoes'),
] + router.urls
