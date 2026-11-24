import api from './client'

export type TipoDocumento = 'termo' | 'politica'

export const NOMES_DOCUMENTOS: Record<TipoDocumento, string> = {
    termo: 'Termo de Uso e Aceite',
    politica: 'Política de Privacidade',
}

export interface DocumentoPublicado {
    tipo: TipoDocumento
    nome: string
    versao: string
    /** Nulo enquanto a Direção não publicou nenhuma versão pelo portal: vale o texto que acompanha o sistema. */
    conteudo: string | null
    resumo: string | null
    publicado_em: string | null
    publicado_por: string | null
}

export type VersaoDocumento = Omit<DocumentoPublicado, 'conteudo'>

export async function obterDocumento(tipo: TipoDocumento): Promise<DocumentoPublicado> {
    return (await api.get(`/documentos/${tipo}/`)).data
}

export async function publicarDocumento(tipo: TipoDocumento, conteudo: string, resumo: string): Promise<DocumentoPublicado> {
    return (await api.post(`/documentos/${tipo}/`, { conteudo, resumo })).data
}

export async function listarVersoes(tipo: TipoDocumento): Promise<VersaoDocumento[]> {
    return (await api.get(`/documentos/${tipo}/versoes/`)).data
}

/** Sobe o último número da versão, como o servidor faz ao publicar: 2.2 -> 2.3. */
export function proximaVersao(versao: string): string {
    const partes = versao.split('.')
    if (!partes.every((p) => /^\d+$/.test(p))) return `${versao}.1`
    partes[partes.length - 1] = String(Number(partes[partes.length - 1]) + 1)
    return partes.join('.')
}
