"""Cria dados fictícios para demonstração: contas de todos os perfis, turmas, notas, chamadas, avisos,
tarefas e eventos do calendário.

Uso: python manage.py criar_dados_demo
     python manage.py criar_dados_demo --agenda   (só acrescenta tarefas e eventos a uma demonstração já criada)

Todas as contas usam e-mail @exemplo.com e a mesma senha: a da variável DEMO_SENHA ou, sem ela, SENHA_DEMO.
Em um servidor público, defina DEMO_SENHA, porque SENHA_DEMO está no repositório. Nenhum e-mail é enviado.
Se o ano letivo atual já existir, ele é reaproveitado sem apagar nada; se o 4º bimestre já tiver
terminado, ele é estendido até 18/12 para que a chamada do dia funcione na demonstração.
O comando não roda duas vezes no mesmo banco, para não duplicar dados.
"""
import os
import random
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from apps.academic.models import (
    AnoLetivo,
    Bimestre,
    Chamada,
    Disciplina,
    Falta,
    Matricula,
    Nota,
    Turma,
    VinculoResponsavel,
)
from apps.accounts.documentos import versao_vigente
from apps.accounts.models import User
from apps.communication.models import AnexoTarefa, Aviso, EventoCalendario, Tarefa

SENHA_DEMO = 'Demo@2026'


def senha_demo():
    return os.environ.get('DEMO_SENHA') or SENHA_DEMO


def bimestres_padrao(ano):
    return [(date(ano, 2, 2), date(ano, 4, 17)), (date(ano, 4, 20), date(ano, 7, 3)),
            (date(ano, 7, 20), date(ano, 10, 2)), (date(ano, 10, 5), date(ano, 12, 18))]
PROFESSORES = {
    'Matemática': ('Paulo', 'Mendes'),
    'Português': ('Clara', 'Nunes'),
    'História': ('Rafael', 'Lima'),
    'Química': ('Beatriz', 'Costa'),
}
TURMAS = [('1º A', '1ª série', 'manha'), ('2º A', '2ª série', 'manha'), ('3º A', '3ª série', 'tarde')]
ALUNOS = [
    ['Ana Souza', 'Bruno Alves', 'Carla Dias', 'Diego Rocha', 'Elisa Prado', 'Fábio Moura'],
    ['Gabriela Lopes', 'Hugo Martins', 'Isabela Ramos', 'João Pires', 'Karen Faria', 'Lucas Teles'],
    ['Mariana Souza', 'Nicolas Alves', 'Olívia Castro', 'Pedro Gomes', 'Renata Melo', 'Samuel Vieira'],
]
IRMAOS = {('Ana Souza', 'Mariana Souza'): ('Rita', 'Souza'), ('Bruno Alves', 'Nicolas Alves'): ('Marcos', 'Alves')}
BASE_NOTA = {'Diego Rocha': 4.6, 'Hugo Martins': 5.1, 'Pedro Gomes': 5.0, 'Fábio Moura': 5.6}
CHANCE_FALTA = {'Elisa Prado': 0.32, 'Lucas Teles': 0.30, 'Samuel Vieira': 0.27}


def email_de(nome, sobrenome, prefixo=''):
    base = f'{prefixo}{nome}.{sobrenome}'.lower()
    for de, para in (('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ç', 'c'), ('ã', 'a'), ('õ', 'o')):
        base = base.replace(de, para)
    return f'{base}@exemplo.com'


class Command(BaseCommand):
    help = 'Cria dados fictícios de demonstração (contas @exemplo.com, turmas, notas, chamadas e avisos).'

    def conta(self, role, nome, sobrenome, email=None):
        email = email or email_de(nome, sobrenome)
        usuario = User.objects.create_user(
            username=email, email=email, password=senha_demo(), role=role, first_name=nome, last_name=sobrenome,
            termos_versao_aceita=versao_vigente(), termos_aceitos_em=timezone.now(),
        )
        self.contas.append((role, email))
        return usuario

    def ano_letivo(self, hoje):
        """Reaproveita o ano letivo atual ou cria um com os bimestres padrão."""
        ano = AnoLetivo.objects.filter(ano=hoje.year).first()
        if ano is None:
            AnoLetivo.objects.update(ativo=False)
            ano = AnoLetivo.objects.create(ano=hoje.year, ativo=True)
            for i, (inicio, fim) in enumerate(bimestres_padrao(hoje.year), start=1):
                Bimestre.objects.create(ano_letivo=ano, numero=i, inicio=inicio, fim=fim)
        elif not ano.ativo:
            AnoLetivo.objects.update(ativo=False)
            AnoLetivo.objects.filter(pk=ano.pk).update(ativo=True)
        bimestres = list(ano.bimestres.order_by('numero'))
        if len(bimestres) != 4:
            raise CommandError(f'O ano letivo {ano.ano} precisa ter os 4 bimestres cadastrados.')
        ultimo = bimestres[-1]
        if ultimo.fim < hoje:
            novo_fim = max(date(hoje.year, 12, 18), hoje)
            self.stdout.write(f'O 4º bimestre terminava em {ultimo.fim:%d/%m/%Y}; '
                              f'agora termina em {novo_fim:%d/%m/%Y}.')
            ultimo.fim = novo_fim
            ultimo.save(update_fields=['fim'])
        return ano, bimestres

    def add_arguments(self, parser):
        parser.add_argument('--agenda', action='store_true',
                            help='Acrescenta só as tarefas e os eventos a uma demonstração já criada.')

    @transaction.atomic
    def handle(self, *args, **options):
        if options.get('agenda'):
            return self.somente_agenda()
        if User.objects.filter(email='secretaria@exemplo.com').exists():
            raise CommandError('Os dados de demonstração já existem neste banco.')

        random.seed(2026)
        hoje = timezone.localdate()
        self.contas = []
        ano, bimestres = self.ano_letivo(hoje)
        existentes = set(Turma.objects.filter(ano_letivo=ano).values_list('nome', flat=True))
        repetidas = existentes & {nome for nome, _, _ in TURMAS}
        if repetidas:
            raise CommandError(f'Já existem as turmas {", ".join(sorted(repetidas))} em {ano.ano}.')

        self.conta(User.Role.SECRETARIA, 'Sandra', 'Oliveira', 'secretaria@exemplo.com')
        direcao = self.conta(User.Role.DIRECAO, 'Helena', 'Barros', 'direcao@exemplo.com')
        professores = {disc: self.conta(User.Role.PROFESSOR, n, s, email_de(n, s, 'prof.'))
                       for disc, (n, s) in PROFESSORES.items()}

        turmas, disciplinas = [], []
        for nome, serie, turno in TURMAS:
            turma = Turma.objects.create(ano_letivo=ano, nome=nome, serie=serie, turno=turno)
            turmas.append(turma)
            for disc, professor in professores.items():
                disciplinas.append(Disciplina.objects.create(
                    turma=turma, nome=disc, carga_horaria=160 if disc in ('Matemática', 'Português') else 80,
                    professor=professor))

        responsaveis = {}
        for (a, b), (n, s) in IRMAOS.items():
            r = self.conta(User.Role.RESPONSAVEL, n, s)
            responsaveis[a] = responsaveis[b] = r
        matriculas = []
        for turma, nomes in zip(turmas, ALUNOS, strict=True):
            for completo in nomes:
                nome, sobrenome = completo.split()
                if completo not in responsaveis:
                    pais = random.choice(['Carlos', 'Fernanda', 'Roberto', 'Patrícia', 'Sérgio', 'Juliana',
                                          'André', 'Cristina', 'Eduardo', 'Luciana', 'Marcelo', 'Vanessa'])
                    responsaveis[completo] = self.conta(User.Role.RESPONSAVEL, pais, sobrenome,
                                                        email_de(pais, sobrenome, f'{nome.lower()}.'))
                aluno = self.conta(User.Role.ALUNO, nome, sobrenome)
                VinculoResponsavel.objects.create(responsavel=responsaveis[completo], aluno=aluno)
                matriculas.append(Matricula.objects.create(aluno=aluno, turma=turma, data_inicio=bimestres[0].inicio))

        notas = []
        for m in matriculas:
            nome = m.aluno.get_full_name()
            base = BASE_NOTA.get(nome, random.uniform(6.2, 8.9))
            for disc in (d for d in disciplinas if d.turma_id == m.turma_id):
                ajuste = random.uniform(-0.8, 0.8)
                for b in bimestres:
                    if b.inicio > hoje:
                        continue
                    if b.numero == 4 and disc.nome in ('História', 'Química'):
                        continue
                    valor = max(0.0, min(10.0, base + ajuste + random.uniform(-1.2, 1.2)))
                    publicada = b.fim < hoje or disc.nome == 'Matemática'
                    notas.append(Nota(matricula=m, disciplina=disc, bimestre=b,
                                      valor=Decimal(str(round(valor, 1))), publicada=publicada,
                                      publicada_em=timezone.now() if publicada else None))
        Nota.objects.bulk_create(notas)

        faltas = []
        for disc in disciplinas:
            alunos_turma = [m for m in matriculas if m.turma_id == disc.turma_id]
            deslocamento = ['Matemática', 'Português', 'História', 'Química'].index(disc.nome)
            dia = bimestres[0].inicio + timedelta(days=deslocamento)
            while dia < hoje:
                bimestre = next((b for b in bimestres if b.inicio <= dia <= b.fim), None)
                if bimestre:
                    chamada = Chamada.objects.create(disciplina=disc, bimestre=bimestre, data=dia,
                                                     quantidade_aulas=2, registrada_por=disc.professor)
                    for m in alunos_turma:
                        if random.random() < CHANCE_FALTA.get(m.aluno.get_full_name(), 0.04):
                            faltas.append(Falta(chamada=chamada, matricula=m, quantidade=2))
                dia += timedelta(days=7)
        Falta.objects.bulk_create(faltas)

        prof_mat = professores['Matemática']
        Aviso.objects.create(titulo='Reunião de pais e mestres', fixado=True, autor=direcao,
                             conteudo='A reunião do 4º bimestre será no dia 21/11, às 19h, no auditório.')
        Aviso.objects.create(titulo='Simulado preparatório para o ENEM', autor=prof_mat, turma=turmas[2],
                             conteudo='O simulado será no sábado, 14/11, das 8h às 12h. Tragam caneta preta.')
        Aviso.objects.create(titulo='Lista de exercícios de funções', autor=prof_mat, turma=turmas[0],
                             conteudo='A lista está disponível na secretaria e deve ser entregue até 13/11.')
        Aviso.objects.create(titulo='Recesso de fim de ano', autor=direcao,
                             inicio_exibicao=hoje + timedelta(days=20),
                             conteudo='Não haverá aulas entre 21/12 e 31/01. Bom descanso a todos.')
        Aviso.objects.create(titulo='Inscrições para a Feira de Ciências', autor=direcao,
                             inicio_exibicao=date(ano.ano, 9, 1), fim_exibicao=date(ano.ano, 9, 30),
                             conteudo='As inscrições foram encerradas. Obrigado a todos os participantes.')

        tarefas, eventos = criar_agenda(hoje, turmas, disciplinas, direcao)

        self.stdout.write(self.style.SUCCESS(
            f'Dados criados: {len(self.contas)} contas, {len(turmas)} turmas, {len(disciplinas)} disciplinas, '
            f'{len(notas)} notas, {Chamada.objects.filter(disciplina__in=disciplinas).count()} chamadas, '
            f'{len(faltas)} faltas, 5 avisos, {tarefas} tarefas e {eventos} eventos.'))
        self.stdout.write('Senha de todas as contas: a da variável DEMO_SENHA.' if os.environ.get('DEMO_SENHA')
                          else f'Senha de todas as contas: {SENHA_DEMO}')
        for role in ('secretaria', 'direcao', 'professor', 'responsavel', 'aluno'):
            emails = [e for r, e in self.contas if r == role]
            self.stdout.write(f'  {role}: {emails[0]}' + (f' (e mais {len(emails) - 1})' if len(emails) > 1 else ''))

    def somente_agenda(self):
        direcao = User.objects.filter(email='direcao@exemplo.com').first()
        ano = AnoLetivo.atual()
        nomes = [nome for nome, _, _ in TURMAS]
        turmas = sorted(Turma.objects.filter(ano_letivo=ano, nome__in=nomes), key=lambda t: nomes.index(t.nome))
        if direcao is None or len(turmas) != len(TURMAS):
            raise CommandError('Crie primeiro a demonstração com: python manage.py criar_dados_demo')
        if Tarefa.objects.filter(disciplina__turma__in=turmas).exists():
            raise CommandError('As tarefas de demonstração já existem neste banco.')
        disciplinas = list(Disciplina.objects.filter(turma__in=turmas).select_related('professor'))
        tarefas, eventos = criar_agenda(timezone.localdate(), turmas, disciplinas, direcao)
        self.stdout.write(self.style.SUCCESS(f'Agenda criada: {tarefas} tarefas e {eventos} eventos.'))


def pdf_da_lista(titulo, linhas):
    """Gera um PDF simples para servir de anexo de demonstração."""
    buffer = BytesIO()
    pagina = canvas.Canvas(buffer, pagesize=A4)
    pagina.setFont('Helvetica-Bold', 16)
    pagina.drawString(60, 780, titulo)
    pagina.setFont('Helvetica', 12)
    for i, linha in enumerate(linhas):
        pagina.drawString(60, 740 - 22 * i, linha)
    pagina.save()
    return buffer.getvalue()


def criar_agenda(hoje, turmas, disciplinas, direcao):
    """Tarefas com prazos próximos (uma com PDF anexo) e eventos gerais e por turma."""
    def disciplina(turma, nome):
        return next(d for d in disciplinas if d.turma_id == turma.id and d.nome == nome)

    planos = [
        (turmas[0], 'Matemática', 'Lista de exercícios de funções', 'Resolver os exercícios 1 a 10.', 3, True),
        (turmas[0], 'Português', 'Resenha do conto "A cartomante"', 'Resenha de uma página.', 6, False),
        (turmas[1], 'História', 'Linha do tempo da República', 'Pode ser feita em grupo de até 3 alunos.', 4, False),
        (turmas[2], 'Química', 'Relatório da aula prática', 'Seguir o roteiro entregue na aula.', 2, False),
        (turmas[2], 'Matemática', 'Simulado de geometria', 'Questões de múltipla escolha.', 12, False),
        (turmas[0], 'História', 'Questionário sobre o Brasil Colônia', 'Responder às 5 questões.', -5, False),
    ]
    for turma, nome, titulo, descricao, dias, com_anexo in planos:
        materia = disciplina(turma, nome)
        tarefa = Tarefa.objects.create(disciplina=materia, titulo=titulo, descricao=descricao,
                                       prazo=hoje + timedelta(days=dias), autor=materia.professor)
        if com_anexo:
            conteudo = pdf_da_lista(titulo, [f'{n}) Exercício {n} da lista de funções.' for n in range(1, 11)])
            anexo = AnexoTarefa(tarefa=tarefa, nome_original='lista-de-funcoes.pdf', tamanho=len(conteudo))
            anexo.arquivo.save('lista-de-funcoes.pdf', ContentFile(conteudo), save=True)

    eventos = [
        ('Reunião de pais e mestres', 'reuniao', 6, 6, None),
        ('Prova de Matemática', 'prova', 4, 4, turmas[0]),
        ('Prova de Química', 'prova', 8, 8, turmas[2]),
        ('Feira de Ciências', 'evento', 10, 11, None),
        ('Recesso de fim de ano', 'feriado', 36, 60, None),
    ]
    for titulo, tipo, inicio, fim, turma in eventos:
        EventoCalendario.objects.create(titulo=titulo, tipo=tipo, inicio=hoje + timedelta(days=inicio),
                                        fim=hoje + timedelta(days=fim), turma=turma, criado_por=direcao)
    return len(planos), len(eventos)
