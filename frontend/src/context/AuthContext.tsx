import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import api, { setAccessToken, REFRESH_TOKEN_KEY } from '../api/client'

export interface Usuario {
    id: number
    username: string
    email: string
    nome: string
    role: 'admin' | 'professor' | 'aluno'
}

interface AuthContextData {
    usuario: Usuario | null
    carregando: boolean
    login: (email: string, senha: string) => Promise<void>
    logout: () => void
}

const AuthContext = createContext<AuthContextData | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
    const [usuario, setUsuario] = useState<Usuario | null>(null)
    const [carregando, setCarregando] = useState(true)

    async function carregarUsuarioAtual() {
        const response = await api.get('/auth/me/')
        setUsuario(response.data)
    }

    useEffect(() => {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
        if (!refreshToken) {
            setCarregando(false)
            return
        }
        api.post('/auth/refresh/', { refresh: refreshToken })
            .then((response) => {
                setAccessToken(response.data.access)
                return carregarUsuarioAtual()
            })
            .catch(() => {
                localStorage.removeItem(REFRESH_TOKEN_KEY)
            })
            .finally(() => setCarregando(false))
    }, [])

    async function login(email: string, senha: string) {
        const response = await api.post('/auth/login/', { email, password: senha })
        const { access, refresh } = response.data
        setAccessToken(access)
        // Limitação de segurança: o ideal seria um cookie httpOnly para o
        // refresh token (inacessível a JavaScript, mais resistente a XSS).
        // Aqui usamos localStorage por simplicidade, já que o back-end
        // ainda não expõe um endpoint que defina cookies httpOnly.
        localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
        await carregarUsuarioAtual()
    }

    function logout() {
        setAccessToken(null)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        setUsuario(null)
    }

    return (
        <AuthContext.Provider value={{ usuario, carregando, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth deve ser usado dentro de um AuthProvider')
    }
    return context
}
