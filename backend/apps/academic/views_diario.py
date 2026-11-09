"""Diário de classe: lançamento e publicação de notas (RF15), chamada (RF16) e boletim (RF17/RF18)."""
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.permissions import GESTORES, AceitouTermosVigentes, PodeUsarDiario
from apps.audit.utils import registrar_log
from .pdf import gerar_boletim_pdf
from .models import Bimestre, Chamada, Disciplina, Falta, Matricula, Nota, VinculoResponsavel
from .serializers import LancarNotasSerializer, PublicarNotasSerializer, RegistrarChamadaSerializer
from .servicos import (
    bimestre_da_data,
    bimestre_em_andamento,
    boletim_da_matricula,
    emails_do_aluno_e_responsaveis,
    matricula_do_boletim,
    notificar,
)


def nome(usuario):
    return usuario.get_full_name() or usuario.username


def matriculas_ativas(disciplina):
    return (Matricula.objects.filter(turma=disciplina.turma, situacao=Matricula.Situacao.ATIVA)
            .select_related('aluno').order_by('aluno__first_name', 'aluno__last_name'))


def bimestre_por_numero(disciplina, numero):
    bimestre = Bimestre.objects.filter(ano_letivo=disciplina.turma.ano_letivo, numero=numero).first()
    if bimestre is None:
        raise ValidationError({'bimestre': ['Bimestre não cadastrado neste ano letivo.']})
    return bimestre


def mensagens(erros):
    """Achata os erros aninhados do DRF (por índice da lista) em uma lista simples de mensagens."""
    if isinstance(erros, dict):
        return [m for v in erros.values() for m in mensagens(v)]
    if isinstance(erros, list):
        return [m for v in erros for m in mensagens(v)]
    return [str(erros)]


def validar(serializer):
    if not serializer.is_valid():
        raise ValidationError({campo: sorted(set(mensagens(erro))) for campo, erro in serializer.errors.items()})
    return serializer.validated_data


def bimestre_json(b):
    return {'numero': b.numero, 'inicio': b.inicio, 'fim': b.fim}


class DiarioViewSet(viewsets.GenericViewSet):
    """Rotas em /api/v1/diario/{disciplina}/..."""

    permission_classes = [IsAuthenticated, AceitouTermosVigentes, PodeUsarDiario]

    def get_queryset(self):
        qs = Disciplina.objects.select_related('turma__ano_letivo', 'professor')
        if self.request.user.role == User.Role.PROFESSOR:
            qs = qs.filter(professor=self.request.user)
        return qs

    def exigir_professor(self):
        if self.request.user.role != User.Role.PROFESSOR:
            raise PermissionDenied('Somente o professor da disciplina lança e publica notas.')

    def log(self, acao, detalhes):
        registrar_log(self.request.user, acao, detalhes=detalhes, request=self.request)


    def estado_notas(self, disciplina, bimestre):
        notas = {n.matricula_id: n for n in Nota.objects.filter(disciplina=disciplina, bimestre=bimestre)}
        alunos = []
        for m in matriculas_ativas(disciplina):
            nota = notas.get(m.id)
            alunos.append({
                'matricula': m.id, 'aluno_id': m.aluno_id, 'nome': nome(m.aluno),
                'valor': nota.valor if nota else None, 'publicada': bool(nota and nota.publicada),
            })
        return {
            'disciplina': {'id': disciplina.id, 'nome': disciplina.nome, 'turma': disciplina.turma.nome},
            'bimestre': bimestre_json(bimestre),
            'alunos': alunos,
            'sem_nota': sum(1 for a in alunos if a['valor'] is None),
            'pendentes_publicacao': sum(1 for a in alunos if a['valor'] is not None and not a['publicada']),
        }

    @action(detail=True, methods=['get', 'post'])
    def notas(self, request, pk=None):
        disciplina = self.get_object()
        if request.method == 'GET':
            numero = request.query_params.get('bimestre')
            bimestre = (bimestre_por_numero(disciplina, numero) if numero
                        else bimestre_em_andamento(disciplina.turma.ano_letivo))
            if bimestre is None:
                raise ValidationError({'bimestre': ['O ano letivo ainda não tem bimestres cadastrados.']})
            return Response(self.estado_notas(disciplina, bimestre))

        self.exigir_professor()
        dados = LancarNotasSerializer(data=request.data)
        validar(dados)
        bimestre = bimestre_por_numero(disciplina, dados.validated_data['bimestre'])
        validas = {m.id: m for m in matriculas_ativas(disciplina)}
        existentes = {n.matricula_id: n for n in Nota.objects.filter(disciplina=disciplina, bimestre=bimestre)}

        erros = []
        for item in dados.validated_data['notas']:
            if item['matricula'] not in validas:
                erros.append('Um dos alunos não está matriculado nesta turma.')
            elif item['valor'] is None and existentes.get(item['matricula']) and existentes[item['matricula']].publicada:
                erros.append(f'A nota de {nome(validas[item["matricula"]].aluno)} já foi publicada; corrija o valor em vez de apagá-lo.')
        if erros:
            raise ValidationError({'notas': sorted(set(erros))})

        alteradas = []
        with transaction.atomic():
            for item in dados.validated_data['notas']:
                nota = existentes.get(item['matricula'])
                valor = item['valor']
                if valor is None:
                    if nota:
                        nota.delete()
                elif nota is None:
                    Nota.objects.create(matricula_id=item['matricula'], disciplina=disciplina, bimestre=bimestre, valor=valor)
                elif nota.valor != valor:
                    if nota.publicada:
                        alteradas.append((nota, nota.valor, valor))
                    nota.valor = valor
                    nota.save(update_fields=['valor', 'atualizado_em'])
        self.log('notas_lancadas', f'disciplina id={disciplina.id}, {bimestre.numero}º bimestre, '
                                   f'{len(dados.validated_data["notas"])} aluno(s)')
        for nota, antes, depois in alteradas:
            self.log('nota_alterada', f'matricula id={nota.matricula_id}, disciplina id={disciplina.id}, '
                                      f'{bimestre.numero}º bimestre: {antes} -> {depois}')

        resposta = self.estado_notas(disciplina, bimestre)
        if alteradas:
            alunos = [validas[n.matricula_id].aluno for n, _, _ in alteradas]
            resposta['email_enviado'] = notificar(
                emails_do_aluno_e_responsaveis(alunos), 'Nota atualizada no EducaPortal',
                f'Houve uma atualização de nota em {disciplina.nome}.', '/boletim', request.user, request)
        return Response(resposta)

    @action(detail=True, methods=['post'], url_path='publicar-notas')
    def publicar_notas(self, request, pk=None):
        disciplina = self.get_object()
        self.exigir_professor()
        dados = PublicarNotasSerializer(data=request.data)
        validar(dados)
        bimestre = bimestre_por_numero(disciplina, dados.validated_data['bimestre'])

        estado = self.estado_notas(disciplina, bimestre)
        if estado['sem_nota'] and not dados.validated_data['confirmar']:
            return Response({
                'detail': f'{estado["sem_nota"]} aluno(s) ainda estão sem nota. Confirme para publicar mesmo assim.',
                'requer_confirmacao': True,
            }, status=status.HTTP_409_CONFLICT)

        a_publicar = Nota.objects.filter(disciplina=disciplina, bimestre=bimestre, publicada=False).select_related('matricula__aluno')
        alunos = [n.matricula.aluno for n in a_publicar]
        if not alunos:
            raise ValidationError({'detail': 'Não há notas novas para publicar neste bimestre.'})
        a_publicar.update(publicada=True, publicada_em=timezone.now())
        self.log('notas_publicadas', f'disciplina id={disciplina.id}, {bimestre.numero}º bimestre, {len(alunos)} nota(s)')

        resposta = self.estado_notas(disciplina, bimestre)
        resposta['email_enviado'] = notificar(
            emails_do_aluno_e_responsaveis(alunos), 'Notas novas no EducaPortal',
            f'Foram publicadas notas do {bimestre.numero}º bimestre em {disciplina.nome}.',
            '/boletim', request.user, request)
        return Response(resposta)


    def validar_data(self, disciplina, data):
        if data > timezone.localdate():
            raise ValidationError({'data': ['Escolha uma data entre o início do ano letivo e hoje.']})
        ano = disciplina.turma.ano_letivo
        bimestre = bimestre_da_data(ano, data)
        if bimestre is None:
            raise ValidationError({'data': ['A data não pertence a nenhum bimestre do ano letivo.']})
        if self.request.user.role == User.Role.PROFESSOR and bimestre != bimestre_em_andamento(ano):
            raise ValidationError({'data': [f'O {bimestre.numero}º bimestre está encerrado. '
                                            f'Solicite a correção à secretaria.']})
        return bimestre

    def estado_chamada(self, disciplina, data, bimestre):
        chamada = Chamada.objects.filter(disciplina=disciplina, data=data).first()
        ausentes = set(chamada.faltas.values_list('matricula_id', flat=True)) if chamada else set()
        return {
            'disciplina': {'id': disciplina.id, 'nome': disciplina.nome, 'turma': disciplina.turma.nome},
            'data': data,
            'bimestre': bimestre_json(bimestre),
            'existente': chamada is not None,
            'quantidade_aulas': chamada.quantidade_aulas if chamada else 1,
            'alunos': [
                {'matricula': m.id, 'aluno_id': m.aluno_id, 'nome': nome(m.aluno), 'presente': m.id not in ausentes}
                for m in matriculas_ativas(disciplina)
            ],
        }

    @action(detail=True, methods=['get', 'post'])
    def chamada(self, request, pk=None):
        disciplina = self.get_object()
        if request.method == 'GET':
            texto = request.query_params.get('data')
            try:
                data = timezone.datetime.strptime(texto, '%Y-%m-%d').date() if texto else timezone.localdate()
            except ValueError:
                raise ValidationError({'data': ['Data inválida.']})
            return Response(self.estado_chamada(disciplina, data, self.validar_data(disciplina, data)))

        dados = RegistrarChamadaSerializer(data=request.data)
        validar(dados)
        data = dados.validated_data['data']
        aulas = dados.validated_data['quantidade_aulas']
        bimestre = self.validar_data(disciplina, data)
        validas = {m.id: m for m in matriculas_ativas(disciplina)}
        ausentes = set(dados.validated_data['ausentes'])
        if not ausentes <= validas.keys():
            raise ValidationError({'ausentes': ['Um dos alunos não está matriculado nesta turma.']})

        with transaction.atomic():
            chamada, criada = Chamada.objects.get_or_create(
                disciplina=disciplina, data=data,
                defaults={'bimestre': bimestre, 'quantidade_aulas': aulas, 'registrada_por': request.user},
            )
            anteriores = set() if criada else set(chamada.faltas.values_list('matricula_id', flat=True))
            if not criada:
                chamada.quantidade_aulas = aulas
                chamada.save(update_fields=['quantidade_aulas', 'atualizado_em'])
                chamada.faltas.exclude(matricula_id__in=ausentes).delete()
                chamada.faltas.update(quantidade=aulas)
            Falta.objects.bulk_create(
                Falta(chamada=chamada, matricula_id=m, quantidade=aulas) for m in ausentes - anteriores
            )
        acao = 'chamada_registrada' if criada else 'chamada_alterada'
        self.log(acao, f'disciplina id={disciplina.id}, {data:%d/%m/%Y}, {aulas} aula(s), {len(ausentes)} ausente(s)')

        resposta = self.estado_chamada(disciplina, data, bimestre)
        novos = [validas[m].aluno for m in ausentes - anteriores]
        destinatarios = list(VinculoResponsavel.objects.filter(aluno__in=novos).values_list('responsavel__email', flat=True))
        resposta['email_enviado'] = notificar(
            destinatarios, 'Registro de frequência no EducaPortal',
            'Há um registro novo de frequência do aluno pelo qual você é responsável.',
            '/boletim', request.user, request) if destinatarios else None
        return Response(resposta)


def alunos_acessiveis(usuario):
    """RN71: o aluno vê o próprio boletim; o responsável, o dos alunos vinculados."""
    if usuario.role == User.Role.ALUNO:
        return User.objects.filter(pk=usuario.pk)
    if usuario.role == User.Role.RESPONSAVEL:
        return User.objects.filter(vinculos_como_aluno__responsavel=usuario).order_by('first_name')
    if usuario.role in GESTORES:
        return User.objects.filter(role=User.Role.ALUNO)
    return User.objects.none()


class BoletimAlunosView(APIView):
    """Alunos cujo boletim o usuário pode consultar (para o seletor do responsável)."""

    permission_classes = [IsAuthenticated, AceitouTermosVigentes]

    def get(self, request):
        if request.user.role in GESTORES:
            return Response([])
        return Response([{'id': a.id, 'nome': nome(a)} for a in alunos_acessiveis(request.user)])


class BoletimView(APIView):
    permission_classes = [IsAuthenticated, AceitouTermosVigentes]

    def carregar(self, request, aluno_id):
        """Devolve (aluno, matrícula) ou uma Response de erro (RN71)."""
        aluno = alunos_acessiveis(request.user).filter(pk=aluno_id).first()
        if aluno is None:
            return None, Response({'detail': 'Você não tem permissão para ver o boletim deste aluno.'},
                                  status=status.HTTP_403_FORBIDDEN)
        matricula = matricula_do_boletim(aluno, request.query_params.get('ano'))
        if matricula is None:
            return None, Response({'detail': 'Este aluno ainda não tem matrícula.'}, status=status.HTTP_404_NOT_FOUND)
        return (aluno, matricula), None

    def get(self, request, aluno_id):
        dados, erro = self.carregar(request, aluno_id)
        if erro:
            return erro
        aluno, matricula = dados
        boletim = boletim_da_matricula(matricula)
        boletim['anos'] = sorted(set(aluno.matriculas.values_list('ano_letivo__ano', flat=True)), reverse=True)
        return Response(boletim)


class BoletimPdfView(BoletimView):
    """RF18: o PDF é gerado no momento do pedido e não é armazenado (RN72)."""

    def get(self, request, aluno_id):
        dados, erro = self.carregar(request, aluno_id)
        if erro:
            return erro
        aluno, matricula = dados
        boletim = boletim_da_matricula(matricula)
        if not any(n is not None for d in boletim['disciplinas'] for n in d['notas'].values()):
            return Response({'detail': 'Ainda não há notas publicadas neste ano letivo.'},
                            status=status.HTTP_400_BAD_REQUEST)
        registrar_log(request.user, 'boletim_emitido', detalhes=f'aluno id={aluno.id}, ano {boletim["ano"]}',
                      request=request)
        resposta = HttpResponse(gerar_boletim_pdf(boletim), content_type='application/pdf')
        resposta['Content-Disposition'] = f'attachment; filename="boletim-{boletim["ano"]}-{aluno.id}.pdf"'
        return resposta
