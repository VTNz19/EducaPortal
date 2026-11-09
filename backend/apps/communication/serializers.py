from django.utils import timezone
from rest_framework import serializers

from .models import Aviso


class AvisoSerializer(serializers.ModelSerializer):
    autor_nome = serializers.SerializerMethodField()
    turma_nome = serializers.CharField(source='turma.nome', read_only=True, default=None)
    situacao = serializers.CharField(read_only=True)

    class Meta:
        model = Aviso
        fields = ['id', 'titulo', 'conteudo', 'autor', 'autor_nome', 'criado_em', 'atualizado_em', 'fixado',
                  'turma', 'turma_nome', 'inicio_exibicao', 'fim_exibicao', 'notificar_email', 'situacao']
        read_only_fields = ['id', 'autor', 'criado_em', 'atualizado_em']
        extra_kwargs = {
            'titulo': {'error_messages': {'blank': 'O título não pode ser vazio.'}},
            'conteudo': {'error_messages': {'blank': 'O conteúdo não pode ser vazio.'}},
        }

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

    def validate(self, attrs):
        inicio = attrs.get('inicio_exibicao', getattr(self.instance, 'inicio_exibicao', None)) or timezone.localdate()
        fim = attrs.get('fim_exibicao', getattr(self.instance, 'fim_exibicao', None))
        if inicio and fim and fim < inicio:
            raise serializers.ValidationError(
                {'fim_exibicao': 'A data de fim deve ser igual ou posterior à data de início.'})

        turma = attrs.get('turma')
        request = self.context.get('request')
        if turma and request and request.user.role == 'professor':
            if not turma.disciplinas.filter(professor=request.user).exists():
                raise serializers.ValidationError({'turma': 'Você só pode publicar avisos para turmas em que leciona.'})
        return attrs
