import { useState } from 'react'
import type { Aviso } from '../api/avisos'
import { alternarFixado, excluirAviso } from '../api/avisos'
import { AvisoForm } from './AvisoForm'
import type { OpcaoTurma } from './AvisoForm'

interface AvisoListProps {
    avisos: Aviso[]
    turmas: OpcaoTurma[]
    onAvisoAtualizado: () => void
    podeGerenciar: (aviso: Aviso) => boolean
}

function dataBR(iso: string) {
    return new Date(`${iso}T00:00:00`).toLocaleDateString('pt-BR')
}

const ROTULO_SITUACAO = { agendado: 'Agendado', encerrado: 'Encerrado', vigente: '' }

export function AvisoList({ avisos, turmas, onAvisoAtualizado, podeGerenciar }: AvisoListProps) {
    const [editando, setEditando] = useState<number | null>(null)

    async function handleExcluir(aviso: Aviso) {
        if (!window.confirm(`Excluir o aviso "${aviso.titulo}"?`)) return
        await excluirAviso(aviso.id)
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
                <div key={aviso.id} className={`aviso-card${aviso.fixado ? ' fixado' : ''}${aviso.situacao !== 'vigente' ? ' fora-do-periodo' : ''}`}>
                    {editando === aviso.id ? (
                        <AvisoForm
                            turmas={turmas}
                            aviso={aviso}
                            onSalvo={() => { setEditando(null); onAvisoAtualizado() }}
                            onCancelar={() => setEditando(null)}
                        />
                    ) : (
                        <>
                            <div className="aviso-etiquetas">
                                {aviso.fixado && <span className="aviso-fixado-badge">📌 Fixado</span>}
                                <span className="aviso-etiqueta">{aviso.turma_nome ? `Turma ${aviso.turma_nome}` : 'Toda a escola'}</span>
                                {aviso.situacao !== 'vigente' && (
                                    <span className="aviso-etiqueta aviso-etiqueta-alerta">{ROTULO_SITUACAO[aviso.situacao]}</span>
                                )}
                            </div>
                            <h3>{aviso.titulo}</h3>
                            <p>{aviso.conteudo}</p>
                            <small>
                                {aviso.autor_nome && `Por ${aviso.autor_nome} · `}
                                {new Date(aviso.criado_em).toLocaleString('pt-BR')}
                                {(aviso.situacao !== 'vigente' || aviso.fim_exibicao) &&
                                    ` · Exibição: ${dataBR(aviso.inicio_exibicao)}${aviso.fim_exibicao ? ` a ${dataBR(aviso.fim_exibicao)}` : ' em diante'}`}
                            </small>
                            {podeGerenciar(aviso) && (
                                <div className="aviso-card-acoes">
                                    <button type="button" onClick={() => setEditando(aviso.id)}>Editar</button>
                                    <button type="button" onClick={() => handleAlternarFixado(aviso)}>
                                        {aviso.fixado ? 'Desafixar' : 'Fixar'}
                                    </button>
                                    <button type="button" onClick={() => handleExcluir(aviso)}>Excluir</button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            ))}
        </div>
    )
}
