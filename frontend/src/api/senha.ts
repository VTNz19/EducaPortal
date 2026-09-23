import api from './client'

export async function solicitarRedefinicaoSenha(email: string): Promise<void> {
    await api.post('/auth/esqueci-senha/', { email })
}

export async function redefinirSenha(token: string, novaSenha: string): Promise<void> {
    await api.post('/auth/redefinir-senha/', { token, nova_senha: novaSenha })
}
