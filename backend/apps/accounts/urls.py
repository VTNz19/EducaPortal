from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    EsqueciSenhaView,
    MeView,
    RedefinirSenhaView,
)

urlpatterns = [
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/me/', MeView.as_view(), name='auth-me'),
    path('auth/esqueci-senha/', EsqueciSenhaView.as_view(), name='auth-esqueci-senha'),
    path('auth/redefinir-senha/', RedefinirSenhaView.as_view(), name='auth-redefinir-senha'),
]
