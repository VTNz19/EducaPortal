from django.utils import timezone
from rest_framework import serializers

from .models import Aviso, EventoCalendario, Tarefa
from .regras import erro_das_datas_do_evento, erro_do_anexo, erro_do_prazo


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
        if (turma and request and request.user.role == 'professor'
                and not turma.disciplinas.filter(professor=request.user).exists()):
            raise serializers.ValidationError({'turma': 'Você só pode publicar avisos para turmas em que leciona.'})
        return attrs


def nome_do_autor(usuario):
    if usuario is None:
        return None
    return usuario.get_full_name() or usuario.username


def texto_obrigatorio(valor, mensagem):
    if not valor.strip():
        raise serializers.ValidationError(mensagem)
    return valor


class TarefaSerializer(serializers.ModelSerializer):
    disciplina_nome = serializers.CharField(source='disciplina.nome', read_only=True)
    turma_nome = serializers.CharField(source='disciplina.turma.nome', read_only=True)
    autor_nome = serializers.SerializerMethodField()
    anexos = serializers.SerializerMethodField()
    arquivos = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    encerrada = serializers.SerializerMethodField()

    class Meta:
        model = Tarefa
        fields = ['id', 'disciplina', 'disciplina_nome', 'turma_nome', 'titulo', 'descricao', 'prazo',
                  'autor', 'autor_nome', 'criado_em', 'anexos', 'arquivos', 'encerrada']
        read_only_fields = ['id', 'autor', 'criado_em']
        extra_kwargs = {
            'titulo': {'error_messages': {'blank': 'O título não pode ser vazio.'}},
        }

    def get_autor_nome(self, obj):
        return nome_do_autor(obj.autor)

    def get_anexos(self, obj):
        return [{'id': a.id, 'nome': a.nome_original, 'tamanho': a.tamanho} for a in obj.anexos.all()]

    def get_encerrada(self, obj):
        return obj.prazo < timezone.localdate()

    def validate_titulo(self, value):
        return texto_obrigatorio(value, 'O título não pode ser vazio.')

    def validate_prazo(self, value):
        erro = erro_do_prazo(value, timezone.localdate())
        if erro:
            raise serializers.ValidationError(erro)
        return value

    def validate_disciplina(self, value):
        request = self.context.get('request')
        if request and value.professor_id != request.user.id:
            raise serializers.ValidationError('Você só pode publicar tarefas nas disciplinas atribuídas a você.')
        return value

    def validate_arquivos(self, arquivos):
        erros = []
        for arquivo in arquivos:
            inicio = arquivo.read(8)
            arquivo.seek(0)
            erro = erro_do_anexo(arquivo.name, arquivo.size, inicio)
            if erro:
                erros.append(erro)
        if erros:
            raise serializers.ValidationError(erros)
        return arquivos


class EventoCalendarioSerializer(serializers.ModelSerializer):
    tipo_nome = serializers.CharField(source='get_tipo_display', read_only=True)
    turma_nome = serializers.CharField(source='turma.nome', read_only=True, default=None)

    class Meta:
        model = EventoCalendario
        fields = ['id', 'titulo', 'tipo', 'tipo_nome', 'inicio', 'fim', 'turma', 'turma_nome', 'criado_em']
        read_only_fields = ['id', 'criado_em']
        extra_kwargs = {
            'titulo': {'error_messages': {'blank': 'O título não pode ser vazio.'}},
        }

    def validate_titulo(self, value):
        return texto_obrigatorio(value, 'O título não pode ser vazio.')

    def validate(self, attrs):
        inicio = attrs.get('inicio', getattr(self.instance, 'inicio', None))
        fim = attrs.get('fim', getattr(self.instance, 'fim', None))
        erro = inicio and fim and erro_das_datas_do_evento(inicio, fim)
        if erro:
            raise serializers.ValidationError({'fim': erro})
        return attrs
