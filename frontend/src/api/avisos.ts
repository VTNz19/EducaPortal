import api from './client'

export type SituacaoAviso = 'vigente' | 'agendado' | 'encerrado'

export interface Aviso {
    id: number
    titulo: string
    conteudo: string
    autor: number | null
    autor_nome: string | null
    fixado: boolean
    criado_em: string
    atualizado_em: string
    turma: number | null
    turma_nome: string | null
    inicio_exibicao: string
    fim_exibicao: string | null
    notificar_email: boolean
    situacao: SituacaoAviso
}

export interface DadosAviso {
    titulo: string
    conteudo: string
    turma: number | null
    inicio_exibicao: string
    fim_exibicao: string | null
    notificar_email?: boolean
}


export async function listarAvisos(): Promise<Aviso[]> {
    const response = await api.get('/avisos/')
    return response.data.results ?? response.data
}

export async function criarAviso(dados: DadosAviso): Promise<Aviso> {
    const response = await api.post('/avisos/', dados)
    return response.data
}

export async function editarAviso(id: number, dados: DadosAviso): Promise<Aviso> {
    const response = await api.patch(`/avisos/${id}/`, dados)
    return response.data
}

export async function excluirAviso(id: number): Promise<void> {
    await api.delete(`/avisos/${id}/`)
}

export async function alternarFixado(id: number, fixado: boolean): Promise<Aviso> {
    const response = await api.patch(`/avisos/${id}/`, { fixado })
    return response.data
}
