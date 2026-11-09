import api from './client'
import type { Papel } from '../context/AuthContext'

export const NOMES_PAPEIS: Record<string, string> = {
    secretaria: 'Secretaria',
    direcao: 'Direção',
    professor: 'Professor',
    aluno: 'Aluno',
    responsavel: 'Responsável',
}

export interface UsuarioResumo {
    id: number
    nome: string
    email: string
    role: Papel
    turma: string | null
    is_active: boolean
    date_joined: string
}

export interface MatriculaResumo {
    id: number
    turma_id: number
    turma: string
    ano: number
    situacao: 'ativa' | 'transferida' | 'encerrada'
    data_inicio: string
    data_fim: string | null
}

export interface PessoaVinculada {
    id: number
    nome: string
    email: string
}

export interface UsuarioDetalhe extends UsuarioResumo {
    first_name: string
    last_name: string
    matriculas: MatriculaResumo[]
    vinculos: PessoaVinculada[]
}

export interface NovoUsuario {
    first_name: string
    last_name: string
    email: string
    role: 'aluno' | 'responsavel' | 'professor'
    turma?: number | null
    responsaveis?: number[]
}

export interface FiltrosUsuarios {
    busca?: string
    role?: string
    turma?: number | ''
    ativo?: 'true' | 'false' | ''
    page_size?: number
}

export interface PaginaUsuarios {
    total: number
    usuarios: UsuarioResumo[]
}

export interface UsuarioCriado extends UsuarioResumo {
    email_enviado: boolean
}

export interface RegistroLog {
    id: number
    acao: string
    detalhes: string
    endereco_ip: string | null
    criado_em: string
}

export interface ExportacaoUsuario {
    gerado_em: string
    gerado_por: string
    usuario: UsuarioDetalhe
    logs: RegistroLog[]
}

export async function listarUsuarios(filtros: FiltrosUsuarios = {}): Promise<PaginaUsuarios> {
    const params = Object.fromEntries(Object.entries(filtros).filter(([, v]) => v !== '' && v !== undefined))
    const response = await api.get('/usuarios/', { params })
    return { total: response.data.count ?? response.data.length, usuarios: response.data.results ?? response.data }
}

export async function listarPorPerfil(role: string): Promise<UsuarioResumo[]> {
    return (await listarUsuarios({ role, ativo: 'true', page_size: 500 })).usuarios
}

export async function criarUsuario(dados: NovoUsuario): Promise<UsuarioCriado> {
    const response = await api.post('/usuarios/', dados)
    return response.data
}

export async function buscarUsuario(id: number): Promise<UsuarioDetalhe> {
    const response = await api.get(`/usuarios/${id}/`)
    return response.data
}

export async function listarLogsUsuario(id: number): Promise<RegistroLog[]> {
    const response = await api.get(`/usuarios/${id}/logs/`)
    return response.data
}

export async function exportarDadosUsuario(id: number): Promise<ExportacaoUsuario> {
    const response = await api.get(`/usuarios/${id}/exportar/`)
    return response.data
}
