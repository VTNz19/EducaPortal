
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academic', '0002_chamada_falta_nota_chamada_chamada_unica_por_dia_and_more'),
        ('communication', '0003_aviso_autor'),
    ]

    operations = [
        migrations.AddField(
            model_name='aviso',
            name='fim_exibicao',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='aviso',
            name='inicio_exibicao',
            field=models.DateField(default=django.utils.timezone.localdate),
        ),
        migrations.AddField(
            model_name='aviso',
            name='notificado_em',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='aviso',
            name='notificar_email',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='aviso',
            name='turma',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='avisos', to='academic.turma'),
        ),
    ]
