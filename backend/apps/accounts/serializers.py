from django.conf import settings
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.academic.models import Matricula, Turma, VinculoResponsavel

from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['nome'] = user.get_full_name() or user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['nome'] = self.user.get_full_name() or self.user.username
        return data


class MeSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField()
    precisa_aceitar_termos = serializers.BooleanField(read_only=True)
    versao_termos_atual = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nome', 'role', 'precisa_aceitar_termos', 'versao_termos_atual']

    def get_nome(self, obj):
        return obj.get_full_name() or obj.username

    def get_versao_termos_atual(self, obj):
        return settings.VERSAO_TERMOS


class EsqueciSenhaSerializer(serializers.Serializer):
    email = serializers.EmailField()


class RedefinirSenhaSerializer(serializers.Serializer):
    token = serializers.CharField()
    nova_senha = serializers.CharField(min_length=6)

PAPEIS_CRIAVEIS_PELA_SECRETARIA = [
    (User.Role.ALUNO, 'Aluno'),
    (User.Role.RESPONSAVEL, 'Responsável'),
    (User.Role.PROFESSOR, 'Professor'),
]


class UsuarioListaSerializer(serializers.ModelSerializer):
    nome = serializers.SerializerMethodField()
    turma = serializers.CharField(source='turma_atual', read_only=True, default=None)

    class Meta:
        model = User
        fields = ['id', 'nome', 'email', 'role', 'turma', 'is_active', 'date_joined']

    def get_nome(self, obj):
        return obj.get_full_name() or obj.username


class CriarUsuarioSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=PAPEIS_CRIAVEIS_PELA_SECRETARIA)
    turma = serializers.PrimaryKeyRelatedField(
        queryset=Turma.objects.select_related('ano_letivo'), required=False, allow_null=True, write_only=True,
        error_messages={'does_not_exist': 'Turma não encontrada.'},
    )
    responsaveis = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=User.Role.RESPONSAVEL, is_active=True), many=True, required=False,
        write_only=True, error_messages={'does_not_exist': 'Responsável não encontrado.'},
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role', 'turma', 'responsaveis']
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
        }

    def validate_email(self, value):
        value = value.strip()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Já existe uma conta com este e-mail.')
        return value

    def validate(self, attrs):
        role = attrs['role']
        if role == User.Role.ALUNO:
            turma = attrs.get('turma')
            if turma is None:
                if not Turma.objects.filter(ano_letivo__ativo=True).exists():
                    raise serializers.ValidationError({'turma': 'Cadastre uma turma antes de cadastrar alunos.'})
                raise serializers.ValidationError({'turma': 'Selecione a turma do aluno.'})
            if not turma.ano_letivo.ativo:
                raise serializers.ValidationError({'turma': 'Selecione uma turma do ano letivo atual.'})
            if not attrs.get('responsaveis'):
                if not User.objects.filter(role=User.Role.RESPONSAVEL, is_active=True).exists():
                    raise serializers.ValidationError(
                        {'responsaveis': 'Cadastre um responsável antes de cadastrar alunos.'})
                raise serializers.ValidationError({'responsaveis': 'Selecione ao menos um responsável.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        turma = validated_data.pop('turma', None)
        responsaveis = validated_data.pop('responsaveis', [])
        usuario = User(username=validated_data['email'], **validated_data)
        usuario.set_unusable_password()
        usuario.save()
        if usuario.role == User.Role.ALUNO:
            Matricula.objects.create(aluno=usuario, turma=turma)
            VinculoResponsavel.objects.bulk_create(
                VinculoResponsavel(responsavel=responsavel, aluno=usuario) for responsavel in responsaveis
            )
        return usuario

def _nome(usuario):
    return usuario.get_full_name() or usuario.username


class UsuarioDetalheSerializer(UsuarioListaSerializer):
    matriculas = serializers.SerializerMethodField()
    vinculos = serializers.SerializerMethodField()

    class Meta(UsuarioListaSerializer.Meta):
        fields = ['id', 'nome', 'first_name', 'last_name', 'email', 'role', 'is_active', 'date_joined',
                  'matriculas', 'vinculos']

    def get_matriculas(self, obj):
        """Histórico de matrículas do aluno, da mais recente para a mais antiga (RN56)."""
        if obj.role != User.Role.ALUNO:
            return []
        return [
            {'id': m.id, 'turma_id': m.turma_id, 'turma': m.turma.nome, 'ano': m.ano_letivo.ano,
             'situacao': m.situacao, 'data_inicio': m.data_inicio, 'data_fim': m.data_fim}
            for m in obj.matriculas.select_related('turma', 'ano_letivo').order_by('-data_inicio', '-id')
        ]

    def get_vinculos(self, obj):
        """Para o aluno, os responsáveis; para o responsável, os alunos."""
        if obj.role == User.Role.ALUNO:
            pessoas = [v.responsavel for v in obj.vinculos_como_aluno.select_related('responsavel')]
        elif obj.role == User.Role.RESPONSAVEL:
            pessoas = [v.aluno for v in obj.vinculos_como_responsavel.select_related('aluno')]
        else:
            return []
        return [{'id': p.id, 'nome': _nome(p), 'email': p.email} for p in pessoas]
