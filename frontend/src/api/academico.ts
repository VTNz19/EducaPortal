import api from './client'
import type { UsuarioDetalhe } from './usuarios'

export interface Bimestre {
    numero: number
    inicio: string
    fim: string
}

export interface AnoLetivo {
    id: number
    ano: number
    ativo: boolean
    bimestres: Bimestre[]
}

export type Turno = 'manha' | 'tarde' | 'noite' | 'integral'

export const NOMES_TURNOS: Record<Turno, string> = {
    manha: 'Manhã',
    tarde: 'Tarde',
    noite: 'Noite',
    integral: 'Integral',
}

export interface Turma {
    id: number
    ano_letivo: number
    ano: number
    nome: string
    serie: string
    turno: Turno
    turno_nome: string
    total_alunos: number
}

export interface Disciplina {
    id: number
    turma: number
    turma_nome: string
    ano: number
    nome: string
    carga_horaria: number
    professor: number
    professor_nome: string
}

export async function listarAnosLetivos(): Promise<AnoLetivo[]> {
    return (await api.get('/anos-letivos/')).data
}

export async function criarAnoLetivo(dados: Omit<AnoLetivo, 'id'>): Promise<AnoLetivo> {
    return (await api.post('/anos-letivos/', dados)).data
}

export async function ativarAnoLetivo(id: number): Promise<AnoLetivo> {
    return (await api.patch(`/anos-letivos/${id}/`, { ativo: true })).data
}

export async function listarTurmas(anoLetivo?: number): Promise<Turma[]> {
    return (await api.get('/turmas/', { params: anoLetivo ? { ano_letivo: anoLetivo } : {} })).data
}

export async function criarTurma(dados: Pick<Turma, 'ano_letivo' | 'nome' | 'serie' | 'turno'>): Promise<Turma> {
    return (await api.post('/turmas/', dados)).data
}

export async function excluirTurma(id: number): Promise<void> {
    await api.delete(`/turmas/${id}/`)
}

export async function listarDisciplinas(turma?: number): Promise<Disciplina[]> {
    return (await api.get('/disciplinas/', { params: turma ? { turma } : {} })).data
}

export async function criarDisciplina(
    dados: Pick<Disciplina, 'turma' | 'nome' | 'carga_horaria' | 'professor'>,
): Promise<Disciplina> {
    return (await api.post('/disciplinas/', dados)).data
}

export async function trocarProfessor(id: number, professor: number): Promise<Disciplina> {
    return (await api.patch(`/disciplinas/${id}/`, { professor })).data
}

export async function excluirDisciplina(id: number): Promise<void> {
    await api.delete(`/disciplinas/${id}/`)
}

export async function transferirAluno(aluno: number, turma: number): Promise<UsuarioDetalhe> {
    return (await api.post(`/alunos/${aluno}/transferir/`, { turma })).data
}

export async function rematricularAluno(aluno: number, turma: number): Promise<UsuarioDetalhe> {
    return (await api.post(`/alunos/${aluno}/rematricular/`, { turma })).data
}

export async function vincularResponsavel(aluno: number, responsavel: number): Promise<UsuarioDetalhe> {
    return (await api.post(`/alunos/${aluno}/vincular/`, { responsavel })).data
}

export async function desvincularResponsavel(
    aluno: number, responsavel: number, confirmar = false,
): Promise<UsuarioDetalhe> {
    return (await api.post(`/alunos/${aluno}/desvincular/`, { responsavel, confirmar })).data
}
