import { useState } from 'react'
import { criarAviso, editarAviso } from '../api/avisos'
import type { Aviso, DadosAviso } from '../api/avisos'
import { mensagemDeErro } from '../api/erros'

export interface OpcaoTurma {
    id: number
    nome: string
}

interface AvisoFormProps {
    turmas: OpcaoTurma[]
    aviso?: Aviso | null
    onSalvo: () => void
    onCancelar?: () => void
}

function hojeISO() {
    const hoje = new Date()
    hoje.setMinutes(hoje.getMinutes() - hoje.getTimezoneOffset())
    return hoje.toISOString().slice(0, 10)
}

export function AvisoForm({ turmas, aviso, onSalvo, onCancelar }: AvisoFormProps) {
    const editando = Boolean(aviso)
    const [titulo, setTitulo] = useState(aviso?.titulo ?? '')
    const [conteudo, setConteudo] = useState(aviso?.conteudo ?? '')
    const [turma, setTurma] = useState<number | null>(aviso?.turma ?? null)
    const [inicio, setInicio] = useState(aviso?.inicio_exibicao ?? hojeISO())
    const [fim, setFim] = useState(aviso?.fim_exibicao ?? '')
    const [notificar, setNotificar] = useState(false)
    const [enviando, setEnviando] = useState(false)
    const [erro, setErro] = useState('')

    async function handleSubmit(event: React.FormEvent) {
        event.preventDefault()
        setErro('')
        if (!titulo.trim() || !conteudo.trim()) {
            setErro(!titulo.trim() ? 'O título não pode ser vazio.' : 'O conteúdo não pode ser vazio.')
            return
        }
        if (fim && fim < inicio) {
            setErro('A data de fim deve ser igual ou posterior à data de início.')
            return
        }
        setEnviando(true)
        try {
            const dados: DadosAviso = { titulo, conteudo, turma, inicio_exibicao: inicio, fim_exibicao: fim || null }
            if (aviso) {
                await editarAviso(aviso.id, dados)
            } else {
                await criarAviso({ ...dados, notificar_email: notificar })
                setTitulo('')
                setConteudo('')
                setFim('')
                setNotificar(false)
            }
            onSalvo()
        } catch (error) {
            setErro(mensagemDeErro(error, 'Não foi possível salvar o aviso. Verifique os campos e tente novamente.'))
        } finally {
            setEnviando(false)
        }
    }

    return (
        <form className="aviso-form" onSubmit={handleSubmit}>
            <div className="aviso-form-campo">
                <label htmlFor={`titulo-${aviso?.id ?? 'novo'}`}>Título</label>
                <input id={`titulo-${aviso?.id ?? 'novo'}`} type="text" maxLength={200} value={titulo}
                    onChange={(event) => setTitulo(event.target.value)} required />
            </div>
            <div className="aviso-form-campo">
                <label htmlFor={`conteudo-${aviso?.id ?? 'novo'}`}>Conteúdo</label>
                <textarea id={`conteudo-${aviso?.id ?? 'novo'}`} value={conteudo}
                    onChange={(event) => setConteudo(event.target.value)} required />
            </div>
            <div className="aviso-form-linha">
                <div className="aviso-form-campo">
                    <label htmlFor={`destino-${aviso?.id ?? 'novo'}`}>Destino</label>
                    <select id={`destino-${aviso?.id ?? 'novo'}`} value={turma ?? ''}
                        onChange={(event) => setTurma(event.target.value ? Number(event.target.value) : null)}>
                        <option value="">Toda a escola</option>
                        {turmas.map((t) => <option key={t.id} value={t.id}>Turma {t.nome}</option>)}
                    </select>
                </div>
                <div className="aviso-form-campo">
                    <label htmlFor={`inicio-${aviso?.id ?? 'novo'}`}>Exibir a partir de</label>
                    <input id={`inicio-${aviso?.id ?? 'novo'}`} type="date" value={inicio} required
                        onChange={(event) => setInicio(event.target.value)} />
                </div>
                <div className="aviso-form-campo">
                    <label htmlFor={`fim-${aviso?.id ?? 'novo'}`}>Até (opcional)</label>
                    <input id={`fim-${aviso?.id ?? 'novo'}`} type="date" value={fim} min={inicio}
                        onChange={(event) => setFim(event.target.value)} />
                </div>
            </div>
            {!editando && (
                <label className="aviso-form-opcao">
                    <input type="checkbox" checked={notificar} onChange={(event) => setNotificar(event.target.checked)} />
                    Avisar os destinatários por e-mail (só o título e o link; avisos agendados são enviados na data de início)
                </label>
            )}
            {erro && <p className="aviso-form-erro" role="alert">{erro}</p>}
            <div className="aviso-form-botoes">
                <button type="submit" className="aviso-form-botao" disabled={enviando}>
                    {enviando ? 'Salvando...' : editando ? 'Salvar alterações' : 'Publicar aviso'}
                </button>
                {onCancelar && (
                    <button type="button" className="aviso-form-cancelar" onClick={onCancelar}>Cancelar</button>
                )}
            </div>
        </form>
    )
}
