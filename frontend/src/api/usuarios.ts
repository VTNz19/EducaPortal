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
    is_active: boolean
    date_joined: string
}

export interface UsuarioDetalhe extends UsuarioResumo {
    first_name: string
    last_name: string
}

export interface NovoUsuario {
    first_name: string
    last_name: string
    email: string
    role: 'aluno' | 'responsavel' | 'professor'
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

export async function listarUsuarios(): Promise<UsuarioResumo[]> {
    const response = await api.get('/usuarios/')
    return response.data.results ?? response.data
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
