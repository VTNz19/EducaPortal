"""Regras de negócio do módulo acadêmico que não dependem do banco de dados."""


def erros_dos_bimestres(bimestres):
    """Verifica a RN50 e devolve a lista de erros (vazia quando os bimestres são válidos).

    `bimestres` é uma lista de dicionários com `numero`, `inicio` e `fim`.
    """
    numeros = sorted(b['numero'] for b in bimestres)
    if numeros != [1, 2, 3, 4]:
        return ['Informe os 4 bimestres do ano letivo, numerados de 1 a 4.']

    erros = []
    ordenados = sorted(bimestres, key=lambda b: b['numero'])
    for b in ordenados:
        if b['fim'] < b['inicio']:
            erros.append(f'O fim do {b["numero"]}º bimestre não pode ser anterior ao início.')
    for anterior, atual in zip(ordenados, ordenados[1:], strict=False):
        if atual['inicio'] <= anterior['fim']:
            erros.append(
                f'O {atual["numero"]}º bimestre deve começar depois do fim do {anterior["numero"]}º bimestre.'
            )
    return erros
