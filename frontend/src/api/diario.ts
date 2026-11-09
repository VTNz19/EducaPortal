import api from './client'

export interface BimestreInfo {
    numero: number
    inicio: string
    fim: string
}

export interface DisciplinaInfo {
    id: number
    nome: string
    turma: string
}

export interface NotaAluno {
    matricula: number
    aluno_id: number
    nome: string
    valor: number | null
    publicada: boolean
}

export interface EstadoNotas {
    disciplina: DisciplinaInfo
    bimestre: BimestreInfo
    alunos: NotaAluno[]
    sem_nota: number
    pendentes_publicacao: number
    email_enviado?: boolean
}

export async function obterNotas(disciplina: number, bimestre?: number): Promise<EstadoNotas> {
    return (await api.get(`/diario/${disciplina}/notas/`, { params: bimestre ? { bimestre } : {} })).data
}

export async function salvarNotas(
    disciplina: number, bimestre: number, notas: { matricula: number; valor: string | null }[],
): Promise<EstadoNotas> {
    return (await api.post(`/diario/${disciplina}/notas/`, { bimestre, notas })).data
}

export async function publicarNotas(disciplina: number, bimestre: number, confirmar = false): Promise<EstadoNotas> {
    return (await api.post(`/diario/${disciplina}/publicar-notas/`, { bimestre, confirmar })).data
}

export interface PresencaAluno {
    matricula: number
    aluno_id: number
    nome: string
    presente: boolean
}

export interface EstadoChamada {
    disciplina: DisciplinaInfo
    data: string
    bimestre: BimestreInfo
    existente: boolean
    quantidade_aulas: number
    alunos: PresencaAluno[]
    email_enviado?: boolean | null
}

export async function obterChamada(disciplina: number, data: string): Promise<EstadoChamada> {
    return (await api.get(`/diario/${disciplina}/chamada/`, { params: { data } })).data
}

export async function registrarChamada(
    disciplina: number, data: string, quantidade_aulas: number, ausentes: number[],
): Promise<EstadoChamada> {
    return (await api.post(`/diario/${disciplina}/chamada/`, { data, quantidade_aulas, ausentes })).data
}

export interface LinhaBoletim {
    disciplina_id: number
    disciplina: string
    professor: string
    notas: Record<'1' | '2' | '3' | '4', number | null>
    media: number | null
    media_parcial: boolean
    abaixo_media: boolean
    aulas: number
    faltas: number
    frequencia: number | null
    abaixo_frequencia: boolean
}

export interface Boletim {
    aluno: { id: number; nome: string }
    ano: number
    turma: string
    situacao_matricula: string
    disciplinas: LinhaBoletim[]
    anos: number[]
}

export async function listarAlunosDoBoletim(): Promise<{ id: number; nome: string }[]> {
    return (await api.get('/boletim/alunos/')).data
}

export async function obterBoletim(aluno: number, ano?: number): Promise<Boletim> {
    return (await api.get(`/boletim/${aluno}/`, { params: ano ? { ano } : {} })).data
}

export async function baixarBoletimPdf(aluno: number, ano?: number): Promise<void> {
    const response = await api.get(`/boletim/${aluno}/pdf/`, { params: ano ? { ano } : {}, responseType: 'blob' })
    const nome = /filename="([^"]+)"/.exec(response.headers['content-disposition'] ?? '')?.[1] ?? 'boletim.pdf'
    const url = URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = nome
    link.click()
    URL.revokeObjectURL(url)
}
