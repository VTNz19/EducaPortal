import api from './client'

export type TipoEvento = 'prova' | 'feriado' | 'reuniao' | 'evento'

export const NOMES_TIPOS: Record<TipoEvento, string> = {
    prova: 'Prova',
    feriado: 'Feriado',
    reuniao: 'Reunião',
    evento: 'Evento escolar',
}

export interface Evento {
    id: number
    titulo: string
    tipo: TipoEvento
    tipo_nome: string
    inicio: string
    fim: string
    turma: number | null
    turma_nome: string | null
}

export interface DadosEvento {
    titulo: string
    tipo: TipoEvento
    inicio: string
    fim: string
    turma: number | null
}

export async function listarEventos(mes: string): Promise<Evento[]> {
    return (await api.get('/eventos/', { params: { mes } })).data
}

export async function criarEvento(dados: DadosEvento): Promise<Evento> {
    return (await api.post('/eventos/', dados)).data
}

export async function editarEvento(id: number, dados: DadosEvento): Promise<Evento> {
    return (await api.patch(`/eventos/${id}/`, dados)).data
}

export async function excluirEvento(id: number): Promise<void> {
    await api.delete(`/eventos/${id}/`)
}
