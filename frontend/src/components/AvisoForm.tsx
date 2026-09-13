import { useState } from 'react'
import { criarAviso } from '../api/avisos'

interface AvisoFormProps {
    onAvisoCriado: () => void
}

export function AvisoForm({ onAvisoCriado }: AvisoFormProps) {
    const [titulo, setTitulo] = useState('')
    const [conteudo, setConteudo] = useState('')
    const [enviando, setEnviando] = useState(false)
    const [erro, setErro] = useState('')

    async function handleSubmit(event: React.FormEvent) {
        event.preventDefault()
        setErro('')
        setEnviando(true)
        try {
            await criarAviso(titulo, conteudo)
            setTitulo('')
            setConteudo('')
            onAvisoCriado()
        } catch {
            setErro('Não foi possível publicar o aviso. Verifique os campos e tente novamente.')
        } finally {
            setEnviando(false)
        }
    }

    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label htmlFor="titulo">Título</label>
                <input
                    id="titulo"
                    type="text"
                    value={titulo}
                    onChange={(event) => setTitulo(event.target.value)}
                    required
                />
            </div>
            <div>
                <label htmlFor="conteudo">Conteúdo</label>
                <textarea
                    id="conteudo"
                    value={conteudo}
                    onChange={(event) => setConteudo(event.target.value)}
                    required
                />
            </div>
            {erro && <p role="alert">{erro}</p>}
            <button type="submit" disabled={enviando}>
                {enviando ? 'Publicando...' : 'Publicar aviso'}
            </button>
        </form>
    )
}
