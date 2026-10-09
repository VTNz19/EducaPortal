"""Testes unitários das validações do AvisoSerializer (RN26 e RN27).

O serializer é validado em memória, sem gravar nada no banco.
"""
import pytest
from rest_framework import serializers

from apps.communication.serializers import AvisoSerializer


def test_deve_aceitar_aviso_com_titulo_e_conteudo_preenchidos():
    # Arrange
    serializer = AvisoSerializer(data={'titulo': 'Reunião de pais', 'conteudo': 'Sexta-feira, às 19h.'})

    # Act
    valido = serializer.is_valid()

    # Assert
    assert valido is True
    assert serializer.validated_data['titulo'] == 'Reunião de pais'


def test_deve_lancar_erro_com_mensagem_quando_titulo_tem_apenas_espacos():
    # Arrange
    serializer = AvisoSerializer()

    # Act
    with pytest.raises(serializers.ValidationError) as erro:
        serializer.validate_titulo('   ')

    # Assert
    assert erro.value.detail == ['O título não pode ser vazio.']


def test_deve_lancar_erro_com_mensagem_quando_conteudo_tem_apenas_espacos():
    # Arrange
    serializer = AvisoSerializer()

    # Act
    with pytest.raises(serializers.ValidationError) as erro:
        serializer.validate_conteudo('\n\t ')

    # Assert
    assert erro.value.detail == ['O conteúdo não pode ser vazio.']


@pytest.mark.parametrize(
    ('tamanho', 'esperado'),
    [
        (200, True),   # exatamente no limite do campo
        (201, False),  # um caractere acima
    ],
)
def test_deve_respeitar_o_limite_de_200_caracteres_no_titulo(tamanho, esperado):
    # Arrange
    serializer = AvisoSerializer(data={'titulo': 'a' * tamanho, 'conteudo': 'Texto do aviso.'})

    # Act
    valido = serializer.is_valid()

    # Assert
    assert valido is esperado
    if not esperado:
        assert serializer.errors['titulo'][0].code == 'max_length'
