import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import termo from '../../../docs/termo-de-uso.md?raw'
import { ConteudoMarkdown } from '../components/DocumentoLegal'
import { useAuth } from '../context/AuthContext'
import './LegalPage.css'

export function AceiteTermos() {
    const { usuario, carregando, aceitarTermos, logout } = useAuth()
    const [marcado, setMarcado] = useState(false)
    const [enviando, setEnviando] = useState(false)
    const [erro, setErro] = useState('')

    if (carregando) {
        return <p>Carregando...</p>
    }
    if (!usuario) {
        return <Navigate to="/login" replace />
    }
    if (!usuario.precisa_aceitar_termos) {
        return <Navigate to="/mural" replace />
    }

    async function handleAceitar() {
        setErro('')
        setEnviando(true)
        try {
            await aceitarTermos()
        } catch {
            setErro('Não foi possível registrar o aceite. Recarregue a página e tente novamente.')
        } finally {
            setEnviando(false)
        }
    }

    return (
        <div className="legal-page">
            <p className="aceite-intro">
                Olá, <strong>{usuario.nome}</strong>. Para usar o EducaPortal, leia e aceite
                o Termo de Uso e Aceite (versão {usuario.versao_termos_atual}). Se você é
                menor de idade, leia junto com o seu responsável.
            </p>

            <div className="aceite-documento">
                <ConteudoMarkdown conteudo={termo} />
            </div>

            <label className="aceite-confirmacao">
                <input
                    type="checkbox"
                    checked={marcado}
                    onChange={(e) => setMarcado(e.target.checked)}
                />
                <span>
                    Li e aceito o Termo de Uso e Aceite e estou ciente da{' '}
                    <Link to="/politica-de-privacidade">Política de Privacidade</Link>.
                </span>
            </label>

            {erro && <p className="aceite-erro" role="alert">{erro}</p>}

            <div className="aceite-acoes">
                <button
                    type="button"
                    className="aceite-botao"
                    disabled={!marcado || enviando}
                    onClick={handleAceitar}
                >
                    {enviando ? 'Registrando...' : 'Aceitar e continuar'}
                </button>
                <button type="button" className="aceite-sair" onClick={logout}>
                    Sair
                </button>
            </div>
        </div>
    )
}
