from django.db import transaction
from rest_framework import serializers

from apps.accounts.models import User
from .models import AnoLetivo, Bimestre, Disciplina, Turma
from .regras import erros_dos_bimestres


class BimestreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bimestre
        fields = ['numero', 'inicio', 'fim']


class AnoLetivoSerializer(serializers.ModelSerializer):
    bimestres = BimestreSerializer(many=True)

    class Meta:
        model = AnoLetivo
        fields = ['id', 'ano', 'ativo', 'bimestres']
        extra_kwargs = {
            'ano': {'error_messages': {'unique': 'Este ano letivo já está cadastrado.'}},
        }

    def validate_bimestres(self, value):
        erros = erros_dos_bimestres(value)
        if erros:
            raise serializers.ValidationError(erros)
        return value

    @transaction.atomic
    def create(self, validated_data):
        bimestres = validated_data.pop('bimestres')
        if validated_data.get('ativo'):
            AnoLetivo.objects.update(ativo=False)
        ano = AnoLetivo.objects.create(**validated_data)
        Bimestre.objects.bulk_create(Bimestre(ano_letivo=ano, **b) for b in bimestres)
        return ano

    @transaction.atomic
    def update(self, instance, validated_data):
        bimestres = validated_data.pop('bimestres', None)
        if validated_data.get('ativo'):
            AnoLetivo.objects.exclude(pk=instance.pk).update(ativo=False)
        instance = super().update(instance, validated_data)
        if bimestres is not None:
            for b in bimestres:
                Bimestre.objects.update_or_create(ano_letivo=instance, numero=b['numero'], defaults=b)
        return instance


class TurmaSerializer(serializers.ModelSerializer):
    ano = serializers.IntegerField(source='ano_letivo.ano', read_only=True)
    turno_nome = serializers.CharField(source='get_turno_display', read_only=True)
    total_alunos = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Turma
        fields = ['id', 'ano_letivo', 'ano', 'nome', 'serie', 'turno', 'turno_nome', 'total_alunos']
        validators = []

    def validate_nome(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('O nome da turma não pode ser vazio.')
        return value

    def validate(self, attrs):
        ano_letivo = attrs.get('ano_letivo', getattr(self.instance, 'ano_letivo', None))
        nome = attrs.get('nome', getattr(self.instance, 'nome', None))
        repetida = Turma.objects.filter(ano_letivo=ano_letivo, nome__iexact=nome)
        if self.instance:
            repetida = repetida.exclude(pk=self.instance.pk)
        if repetida.exists():
            raise serializers.ValidationError({'nome': f'Já existe a turma {nome} em {ano_letivo}.'})
        return attrs


class DisciplinaSerializer(serializers.ModelSerializer):
    turma_nome = serializers.CharField(source='turma.nome', read_only=True)
    ano = serializers.IntegerField(source='turma.ano_letivo.ano', read_only=True)
    professor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        error_messages={'does_not_exist': 'Professor não encontrado.'},
    )
    professor_nome = serializers.SerializerMethodField()

    class Meta:
        model = Disciplina
        fields = ['id', 'turma', 'turma_nome', 'ano', 'nome', 'carga_horaria', 'professor', 'professor_nome']
        validators = []

    def get_professor_nome(self, obj):
        return obj.professor.get_full_name() or obj.professor.username

    def validate_nome(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('O nome da disciplina não pode ser vazio.')
        return value

    def validate_carga_horaria(self, value):
        if value < 1:
            raise serializers.ValidationError('A carga horária deve ser de pelo menos 1 aula.')
        return value

    def validate_professor(self, value):
        if value.role != User.Role.PROFESSOR or not value.is_active:
            raise serializers.ValidationError('Selecione uma conta de professor ativa.')
        return value

    def validate(self, attrs):
        turma = attrs.get('turma', getattr(self.instance, 'turma', None))
        nome = attrs.get('nome', getattr(self.instance, 'nome', None))
        repetida = Disciplina.objects.filter(turma=turma, nome__iexact=nome)
        if self.instance:
            repetida = repetida.exclude(pk=self.instance.pk)
        if repetida.exists():
            raise serializers.ValidationError({'nome': f'A turma {turma.nome} já tem a disciplina {nome}.'})
        return attrs


class TurmaDestinoSerializer(serializers.Serializer):
    turma = serializers.PrimaryKeyRelatedField(
        queryset=Turma.objects.select_related('ano_letivo'),
        error_messages={'does_not_exist': 'Turma não encontrada.'},
    )


class ResponsavelSerializer(serializers.Serializer):
    responsavel = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.RESPONSAVEL),
        error_messages={'does_not_exist': 'Responsável não encontrado.'},
    )
    confirmar = serializers.BooleanField(required=False, default=False)


MSG_NOTA = 'A nota deve estar entre 0 e 10, com até uma casa decimal.'


class NotaItemSerializer(serializers.Serializer):
    matricula = serializers.IntegerField()
    valor = serializers.DecimalField(
        max_digits=3, decimal_places=1, min_value=0, max_value=10, allow_null=True,
        error_messages={k: MSG_NOTA for k in ('invalid', 'min_value', 'max_value', 'max_digits',
                                              'max_decimal_places', 'max_whole_digits')},
    )


class LancarNotasSerializer(serializers.Serializer):
    bimestre = serializers.IntegerField(min_value=1, max_value=4)
    notas = NotaItemSerializer(many=True, allow_empty=False)


class PublicarNotasSerializer(serializers.Serializer):
    bimestre = serializers.IntegerField(min_value=1, max_value=4)
    confirmar = serializers.BooleanField(required=False, default=False)


class RegistrarChamadaSerializer(serializers.Serializer):
    data = serializers.DateField()
    quantidade_aulas = serializers.IntegerField(
        min_value=1, max_value=4,
        error_messages={'min_value': 'Informe de 1 a 4 aulas.', 'max_value': 'Informe de 1 a 4 aulas.'},
    )
    ausentes = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)
