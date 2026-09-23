import api from './client'

export interface Aviso {
    id: number;
    titulo: string
    conteudo: string
    fixado: boolean
    criado_em: string
    atualizado_em: string
}

export async function listarAvisos(): Promise<Aviso[]> {
    const response = await api.get('/avisos/')
    return response.data.results ?? response.data
}

export async function criarAviso(titulo: string, conteudo: string): Promise<Aviso> {
    const response = await api.post('/avisos/', { titulo, conteudo })
    return response.data
}

export async function excluirAviso(id: number): Promise<void> {
    await api.delete(`/avisos/${id}/`)
}

export async function alternarFixado(id: number, fixado: boolean): Promise<Aviso> {
    const response = await api.patch(`/avisos/${id}/`, { fixado })
    return response.data
}
