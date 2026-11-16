from django.contrib import admin
from django.urls import include, path

from apps.audit.views import RotinasDiariasView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.communication.urls')),
    path('api/v1/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.academic.urls')),
    path('api/v1/rotinas/diarias/', RotinasDiariasView.as_view(), name='rotinas-diarias'),
]
