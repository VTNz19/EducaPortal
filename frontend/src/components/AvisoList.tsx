import type { Aviso } from '../api/avisos'
import { excluirAviso } from '../api/avisos'

interface AvisoListProps {
    avisos: Aviso[]
    onAvisoExcluido: () => void
}

export function AvisoList({ avisos, onAvisoExcluido }: AvisoListProps) {
    async function handleExcluir(id: number) {
        await excluirAviso(id)
        onAvisoExcluido()
    }

    if (avisos.length === 0) {
        return <p>Nenhum aviso publicado ainda.</p>
    }

    return (
        <ul>
            {avisos.map((aviso) => (
                <li key={aviso.id}>
                    <h3>{aviso.titulo}</h3>
                    <p>{aviso.conteudo}</p>
                    <small>{new Date(aviso.criado_em).toLocaleString('pt-BR')}</small>
                    <button type="button" onClick={() => handleExcluir(aviso.id)}>
                        Excluir
                    </button>
                </li>
            ))}
        </ul>
    )
}
