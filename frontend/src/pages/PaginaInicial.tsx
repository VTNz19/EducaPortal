import { Link } from 'react-router-dom'
import './PaginaInicial.css'
import { RodapeLegal } from '../components/RodapeLegal'


export function PaginaInicial() {
    return (
        <div className="inicial-page">
            <header className="inicial-header">
                <span className="inicial-logo">🎓 EducaPortal</span>
                <Link to="/login" className="inicial-login-botao">LOGIN</Link>
            </header>

            <main className="inicial-hero">
                <span className="inicial-hero-tag">Portal educacional</span>
                <h1>Menos dificuldades no seu ensino</h1>
                <p>
                    O EducaPortal automatiza notas, faltas e boletins, e
                    centraliza a comunicação entre professores, alunos e
                    responsáveis — numa única plataforma web.
                </p>
            </main>
            <RodapeLegal />
        </div>
    )
}
