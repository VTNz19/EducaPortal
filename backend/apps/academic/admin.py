from django.contrib import admin

from .models import AnoLetivo, Bimestre, Disciplina, Matricula, Turma, VinculoResponsavel


class BimestreInline(admin.TabularInline):
    model = Bimestre
    extra = 0


@admin.register(AnoLetivo)
class AnoLetivoAdmin(admin.ModelAdmin):
    list_display = ['ano', 'ativo']
    inlines = [BimestreInline]


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'serie', 'turno', 'ano_letivo']
    list_filter = ['ano_letivo', 'turno']


@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'turma', 'professor', 'carga_horaria']
    list_filter = ['turma__ano_letivo', 'turma']


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'turma', 'situacao', 'data_inicio', 'data_fim']
    list_filter = ['situacao', 'ano_letivo']


@admin.register(VinculoResponsavel)
class VinculoResponsavelAdmin(admin.ModelAdmin):
    list_display = ['responsavel', 'aluno', 'criado_em']
