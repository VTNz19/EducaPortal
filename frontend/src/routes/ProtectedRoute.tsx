import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import type { Papel } from '../context/AuthContext'

interface ProtectedRouteProps {
    children: ReactNode
    papeis?: Papel[]
}

export function ProtectedRoute({ children, papeis }: ProtectedRouteProps) {
    const { usuario, carregando } = useAuth()

    if (carregando) {
        return <p>Carregando...</p>
    }

    if (!usuario) {
        return <Navigate to="/login" replace />
    }

    if (usuario.precisa_aceitar_termos) {
        return <Navigate to="/aceite-termos" replace />
    }

    if (papeis && !papeis.includes(usuario.role)) {
        return <Navigate to="/mural" replace />
    }

    return <>{children}</>
}
