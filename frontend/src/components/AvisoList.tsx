import type { Aviso } from '../api/avisos'
import { alternarFixado, excluirAviso } from '../api/avisos'

interface AvisoListProps {
    avisos: Aviso[]
    onAvisoAtualizado: () => void
}

export function AvisoList({ avisos, onAvisoAtualizado }: AvisoListProps) {
    async function handleExcluir(id: number) {
        await excluirAviso(id)
        onAvisoAtualizado()
    }

    async function handleAlternarFixado(aviso: Aviso) {
        await alternarFixado(aviso.id, !aviso.fixado)
        onAvisoAtualizado()
    }

    if (avisos.length === 0) {
        return <p>Nenhum aviso publicado ainda.</p>
    }

    return (
        <ul>
            {avisos.map((aviso) => (
                <li key={aviso.id}>
                    {aviso.fixado && <strong>📌 Fixado</strong>}
                    <h3>{aviso.titulo}</h3>
                    <p>{aviso.conteudo}</p>
                    <small>{new Date(aviso.criado_em).toLocaleString('pt-BR')}</small>
                    <button type="button" onClick={() => handleAlternarFixado(aviso)}>
                        {aviso.fixado ? 'Desafixar' : 'Fixar'}
                    </button>
                    <button type="button" onClick={() => handleExcluir(aviso.id)}>
                        Excluir
                    </button>
                </li>
            ))}
        </ul>
    )
}
