import { isAxiosError } from 'axios'

export function mensagemDeErro(error: unknown, padrao: string): string {
    if (isAxiosError(error) && error.response?.data && typeof error.response.data === 'object') {
        const mensagens = Object.values(error.response.data as Record<string, unknown>)
            .flat()
            .filter((m) => typeof m === 'string')
        if (mensagens.length > 0) return mensagens.join(' ')
    }
    return padrao
}
