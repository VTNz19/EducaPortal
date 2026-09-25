import type { Aviso } from '../api/avisos'
import { alternarFixado, excluirAviso } from '../api/avisos'

interface AvisoListProps {
    avisos: Aviso[]
    onAvisoAtualizado: () => void
    podeGerenciar: (aviso: Aviso) => boolean
}

export function AvisoList({ avisos, onAvisoAtualizado, podeGerenciar }: AvisoListProps) {
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
        <div className="aviso-grid">
            {avisos.map((aviso) => (
                <div key={aviso.id} className={`aviso-card${aviso.fixado ? ' fixado' : ''}`}>
                    {aviso.fixado && <span className="aviso-fixado-badge">📌 Fixado</span>}
                    <h3>{aviso.titulo}</h3>
                    <p>{aviso.conteudo}</p>
                    <small>
                        {aviso.autor_nome && `Por ${aviso.autor_nome} · `}
                        {new Date(aviso.criado_em).toLocaleString('pt-BR')}
                    </small>
                    {podeGerenciar(aviso) && (
                        <div className="aviso-card-acoes">
                            <button type="button" onClick={() => handleAlternarFixado(aviso)}>
                                {aviso.fixado ? 'Desafixar' : 'Fixar'}
                            </button>
                            <button type="button" onClick={() => handleExcluir(aviso.id)}>
                                Excluir
                            </button>
                        </div>
                    )}
                </div>
            ))}
        </div>
    )
}
