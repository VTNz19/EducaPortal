
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnoLetivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ano', models.PositiveIntegerField(unique=True)),
                ('ativo', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'ano letivo',
                'verbose_name_plural': 'anos letivos',
                'ordering': ['-ano'],
            },
        ),
        migrations.CreateModel(
            name='Turma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=20)),
                ('serie', models.CharField(max_length=30)),
                ('turno', models.CharField(choices=[('manha', 'Manhã'), ('tarde', 'Tarde'), ('noite', 'Noite'), ('integral', 'Integral')], max_length=10)),
                ('ano_letivo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='turmas', to='academic.anoletivo')),
            ],
            options={
                'ordering': ['ano_letivo', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='Matricula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_inicio', models.DateField(default=django.utils.timezone.localdate)),
                ('data_fim', models.DateField(blank=True, null=True)),
                ('situacao', models.CharField(choices=[('ativa', 'Ativa'), ('transferida', 'Transferida'), ('encerrada', 'Encerrada')], default='ativa', max_length=12)),
                ('aluno', models.ForeignKey(limit_choices_to={'role': 'aluno'}, on_delete=django.db.models.deletion.PROTECT, related_name='matriculas', to=settings.AUTH_USER_MODEL)),
                ('ano_letivo', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='matriculas', to='academic.anoletivo')),
                ('turma', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='matriculas', to='academic.turma')),
            ],
            options={
                'ordering': ['-data_inicio'],
            },
        ),
        migrations.CreateModel(
            name='Disciplina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80)),
                ('carga_horaria', models.PositiveIntegerField()),
                ('professor', models.ForeignKey(limit_choices_to={'role': 'professor'}, on_delete=django.db.models.deletion.PROTECT, related_name='disciplinas', to=settings.AUTH_USER_MODEL)),
                ('turma', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='disciplinas', to='academic.turma')),
            ],
            options={
                'ordering': ['turma', 'nome'],
            },
        ),
        migrations.CreateModel(
            name='VinculoResponsavel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('aluno', models.ForeignKey(limit_choices_to={'role': 'aluno'}, on_delete=django.db.models.deletion.CASCADE, related_name='vinculos_como_aluno', to=settings.AUTH_USER_MODEL)),
                ('responsavel', models.ForeignKey(limit_choices_to={'role': 'responsavel'}, on_delete=django.db.models.deletion.CASCADE, related_name='vinculos_como_responsavel', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'vínculo de responsável',
                'verbose_name_plural': 'vínculos de responsáveis',
            },
        ),
        migrations.CreateModel(
            name='Bimestre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.PositiveSmallIntegerField(choices=[(1, '1º bimestre'), (2, '2º bimestre'), (3, '3º bimestre'), (4, '4º bimestre')])),
                ('inicio', models.DateField()),
                ('fim', models.DateField()),
                ('ano_letivo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bimestres', to='academic.anoletivo')),
            ],
            options={
                'ordering': ['ano_letivo', 'numero'],
                'constraints': [models.UniqueConstraint(fields=('ano_letivo', 'numero'), name='bimestre_unico_no_ano')],
            },
        ),
        migrations.AddConstraint(
            model_name='turma',
            constraint=models.UniqueConstraint(fields=('ano_letivo', 'nome'), name='turma_unica_no_ano'),
        ),
        migrations.AddConstraint(
            model_name='matricula',
            constraint=models.UniqueConstraint(condition=models.Q(('situacao', 'ativa')), fields=('aluno', 'ano_letivo'), name='uma_matricula_ativa_por_ano'),
        ),
        migrations.AddConstraint(
            model_name='disciplina',
            constraint=models.UniqueConstraint(fields=('turma', 'nome'), name='disciplina_unica_na_turma'),
        ),
        migrations.AddConstraint(
            model_name='vinculoresponsavel',
            constraint=models.UniqueConstraint(fields=('responsavel', 'aluno'), name='vinculo_unico'),
        ),
    ]
