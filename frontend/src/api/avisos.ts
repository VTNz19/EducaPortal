import axios from "axios";

const API_URL = 'http://localhost:8000/api/v1/avisos/'

export interface Aviso {
    id: number;
    titulo: string
    conteudo: string
    fixado: boolean
    criado_em: string
    atualizado_em: string
}

export async function listarAvisos(): Promise<Aviso[]> {
    const response = await axios.get(API_URL)
    return response.data.results ?? response.data
}

export async function criarAviso(titulo: string, conteudo: string): Promise<Aviso> {
    const response = await axios.post(API_URL, { titulo, conteudo })
    return response.data
}

export async function excluirAviso(id: number): Promise<void> {
    await axios.delete(`${API_URL}${id}/`)
}

export async function alternarFixado(id: number, fixado: boolean): Promise<Aviso> {
    const response = await axios.patch(`${API_URL}${id}/`, { fixado })
    return response.data
}
