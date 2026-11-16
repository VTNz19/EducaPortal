from django.contrib import admin

from .models import AnexoTarefa, Aviso, EventoCalendario, Tarefa

admin.site.register(Aviso)
admin.site.register(EventoCalendario)


class AnexoInline(admin.TabularInline):
    model = AnexoTarefa
    extra = 0


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'disciplina', 'prazo', 'autor']
    inlines = [AnexoInline]
