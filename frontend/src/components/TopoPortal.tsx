import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import type { Papel } from '../context/AuthContext'

const LINKS: { para: string; texto: string; papeis: Papel[] }[] = [
    { para: '/painel', texto: 'Painel', papeis: ['secretaria', 'direcao', 'professor', 'aluno', 'responsavel'] },
    { para: '/mural', texto: 'Mural', papeis: ['secretaria', 'direcao', 'professor', 'aluno', 'responsavel'] },
    { para: '/professor/notas', texto: 'Lançar notas', papeis: ['professor'] },
    { para: '/professor/chamada', texto: 'Chamada', papeis: ['professor'] },
    { para: '/boletim', texto: 'Boletim', papeis: ['aluno', 'responsavel'] },
    { para: '/secretaria', texto: 'Contas', papeis: ['secretaria', 'direcao'] },
    { para: '/secretaria/estrutura', texto: 'Estrutura acadêmica', papeis: ['secretaria', 'direcao'] },
]

export function TopoPortal() {
    const { usuario, logout } = useAuth()
    const links = LINKS.filter((l) => usuario && l.papeis.includes(usuario.role))
    return (
        <header className="mural-topbar">
            <span className="mural-logo">🎓 EducaPortal</span>
            <nav className="mural-topbar-usuario" aria-label="Navegação principal">
                {links.map((l) => (
                    <NavLink key={l.para} to={l.para} end className="mural-topbar-link">{l.texto}</NavLink>
                ))}
                {usuario && <span>{usuario.nome}</span>}
                <button type="button" onClick={logout}>Sair</button>
            </nav>
        </header>
    )
}
