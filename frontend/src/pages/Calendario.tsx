import { useEffect, useState } from 'react'
import { listarAnosLetivos, listarTurmas } from '../api/academico'
import { criarEvento, editarEvento, excluirEvento, listarEventos, NOMES_TIPOS } from '../api/calendario'
import type { DadosEvento, Evento, TipoEvento } from '../api/calendario'
import { mensagemDeErro } from '../api/erros'
import { useAuth } from '../context/AuthContext'
import { TopoPortal } from '../components/TopoPortal'
import { RodapeLegal } from '../components/RodapeLegal'
import { formatarData } from '../api/tarefas'
import './MuralAvisos.css'
import './PainelSecretaria.css'
import './Painel.css'
import './Calendario.css'

const SEMANA = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

function iso(data: Date) {
    const copia = new Date(data)
    copia.setMinutes(copia.getMinutes() - copia.getTimezoneOffset())
    return copia.toISOString().slice(0, 10)
}

function chaveDoMes(data: Date) {
    return iso(data).slice(0, 7)
}

function diasDaGrade(mes: Date) {
    const primeiro = new Date(mes.getFullYear(), mes.getMonth(), 1)
    const inicio = new Date(primeiro)
    inicio.setDate(1 - primeiro.getDay())
    const ultimo = new Date(mes.getFullYear(), mes.getMonth() + 1, 0)
    const total = Math.ceil((primeiro.getDay() + ultimo.getDate()) / 7) * 7
    return Array.from({ length: total }, (_, i) => {
        const dia = new Date(inicio)
        dia.setDate(inicio.getDate() + i)
        return dia
    })
}

function periodo(evento: Evento) {
    return evento.inicio === evento.fim
        ? formatarData(evento.inicio)
        : `${formatarData(evento.inicio)} a ${formatarData(evento.fim)}`
}

const VAZIO: DadosEvento = { titulo: '', tipo: 'evento', inicio: '', fim: '', turma: null }

function FormEvento({ turmas, evento, onSalvo, onCancelar }: {
    turmas: { id: number; nome: string }[]
    evento: Evento | null
    onSalvo: (mensagem: string) => void
    onCancelar: () => void
}) {
    const [dados, setDados] = useState<DadosEvento>(evento
        ? { titulo: evento.titulo, tipo: evento.tipo, inicio: evento.inicio, fim: evento.fim, turma: evento.turma }
        : VAZIO)
    const [erro, setErro] = useState('')
    const [salvando, setSalvando] = useState(false)

    function alterar<K extends keyof DadosEvento>(campo: K, valor: DadosEvento[K]) {
        setDados((atual) => ({ ...atual, [campo]: valor }))
    }

    async function handleSubmit(event: React.FormEvent) {
        event.preventDefault()
        setErro('')
        if (!dados.titulo.trim()) return setErro('O título não pode ser vazio.')
        if (!dados.inicio || !dados.fim) return setErro('Informe a data de início e a de término.')
        if (dados.fim < dados.inicio) return setErro('A data de término não pode ser anterior à data de início.')
        setSalvando(true)
        try {
            const salvo = evento ? await editarEvento(evento.id, dados) : await criarEvento(dados)
            onSalvo(`Evento "${salvo.titulo}" ${evento ? 'atualizado' : 'cadastrado'}.`)
        } catch (error) {
            setErro(mensagemDeErro(error, 'Não foi possível salvar o evento.'))
        } finally {
            setSalvando(false)
        }
    }

    return (
        <section className="painel-card">
            <h2>{evento ? 'Editar evento' : 'Novo evento'}</h2>
            <form onSubmit={handleSubmit} noValidate>
                <div className="painel-campo">
                    <label htmlFor="evento-titulo">Título</label>
                    <input id="evento-titulo" type="text" maxLength={200} value={dados.titulo}
                        onChange={(e) => alterar('titulo', e.target.value)} />
                    <p className="painel-ajuda">Eventos do calendário não devem conter dados pessoais.</p>
                </div>
                <div className="painel-form">
                    <div className="painel-campo">
                        <label htmlFor="evento-tipo">Tipo</label>
                        <select id="evento-tipo" value={dados.tipo} onChange={(e) => alterar('tipo', e.target.value as TipoEvento)}>
                            {Object.entries(NOMES_TIPOS).map(([valor, nome]) => <option key={valor} value={valor}>{nome}</option>)}
                        </select>
                    </div>
                    <div className="painel-campo">
                        <label htmlFor="evento-turma">Para</label>
                        <select id="evento-turma" value={dados.turma ?? ''}
                            onChange={(e) => alterar('turma', e.target.value ? Number(e.target.value) : null)}>
                            <option value="">Toda a escola</option>
                            {turmas.map((t) => <option key={t.id} value={t.id}>Turma {t.nome}</option>)}
                        </select>
                    </div>
                    <div className="painel-campo">
                        <label htmlFor="evento-inicio">Início</label>
                        <input id="evento-inicio" type="date" value={dados.inicio}
                            onChange={(e) => setDados((atual) => ({
                                ...atual, inicio: e.target.value, fim: atual.fim || e.target.value,
                            }))} />
                    </div>
                    <div className="painel-campo">
                        <label htmlFor="evento-fim">Término</label>
                        <input id="evento-fim" type="date" value={dados.fim} onChange={(e) => alterar('fim', e.target.value)} />
                    </div>
                </div>
                {erro && <p className="painel-erro" role="alert">{erro}</p>}
                <div className="painel-acoes">
                    <button type="submit" className="painel-botao" disabled={salvando}>
                        {salvando ? 'Salvando...' : evento ? 'Salvar alterações' : 'Cadastrar evento'}
                    </button>
                    <button type="button" className="painel-botao-secundario" onClick={onCancelar}>Cancelar</button>
                </div>
            </form>
        </section>
    )
}

export function Calendario() {
    const { usuario } = useAuth()
    const ehGestor = usuario?.role === 'secretaria' || usuario?.role === 'direcao'
    const [mes, setMes] = useState(() => {
        const hoje = new Date()
        return new Date(hoje.getFullYear(), hoje.getMonth(), 1)
    })
    const [eventos, setEventos] = useState<Evento[]>([])
    const [turmas, setTurmas] = useState<{ id: number; nome: string }[]>([])
    const [formulario, setFormulario] = useState<{ evento: Evento | null } | null>(null)
    const [mensagem, setMensagem] = useState('')
    const [erro, setErro] = useState('')
    const [versao, setVersao] = useState(0)

    useEffect(() => {
        listarEventos(chaveDoMes(mes))
            .then((lista) => { setEventos(lista); setErro('') })
            .catch((error) => setErro(mensagemDeErro(error, 'Não foi possível carregar o calendário.')))
    }, [mes, versao])

    useEffect(() => {
        if (!ehGestor) return
        listarAnosLetivos().then(async (anos) => {
            const atual = anos.find((a) => a.ativo)
            if (atual) setTurmas((await listarTurmas(atual.id)).map((t) => ({ id: t.id, nome: t.nome })))
        })
    }, [ehGestor])

    function mudarMes(delta: number) {
        setMes((atual) => new Date(atual.getFullYear(), atual.getMonth() + delta, 1))
    }

    async function handleExcluir(evento: Evento) {
        if (!window.confirm(`Excluir o evento "${evento.titulo}"?`)) return
        try {
            await excluirEvento(evento.id)
            setMensagem(`Evento "${evento.titulo}" excluído.`)
            setVersao((v) => v + 1)
        } catch (error) {
            setErro(mensagemDeErro(error, 'Não foi possível excluir o evento.'))
        }
    }

    const hoje = iso(new Date())
    const extenso = mes.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })
    const nomeDoMes = extenso.charAt(0).toUpperCase() + extenso.slice(1)

    return (
        <div className="mural-page">
            <TopoPortal />
            <main className="painel-conteudo">
                <h1>Calendário escolar</h1>
                {ehGestor && !formulario && (
                    <div className="painel-acoes">
                        <button type="button" className="painel-botao" onClick={() => { setMensagem(''); setFormulario({ evento: null }) }}>
                            Novo evento
                        </button>
                    </div>
                )}
                {formulario && (
                    <FormEvento key={formulario.evento?.id ?? 'novo'} turmas={turmas} evento={formulario.evento}
                        onCancelar={() => setFormulario(null)}
                        onSalvo={(texto) => { setFormulario(null); setMensagem(texto); setVersao((v) => v + 1) }} />
                )}
                {mensagem && <p className="painel-sucesso" role="status">{mensagem}</p>}
                {erro && <p className="painel-erro" role="alert">{erro}</p>}

                <section className="painel-card">
                    <div className="calendario-navegacao">
                        <button type="button" className="painel-botao-secundario" onClick={() => mudarMes(-1)}>‹ Mês anterior</button>
                        <h2>{nomeDoMes}</h2>
                        <button type="button" className="painel-botao-secundario" onClick={() => mudarMes(1)}>Próximo mês ›</button>
                    </div>
                    <div className="calendario-grade" role="grid" aria-label={`Calendário de ${nomeDoMes}`}>
                        {SEMANA.map((d) => <div key={d} className="calendario-semana" role="columnheader">{d}</div>)}
                        {diasDaGrade(mes).map((dia) => {
                            const chave = iso(dia)
                            const doDia = eventos.filter((e) => e.inicio <= chave && chave <= e.fim)
                            const classes = ['calendario-dia']
                            if (dia.getMonth() !== mes.getMonth()) classes.push('calendario-dia-fora')
                            if (chave === hoje) classes.push('calendario-dia-hoje')
                            return (
                                <div key={chave} className={classes.join(' ')} role="gridcell">
                                    <span className="calendario-numero">{dia.getDate()}</span>
                                    {doDia.map((e) => (
                                        <span key={e.id} className={`calendario-evento calendario-tipo-${e.tipo}`} title={`${e.tipo_nome}: ${e.titulo}`}>
                                            {e.titulo}
                                        </span>
                                    ))}
                                </div>
                            )
                        })}
                    </div>
                </section>

                <section className="painel-card">
                    <h2>Eventos do mês</h2>
                    {eventos.length === 0 ? (
                        <p className="painel-ajuda">Nenhum evento neste mês.</p>
                    ) : (
                        <ul className="calendario-lista">
                            {eventos.map((e) => (
                                <li key={e.id}>
                                    <span className={`calendario-evento calendario-tipo-${e.tipo}`}>{e.tipo_nome}</span>
                                    <span className="calendario-lista-titulo">{e.titulo}</span>
                                    <span className="painel-ajuda-inline">{periodo(e)} · {e.turma_nome ? `Turma ${e.turma_nome}` : 'Toda a escola'}</span>
                                    {ehGestor && (
                                        <span className="painel-acoes-linha">
                                            <button type="button" className="painel-botao-link" onClick={() => { setMensagem(''); setFormulario({ evento: e }) }}>Editar</button>{' '}
                                            <button type="button" className="painel-botao-link" onClick={() => handleExcluir(e)}>Excluir</button>
                                        </span>
                                    )}
                                </li>
                            ))}
                        </ul>
                    )}
                </section>
            </main>
            <RodapeLegal />
        </div>
    )
}
