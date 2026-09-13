from rest_framework import serializers

from .models import Aviso


class AvisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aviso
        fields = ['id', 'titulo', 'conteudo', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def validate_titulo(self, value):
        if not value.strip():
            raise serializers.ValidationError('O título não pode ser vazio.')
        return value

    def validate_conteudo(self, value):
        if not value.strip():
            raise serializers.ValidationError('O conteúdo não pode ser vazio.')
        return value
