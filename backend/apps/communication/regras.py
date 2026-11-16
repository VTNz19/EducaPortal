"""Regras de tarefas e do calendário que não dependem do banco de dados (RN75 a RN77)."""

TAMANHO_MAXIMO_ANEXO = 10 * 1024 * 1024

ASSINATURAS = {
    'pdf': (b'%PDF',),
    'docx': (b'PK\x03\x04',),
    'png': (b'\x89PNG\r\n\x1a\n',),
    'jpg': (b'\xff\xd8\xff',),
    'jpeg': (b'\xff\xd8\xff',),
}


def extensao_de(nome):
    return nome.rsplit('.', 1)[-1].lower() if '.' in nome else ''


def erro_do_anexo(nome, tamanho, inicio):
    """Devolve o motivo da recusa do arquivo, ou None quando ele é aceito (RN75).

    `inicio` são os primeiros bytes do arquivo: a extensão precisa bater com o conteúdo,
    para que um executável renomeado para .pdf não seja aceito.
    """
    extensao = extensao_de(nome)
    if extensao not in ASSINATURAS:
        return f'O arquivo "{nome}" foi recusado: tipo não permitido. Envie PDF, DOCX, PNG ou JPG.'
    if tamanho > TAMANHO_MAXIMO_ANEXO:
        return f'O arquivo "{nome}" foi recusado: o tamanho passa de 10 MB.'
    if not inicio.startswith(ASSINATURAS[extensao]):
        return f'O arquivo "{nome}" foi recusado: o conteúdo não é de um arquivo {extensao.upper()}.'
    return None


def erro_do_prazo(prazo, hoje):
    """RN76: o prazo de entrega não pode ser anterior à data de publicação."""
    if prazo < hoje:
        return 'O prazo de entrega não pode ser anterior a hoje.'
    return None


def erro_das_datas_do_evento(inicio, fim):
    """RN77: a data de término não pode ser anterior à data de início."""
    if fim < inicio:
        return 'A data de término não pode ser anterior à data de início.'
    return None
