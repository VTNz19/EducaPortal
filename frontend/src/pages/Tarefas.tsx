import { useEffect, useRef, useState } from 'react'
import { listarDisciplinas } from '../api/academico'
import type { Disciplina } from '../api/academico'
import {
    baixarAnexo, erroDoArquivo, excluirTarefa, formatarData, formatarTamanho, listarTarefas, publicarTarefa,
} from '../api/tarefas'
import type { AnexoTarefa, Tarefa } from '../api/tarefas'
import { mensagemDeErro } from '../api/erros'
import { useAuth } from '../context/AuthContext'
import { TopoPortal } from '../components/TopoPortal'
import { RodapeLegal } from '../components/RodapeLegal'
import './MuralAvisos.css'
import './PainelSecretaria.css'
import './Painel.css'
import './Tarefas.css'

function hojeISO() {
    const hoje = new Date()
    hoje.setMinutes(hoje.getMinutes() - hoje.getTimezoneOffset())
    return hoje.toISOString().slice(0, 10)
}

function NovaTarefa({ disciplinas, onPublicada }: { disciplinas: Disciplina[]; onPublicada: (mensagem: string) => void }) {
    const [disciplina, setDisciplina] = useState<number | null>(disciplinas.length === 1 ? disciplinas[0].id : null)
    const [titulo, setTitulo] = useState('')
    const [descricao, setDescricao] = useState('')
    const [prazo, setPrazo] = useState('')
    const [arquivos, setArquivos] = useState<File[]>([])
    const [erros, setErros] = useState<string[]>([])
    const [enviando, setEnviando] = useState(false)
    const campoArquivos = useRef<HTMLInputElement>(null)

    function escolherArquivos(lista: FileList | null) {
        const escolhidos = Array.from(lista ?? [])
        setErros(escolhidos.map(erroDoArquivo).filter((e): e is string => e !== null))
        setArquivos(escolhidos.filter((a) => erroDoArquivo(a) === null))
    }

    async function handleSubmit(event: React.FormEvent) {
        event.preventDefault()
        const problemas = []
        if (!disciplina) problemas.push('Selecione a disciplina.')
        if (!titulo.trim()) problemas.push('O título não pode ser vazio.')
        if (!prazo) problemas.push('Informe o prazo de entrega.')
        else if (prazo < hojeISO()) problemas.push('O prazo de entrega não pode ser anterior a hoje.')
        setErros(problemas)
        if (problemas.length > 0 || !disciplina) return

        setEnviando(true)
        try {
            const tarefa = await publicarTarefa({ disciplina, titulo, descricao, prazo, arquivos })
            setTitulo('')
            setDescricao('')
            setPrazo('')
            setArquivos([])
            if (campoArquivos.current) campoArquivos.current.value = ''
            const email = tarefa.email_enviado === false
                ? ' O aviso por e-mail não pôde ser enviado.'
                : tarefa.email_enviado ? ' Alunos e responsáveis foram avisados por e-mail.' : ''
            onPublicada(`Tarefa "${tarefa.titulo}" publicada para a turma ${tarefa.turma_nome}.${email}`)
        } catch (error) {
            setErros([mensagemDeErro(error, 'Não foi possível publicar a tarefa. Verifique os campos.')])
        } finally {
            setEnviando(false)
        }
    }

    return (
        <section className="painel-card">
            <h2>Nova tarefa</h2>
            <form onSubmit={handleSubmit} noValidate>
                <div className="painel-form">
                    <div className="painel-campo">
                        <label htmlFor="disciplina">Disciplina</label>
                        <select id="disciplina" value={disciplina ?? ''}
                            onChange={(e) => setDisciplina(e.target.value ? Number(e.target.value) : null)}>
                            <option value="">Selecione</option>
                            {disciplinas.map((d) => (
                                <option key={d.id} value={d.id}>{d.nome} – {d.turma_nome}</option>
                            ))}
                        </select>
                    </div>
                    <div className="painel-campo">
                        <label htmlFor="prazo">Prazo de entrega</label>
                        <input id="prazo" type="date" min={hojeISO()} value={prazo} onChange={(e) => setPrazo(e.target.value)} />
                    </div>
                </div>
                <div className="painel-campo">
                    <label htmlFor="titulo">Título</label>
                    <input id="titulo" type="text" maxLength={200} value={titulo} onChange={(e) => setTitulo(e.target.value)} />
                </div>
                <div className="painel-campo">
                    <label htmlFor="descricao">Descrição (opcional)</label>
                    <textarea id="descricao" rows={3} value={descricao} onChange={(e) => setDescricao(e.target.value)} />
                </div>
                <div className="painel-campo">
                    <label htmlFor="arquivos">Anexos (opcional)</label>
                    <input id="arquivos" ref={campoArquivos} type="file" multiple accept=".pdf,.docx,.png,.jpg,.jpeg"
                        onChange={(e) => escolherArquivos(e.target.files)} />
                    <p className="painel-ajuda">PDF, DOCX, PNG ou JPG de até 10 MB cada. Não inclua dados pessoais dos alunos.</p>
                    {arquivos.length > 0 && (
                        <ul className="tarefa-anexos">
                            {arquivos.map((a) => <li key={a.name}>{a.name} ({formatarTamanho(a.size)})</li>)}
                        </ul>
                    )}
                </div>
                {erros.length > 0 && (
                    <div className="painel-erro" role="alert">{erros.map((e) => <p key={e}>{e}</p>)}</div>
                )}
                <div className="painel-acoes">
                    <button type="submit" className="painel-botao" disabled={enviando}>
                        {enviando ? 'Publicando...' : 'Publicar tarefa'}
                    </button>
                </div>
            </form>
        </section>
    )
}

function CartaoTarefa({ tarefa, podeExcluir, onExcluir, onErro }: {
    tarefa: Tarefa
    podeExcluir: boolean
    onExcluir: (tarefa: Tarefa) => void
    onErro: (mensagem: string) => void
}) {
    async function baixar(anexo: AnexoTarefa) {
        try {
            await baixarAnexo(tarefa.id, anexo)
        } catch (error) {
            onErro(mensagemDeErro(error, `Não foi possível baixar "${anexo.nome}".`))
        }
    }

    return (
        <li className={`tarefa-card${tarefa.encerrada ? ' tarefa-encerrada' : ''}`}>
            <div className="tarefa-cabecalho">
                <h3>{tarefa.titulo}</h3>
                <span className={`tarefa-prazo${tarefa.encerrada ? '' : ' tarefa-prazo-aberta'}`}>
                    {tarefa.encerrada ? 'Encerrada em ' : 'Entrega até '}{formatarData(tarefa.prazo)}
                </span>
            </div>
            <p className="painel-ajuda">
                {tarefa.disciplina_nome} – Turma {tarefa.turma_nome}{tarefa.autor_nome && ` · ${tarefa.autor_nome}`}
            </p>
            {tarefa.descricao && <p className="tarefa-descricao">{tarefa.descricao}</p>}
            {tarefa.anexos.length > 0 && (
                <ul className="tarefa-anexos">
                    {tarefa.anexos.map((a) => (
                        <li key={a.id}>
                            <button type="button" className="painel-botao-link" onClick={() => baixar(a)}>
                                Baixar {a.nome}
                            </button>{' '}
                            <span className="painel-ajuda-inline">({formatarTamanho(a.tamanho)})</span>
                        </li>
                    ))}
                </ul>
            )}
            {podeExcluir && (
                <div className="painel-acoes">
                    <button type="button" className="painel-botao-secundario painel-botao-perigo" onClick={() => onExcluir(tarefa)}>
                        Excluir tarefa
                    </button>
                </div>
            )}
        </li>
    )
}

export function Tarefas() {
    const { usuario } = useAuth()
    const ehProfessor = usuario?.role === 'professor'
    const [tarefas, setTarefas] = useState<Tarefa[]>([])
    const [disciplinas, setDisciplinas] = useState<Disciplina[]>([])
    const [carregando, setCarregando] = useState(true)
    const [mensagem, setMensagem] = useState('')
    const [erro, setErro] = useState('')
    const [versao, setVersao] = useState(0)

    useEffect(() => {
        listarTarefas()
            .then(setTarefas)
            .catch((error) => setErro(mensagemDeErro(error, 'Não foi possível carregar as tarefas.')))
            .finally(() => setCarregando(false))
    }, [versao])

    useEffect(() => {
        if (ehProfessor) listarDisciplinas().then(setDisciplinas)
    }, [ehProfessor])

    function carregar() {
        setVersao((v) => v + 1)
    }

    async function handleExcluir(tarefa: Tarefa) {
        if (!window.confirm(`Excluir a tarefa "${tarefa.titulo}" e os seus anexos?`)) return
        setErro('')
        try {
            await excluirTarefa(tarefa.id)
            setMensagem(`Tarefa "${tarefa.titulo}" excluída.`)
            carregar()
        } catch (error) {
            setErro(mensagemDeErro(error, 'Não foi possível excluir a tarefa.'))
        }
    }

    const abertas = tarefas.filter((t) => !t.encerrada)
    const encerradas = tarefas.filter((t) => t.encerrada)
    const podeExcluir = (t: Tarefa) => ehProfessor && t.autor === usuario?.id

    function lista(itens: Tarefa[]) {
        return (
            <ul className="tarefa-lista">
                {itens.map((t) => (
                    <CartaoTarefa key={t.id} tarefa={t} podeExcluir={podeExcluir(t)} onExcluir={handleExcluir} onErro={setErro} />
                ))}
            </ul>
        )
    }

    return (
        <div className="mural-page">
            <TopoPortal />
            <main className="painel-conteudo">
                <h1>Tarefas</h1>
                {ehProfessor && disciplinas.length > 0 && (
                    <NovaTarefa disciplinas={disciplinas} onPublicada={(texto) => { setErro(''); setMensagem(texto); carregar() }} />
                )}
                {mensagem && <p className="painel-sucesso" role="status">{mensagem}</p>}
                {erro && <p className="painel-erro" role="alert">{erro}</p>}
                {carregando ? (
                    <p>Carregando tarefas...</p>
                ) : (
                    <>
                        <section className="painel-card">
                            <h2>Com prazo em aberto</h2>
                            {abertas.length === 0 ? <p className="painel-ajuda">Nenhuma tarefa com prazo em aberto.</p> : lista(abertas)}
                        </section>
                        {encerradas.length > 0 && (
                            <section className="painel-card">
                                <h2>Encerradas</h2>
                                {lista(encerradas)}
                            </section>
                        )}
                    </>
                )}
            </main>
            <RodapeLegal />
        </div>
    )
}
