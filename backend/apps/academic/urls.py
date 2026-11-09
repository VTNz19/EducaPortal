from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AlunoMatriculaViewSet, AnoLetivoViewSet, DisciplinaViewSet, TurmaViewSet
from .views_diario import BoletimAlunosView, BoletimPdfView, BoletimView, DiarioViewSet
from .views_painel import PainelAlunosView, PainelView

router = DefaultRouter()
router.register('anos-letivos', AnoLetivoViewSet, basename='ano-letivo')
router.register('turmas', TurmaViewSet, basename='turma')
router.register('disciplinas', DisciplinaViewSet, basename='disciplina')
router.register('alunos', AlunoMatriculaViewSet, basename='aluno')
router.register('diario', DiarioViewSet, basename='diario')

urlpatterns = [
    path('painel/', PainelView.as_view(), name='painel'),
    path('painel/disciplinas/<int:disciplina_id>/alunos/', PainelAlunosView.as_view(), name='painel-alunos'),
    path('boletim/alunos/',BoletimAlunosView.as_view(), name='boletim-alunos'),
    path('boletim/<int:aluno_id>/', BoletimView.as_view(), name='boletim'),
    path('boletim/<int:aluno_id>/pdf/', BoletimPdfView.as_view(), name='boletim-pdf'),
] + router.urls
