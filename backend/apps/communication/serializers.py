from rest_framework import serializers

from .models import Aviso


class AvisoSerializer(serializers.ModelSerializer):
    autor_nome = serializers.SerializerMethodField()

    class Meta:
        model = Aviso
        fields = ['id', 'titulo', 'conteudo', 'autor', 'autor_nome', 'criado_em', 'atualizado_em', 'fixado']
        read_only_fields = ['id', 'autor', 'criado_em', 'atualizado_em']

    def get_autor_nome(self, obj):
        if obj.autor is None:
            return None
        return obj.autor.get_full_name() or obj.autor.username

    def validate_titulo(self, value):
        if not value.strip():
            raise serializers.ValidationError('O título não pode ser vazio.')
        return value

    def validate_conteudo(self, value):
        if not value.strip():
            raise serializers.ValidationError('O conteúdo não pode ser vazio.')
        return value
