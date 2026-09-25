import { Link } from 'react-router-dom'
import './RodapeLegal.css'

export function RodapeLegal() {
    return (
        <footer className="rodape-legal">
            <Link to="/termo-de-uso">Termo de Uso e Aceite</Link>
            <Link to="/politica-de-privacidade">Política de Privacidade</Link>
            <Link to="/plano-de-retencao">Plano de Retenção</Link>
            <a href="mailto:educaportal.tcc@gmail.com">Privacidade: educaportal.tcc@gmail.com</a>
        </footer>
    )
}
