from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['criado_em', 'usuario', 'acao', 'endereco_ip']
    list_filter = ['acao', 'criado_em']
    search_fields = ['detalhes', 'usuario__username', 'usuario__email']
    readonly_fields = ['usuario', 'acao', 'detalhes', 'endereco_ip', 'criado_em']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
