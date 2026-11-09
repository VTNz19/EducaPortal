
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academic', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chamada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField()),
                ('quantidade_aulas', models.PositiveSmallIntegerField()),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('bimestre', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chamadas', to='academic.bimestre')),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='chamadas', to='academic.disciplina')),
                ('registrada_por', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chamadas_registradas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-data'],
            },
        ),
        migrations.CreateModel(
            name='Falta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveSmallIntegerField()),
                ('chamada', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faltas', to='academic.chamada')),
                ('matricula', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='faltas', to='academic.matricula')),
            ],
        ),
        migrations.CreateModel(
            name='Nota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=1, max_digits=3)),
                ('publicada', models.BooleanField(default=False)),
                ('publicada_em', models.DateTimeField(blank=True, null=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('bimestre', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='notas', to='academic.bimestre')),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='notas', to='academic.disciplina')),
                ('matricula', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='notas', to='academic.matricula')),
            ],
        ),
        migrations.AddConstraint(
            model_name='chamada',
            constraint=models.UniqueConstraint(fields=('disciplina', 'data'), name='chamada_unica_por_dia'),
        ),
        migrations.AddConstraint(
            model_name='chamada',
            constraint=models.CheckConstraint(condition=models.Q(('quantidade_aulas__gte', 1), ('quantidade_aulas__lte', 4)), name='chamada_de_1_a_4_aulas'),
        ),
        migrations.AddConstraint(
            model_name='falta',
            constraint=models.UniqueConstraint(fields=('chamada', 'matricula'), name='falta_unica_por_chamada'),
        ),
        migrations.AddConstraint(
            model_name='nota',
            constraint=models.UniqueConstraint(fields=('matricula', 'disciplina', 'bimestre'), name='nota_unica_por_bimestre'),
        ),
        migrations.AddConstraint(
            model_name='nota',
            constraint=models.CheckConstraint(condition=models.Q(('valor__gte', 0), ('valor__lte', 10)), name='nota_entre_0_e_10'),
        ),
    ]
