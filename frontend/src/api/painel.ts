import api from './client'

export interface PontoEvolucao {
    bimestre: number
    media: number | null
}

export interface DisciplinaDoAluno {
    id: number
    disciplina: string
    media: number | null
    media_parcial: boolean
    abaixo_media: boolean
    faltas: number
    frequencia: number | null
    abaixo_frequencia: boolean
}

export interface PainelAluno {
    perfil: 'aluno'
    alunos: { id: number; nome: string }[]
    aluno: { id: number; nome: string } | null
    sem_dados: boolean
    ano?: number
    turma?: string
    resumo?: {
        media_geral: number | null
        frequencia_geral: number | null
        disciplinas_abaixo_media: number
        disciplinas_abaixo_frequencia: number
    }
    disciplinas?: DisciplinaDoAluno[]
    evolucao?: PontoEvolucao[]
}

export interface Pendencia {
    disciplina_id: number
    disciplina: string
    turma: string
    professor: string
    sem_nota_publicada: number
}

export interface BimestrePainel {
    numero: number
    inicio: string
    fim: string
}

export interface DisciplinaDoProfessor {
    id: number
    disciplina: string
    turma: string
    alunos: number
    media_bimestre: number | null
    abaixo_media: number
    abaixo_frequencia: number
}

export interface PainelProfessor {
    perfil: 'professor'
    sem_dados: boolean
    ano?: number
    bimestre?: BimestrePainel
    disciplinas: DisciplinaDoProfessor[]
    pendencias: Pendencia[]
}

export interface TurmaDoGestor {
    id: number
    turma: string
    alunos: number
    media_geral: number | null
    percentual_abaixo_media: number | null
    percentual_abaixo_frequencia: number | null
}

export interface PainelGestor {
    perfil: 'gestor'
    sem_dados: boolean
    contas_sem_aceite: number
    ano?: number
    bimestre?: BimestrePainel
    resumo?: {
        alunos: number
        media_geral: number | null
        percentual_abaixo_media: number | null
        percentual_abaixo_frequencia: number | null
    }
    turmas: TurmaDoGestor[]
    pendencias: Pendencia[]
    evolucao?: PontoEvolucao[]
}

export type DadosPainel = PainelAluno | PainelProfessor | PainelGestor

export type Situacao = 'abaixo_media' | 'abaixo_frequencia'

export interface AlunoNaSituacao {
    id: number
    nome: string
    media: number | null
    frequencia: number | null
}

export function formatar(valor: number | null | undefined, sufixo = '') {
    if (valor === null || valor === undefined) return '—'
    return `${valor.toFixed(1).replace('.', ',')}${sufixo}`
}

export async function obterPainel(filtros: { aluno?: number; bimestre?: number } = {}): Promise<DadosPainel> {
    return (await api.get('/painel/', { params: filtros })).data
}

export async function listarAlunosNaSituacao(disciplina: number, situacao: Situacao): Promise<AlunoNaSituacao[]> {
    return (await api.get(`/painel/disciplinas/${disciplina}/alunos/`, { params: { situacao } })).data
}
