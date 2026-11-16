import api from './client'

export interface AnexoTarefa {
    id: number
    nome: string
    tamanho: number
}

export interface Tarefa {
    id: number
    disciplina: number
    disciplina_nome: string
    turma_nome: string
    titulo: string
    descricao: string
    prazo: string
    autor: number | null
    autor_nome: string | null
    criado_em: string
    anexos: AnexoTarefa[]
    encerrada: boolean
    email_enviado?: boolean | null
}

export interface DadosTarefa {
    disciplina: number
    titulo: string
    descricao: string
    prazo: string
    arquivos: File[]
}

export const TIPOS_ACEITOS = ['pdf', 'docx', 'png', 'jpg', 'jpeg']
export const TAMANHO_MAXIMO = 10 * 1024 * 1024

export function erroDoArquivo(arquivo: File): string | null {
    const extensao = arquivo.name.includes('.') ? arquivo.name.split('.').pop()!.toLowerCase() : ''
    if (!TIPOS_ACEITOS.includes(extensao)) {
        return `O arquivo "${arquivo.name}" foi recusado: tipo não permitido. Envie PDF, DOCX, PNG ou JPG.`
    }
    if (arquivo.size > TAMANHO_MAXIMO) {
        return `O arquivo "${arquivo.name}" foi recusado: o tamanho passa de 10 MB.`
    }
    return null
}

export function formatarData(iso: string) {
    const [ano, mes, dia] = iso.split('-')
    return `${dia}/${mes}/${ano}`
}

export function formatarTamanho(bytes: number) {
    if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1).replace('.', ',')} MB`
}

export async function listarTarefas(): Promise<Tarefa[]> {
    return (await api.get('/tarefas/')).data
}

export async function publicarTarefa(dados: DadosTarefa): Promise<Tarefa> {
    const formulario = new FormData()
    formulario.append('disciplina', String(dados.disciplina))
    formulario.append('titulo', dados.titulo)
    formulario.append('descricao', dados.descricao)
    formulario.append('prazo', dados.prazo)
    dados.arquivos.forEach((arquivo) => formulario.append('arquivos', arquivo))
    return (await api.post('/tarefas/', formulario)).data
}

export async function excluirTarefa(id: number): Promise<void> {
    await api.delete(`/tarefas/${id}/`)
}

export async function baixarAnexo(tarefa: number, anexo: AnexoTarefa): Promise<void> {
    const response = await api.get(`/tarefas/${tarefa}/anexos/${anexo.id}/`, { responseType: 'blob' })
    const url = URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = anexo.nome
    link.click()
    URL.revokeObjectURL(url)
}
