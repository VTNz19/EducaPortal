import ReactMarkdown from 'react-markdown'
import type { Components } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import '../pages/LegalPage.css'

const ROTAS_DOS_DOCUMENTOS: Record<string, string> = {
    'termo-de-uso.md': '/termo-de-uso',
    'politica-de-privacidade.md': '/politica-de-privacidade',
    'plano-de-retencao.md': '/plano-de-retencao',
}

const componentes: Components = {
    a({ href = '', children }) {
        const arquivo = href.split('/').pop() ?? ''
        const rota = ROTAS_DOS_DOCUMENTOS[arquivo]
        if (rota) {
            return <Link to={rota}>{children}</Link>
        }
        return <a href={href} target="_blank" rel="noreferrer">{children}</a>
    },
}

interface DocumentoLegalProps {
    conteudo: string
}

export function ConteudoMarkdown({ conteudo }: DocumentoLegalProps) {
    return (
        <ReactMarkdown remarkPlugins={[remarkGfm]} components={componentes}>
            {conteudo}
        </ReactMarkdown>
    )
}

export function DocumentoLegal({ conteudo }: DocumentoLegalProps) {
    const { usuario } = useAuth()

    return (
        <div className="legal-page">
            <Link to={usuario ? '/mural' : '/login'} className="legal-voltar">
                &larr; {usuario ? 'Voltar para o sistema' : 'Voltar para o login'}
            </Link>
            <ConteudoMarkdown conteudo={conteudo} />
        </div>
    )
}
