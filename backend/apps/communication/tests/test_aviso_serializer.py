"""Testes unitários das validações do AvisoSerializer (RN29 e RN30).

O serializer é validado em memória, sem gravar nada no banco.
"""
import pytest
from rest_framework import serializers

from apps.communication.serializers import AvisoSerializer


def test_deve_aceitar_aviso_com_titulo_e_conteudo_preenchidos():
    serializer = AvisoSerializer(data={'titulo': 'Reunião de pais', 'conteudo': 'Sexta-feira, às 19h.'})

    valido = serializer.is_valid()

    assert valido is True
    assert serializer.validated_data['titulo'] == 'Reunião de pais'


def test_deve_lancar_erro_com_mensagem_quando_titulo_tem_apenas_espacos():
    serializer = AvisoSerializer()

    with pytest.raises(serializers.ValidationError) as erro:
        serializer.validate_titulo('   ')

    assert erro.value.detail == ['O título não pode ser vazio.']


def test_deve_lancar_erro_com_mensagem_quando_conteudo_tem_apenas_espacos():
    serializer = AvisoSerializer()

    with pytest.raises(serializers.ValidationError) as erro:
        serializer.validate_conteudo('\n\t ')

    assert erro.value.detail == ['O conteúdo não pode ser vazio.']


@pytest.mark.parametrize(
    ('tamanho', 'esperado'),
    [
        (200, True),
        (201, False),
    ],
)
def test_deve_respeitar_o_limite_de_200_caracteres_no_titulo(tamanho, esperado):
    serializer = AvisoSerializer(data={'titulo': 'a' * tamanho, 'conteudo': 'Texto do aviso.'})

    valido = serializer.is_valid()

    assert valido is esperado
    if not esperado:
        assert serializer.errors['titulo'][0].code == 'max_length'
