import { useEffect, useState } from 'react'
import { listarDisciplinas } from '../api/academico'
import type { Disciplina } from '../api/academico'
import { obterChamada, registrarChamada } from '../api/diario'
import type { EstadoChamada } from '../api/diario'
import { mensagemDeErro } from '../api/erros'
import { TopoPortal } from '../components/TopoPortal'
import { RodapeLegal } from '../components/RodapeLegal'
import './MuralAvisos.css'
import './PainelSecretaria.css'


function hojeISO() {
    const hoje = new Date()
    hoje.setMinutes(hoje.getMinutes() - hoje.getTimezoneOffset())
    return hoje.toISOString().slice(0, 10)
}

export function Chamada() {
    const [disciplinas, setDisciplinas] = useState<Disciplina[]>([])
    const [disciplinaId, setDisciplinaId] = useState<number | null>(null)
    const [data, setData] = useState(hojeISO())
    const [estado, setEstado] = useState<EstadoChamada | null>(null)
    const [presentes, setPresentes] = useState<Record<number, boolean>>({})
    const [aulas, setAulas] = useState(1)
    const [carregando, setCarregando] = useState(true)
    const [salvando, setSalvando] = useState(false)
    const [erro, setErro] = useState('')
    const [mensagem, setMensagem] = useState('')

    useEffect(() => {
        listarDisciplinas().then((lista) => {
            setDisciplinas(lista)
            setCarregando(false)
        })
    }, [])

    function aplicar(novo: EstadoChamada) {
        setEstado(novo)
        setAulas(novo.quantidade_aulas)
        setPresentes(Object.fromEntries(novo.alunos.map((a) => [a.matricula, a.presente])))
    }

    async function abrir(disciplina: number, dia: string) {
        setErro('')
        setMensagem('')
        try {
            aplicar(await obterChamada(disciplina, dia))
        } catch (error) {
            setEstado(null)
            setErro(mensagemDeErro(error, 'Não foi possível abrir a chamada.'))
        }
    }

    async function handleConfirmar() {
        if (!estado || disciplinaId === null) return
        setErro('')
        setMensagem('')
        setSalvando(true)
        try {
            const ausentes = estado.alunos.filter((a) => !presentes[a.matricula]).map((a) => a.matricula)
            const novo = await registrarChamada(disciplinaId, data, aulas, ausentes)
            aplicar(novo)
            const aviso = novo.email_enviado === null
                ? ''
                : novo.email_enviado
                    ? ' Os responsáveis dos ausentes foram avisados por e-mail.'
                    : ' O aviso por e-mail aos responsáveis não pôde ser enviado.'
            setMensagem(`Chamada ${estado.existente ? 'corrigida' : 'registrada'}: ${ausentes.length} ausente(s).${aviso}`)
        } catch (error) {
            setErro(mensagemDeErro(error, 'Não foi possível registrar a chamada.'))
        } finally {
            setSalvando(false)
        }
    }

    const ausentes = estado ? estado.alunos.filter((a) => !presentes[a.matricula]).length : 0

    return (
        <div className="mural-page">
            <TopoPortal />
            <main className="painel-conteudo">
                <h1>Chamada</h1>

                <section className="painel-card">
                    {carregando ? (
                        <p>Carregando...</p>
                    ) : disciplinas.length === 0 ? (
                        <p className="painel-aviso">Você não tem disciplinas atribuídas neste ano letivo. Procure a secretaria.</p>
                    ) : (
                        <div className="painel-form">
                            <div className="painel-campo">
                                <label htmlFor="disciplina">Disciplina</label>
                                <select id="disciplina" value={disciplinaId ?? ''}
                                    onChange={(e) => {
                                        const id = Number(e.target.value)
                                        setDisciplinaId(id)
                                        if (id) abrir(id, data)
                                    }}>
                                    <option value="">Selecione</option>
                                    {disciplinas.map((d) => (
                                        <option key={d.id} value={d.id}>{d.nome} – {d.turma_nome} ({d.ano})</option>
                                    ))}
                                </select>
                            </div>
                            <div className="painel-campo">
                                <label htmlFor="data">Data da aula</label>
                                <input id="data" type="date" value={data} max={hojeISO()}
                                    onChange={(e) => {
                                        setData(e.target.value)
                                        if (disciplinaId && e.target.value) abrir(disciplinaId, e.target.value)
                                    }} />
                            </div>
                            <div className="painel-campo">
                                <label htmlFor="aulas">Aulas seguidas</label>
                                <select id="aulas" value={aulas} onChange={(e) => setAulas(Number(e.target.value))}>
                                    {[1, 2, 3, 4].map((n) => <option key={n} value={n}>{n}</option>)}
                                </select>
                            </div>
                        </div>
                    )}
                    {erro && <p className="painel-erro" role="alert">{erro}</p>}
                    {mensagem && <p className="painel-sucesso" role="status">{mensagem}</p>}
                </section>

                {estado && (
                    <section className="painel-card">
                        <h2>{estado.disciplina.nome} – {estado.disciplina.turma}</h2>
                        <p className="painel-ajuda">
                            {estado.existente
                                ? 'Já existe chamada nesta data. Ao confirmar, ela será corrigida.'
                                : 'Todos começam presentes. Desmarque apenas quem faltou.'}{' '}
                            {estado.bimestre.numero}º bimestre. Cada falta conta para todas as {aulas} aula(s).
                        </p>
                        {estado.alunos.length === 0 ? (
                            <p>Nenhum aluno matriculado nesta turma.</p>
                        ) : (
                            <ul className="painel-lista painel-chamada">
                                {estado.alunos.map((a) => (
                                    <li key={a.matricula} className={presentes[a.matricula] ? '' : 'painel-ausente'}>
                                        <label className="painel-opcao">
                                            <input type="checkbox" checked={presentes[a.matricula] ?? true}
                                                onChange={(e) => setPresentes({ ...presentes, [a.matricula]: e.target.checked })} />
                                            {a.nome}
                                        </label>
                                        <span className="painel-ajuda-inline">{presentes[a.matricula] ? 'Presente' : 'Ausente'}</span>
                                    </li>
                                ))}
                            </ul>
                        )}
                        <div className="painel-acoes painel-espaco">
                            <button type="button" className="painel-botao" onClick={handleConfirmar}
                                disabled={salvando || estado.alunos.length === 0}>
                                {salvando ? 'Salvando...' : `Confirmar chamada (${ausentes} ausente${ausentes === 1 ? '' : 's'})`}
                            </button>
                        </div>
                    </section>
                )}
            </main>
            <RodapeLegal />
        </div>
    )
}
