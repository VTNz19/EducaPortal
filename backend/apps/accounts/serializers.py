from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
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

    class Meta:
        model = User
        fields = ['id', 'nome', 'email', 'role', 'is_active', 'date_joined']

    def get_nome(self, obj):
        return obj.get_full_name() or obj.username


class CriarUsuarioSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=PAPEIS_CRIAVEIS_PELA_SECRETARIA)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'role']
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
        }

    def validate_email(self, value):
        value = value.strip()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Já existe uma conta com este e-mail.')
        return value

    def create(self, validated_data):
        usuario = User(username=validated_data['email'], **validated_data)
        usuario.set_unusable_password()
        usuario.save()
        return usuario

class UsuarioDetalheSerializer(UsuarioListaSerializer):
    class Meta(UsuarioListaSerializer.Meta):
        fields = ['id', 'nome', 'first_name', 'last_name', 'email', 'role', 'is_active', 'date_joined']
