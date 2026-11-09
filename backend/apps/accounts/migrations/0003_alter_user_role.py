
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_passwordresettoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('secretaria', 'Secretaria'), ('direcao', 'Direção'), ('professor', 'Professor'), ('aluno', 'Aluno'), ('responsavel', 'Responsável')], default='aluno', max_length=20, verbose_name='papel'),
        ),
    ]
