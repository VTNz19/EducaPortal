import { useEffect, useState } from 'react'
import { isAxiosError } from 'axios'
import { listarDisciplinas } from '../api/academico'
import type { Disciplina } from '../api/academico'
import { obterNotas, publicarNotas, salvarNotas } from '../api/diario'
import type { EstadoNotas } from '../api/diario'
import { mensagemDeErro } from '../api/erros'
import { TopoPortal } from '../components/TopoPortal'
import { RodapeLegal } from '../components/RodapeLegal'
import './MuralAvisos.css'
import './PainelSecretaria.css'


const NOTA_VALIDA = /^(10([.,]0)?|\d([.,]\d)?)$/

function formatar(valor: number | null) {
    return valor === null ? '' : String(valor).replace('.', ',')
}

export function LancarNotas() {
    const [disciplinas, setDisciplinas] = useState<Disciplina[]>([])
    const [disciplinaId, setDisciplinaId] = useState<number | null>(null)
    const [bimestre, setBimestre] = useState<number | null>(null)
    const [estado, setEstado] = useState<EstadoNotas | null>(null)
    const [valores, setValores] = useState<Record<number, string>>({})
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

    function aplicar(novo: EstadoNotas) {
        setEstado(novo)
        setBimestre(novo.bimestre.numero)
        setValores(Object.fromEntries(novo.alunos.map((a) => [a.matricula, formatar(a.valor)])))
    }

    async function abrir(disciplina: number, numero?: number) {
        setErro('')
        setMensagem('')
        try {
            aplicar(await obterNotas(disciplina, numero))
        } catch (error) {
            setEstado(null)
            setErro(mensagemDeErro(error, 'Não foi possível carregar as notas.'))
        }
    }

    function escolherDisciplina(id: number) {
        setDisciplinaId(id)
        abrir(id, bimestre ?? undefined)
    }

    const invalidos = Object.entries(valores).filter(([, v]) => v.trim() !== '' && !NOTA_VALIDA.test(v.trim()))
    const alterado = estado?.alunos.some((a) => formatar(a.valor) !== (valores[a.matricula] ?? '')) ?? false

    async function handleSalvar() {
        if (!estado || bimestre === null) return
        setErro('')
        setMensagem('')
        if (invalidos.length > 0) {
            setErro('A nota deve estar entre 0 e 10, com até uma casa decimal. Corrija os campos destacados.')
            return
        }
        setSalvando(true)
        try {
            const notas = estado.alunos.map((a) => {
                const v = (valores[a.matricula] ?? '').trim()
                return { matricula: a.matricula, valor: v === '' ? null : v.replace(',', '.') }
            })
            const novo = await salvarNotas(estado.disciplina.id, bimestre, notas)
            aplicar(novo)
            setMensagem(novo.pendentes_publicacao > 0
                ? 'Notas salvas. Elas só ficam visíveis para alunos e responsáveis depois de publicadas.'
                : 'Notas salvas.')
        } catch (error) {
            setErro(mensagemDeErro(error, 'Não foi possível salvar as notas.'))
        } finally {
            setSalvando(false)
        }
    }

    async function handlePublicar() {
        if (!estado || bimestre === null) return
        setErro('')
        setMensagem('')
        setSalvando(true)
        try {
            let novo: EstadoNotas
            try {
                novo = await publicarNotas(estado.disciplina.id, bimestre)
            } catch (error) {
                if (isAxiosError(error) && error.response?.status === 409 && window.confirm(error.response.data.detail)) {
                    novo = await publicarNotas(estado.disciplina.id, bimestre, true)
                } else {
                    throw error
                }
            }
            aplicar(novo)
            setMensagem(novo.email_enviado
                ? 'Notas publicadas. Alunos e responsáveis foram avisados por e-mail.'
                : 'Notas publicadas, mas o aviso por e-mail não pôde ser enviado.')
        } catch (error) {
            if (!(isAxiosError(error) && error.response?.status === 409)) {
                setErro(mensagemDeErro(error, 'Não foi possível publicar as notas.'))
            }
        } finally {
            setSalvando(false)
        }
    }

    return (
        <div className="mural-page">
            <TopoPortal />
            <main className="painel-conteudo">
                <h1>Lançar notas</h1>

                <section className="painel-card">
                    {carregando ? (
                        <p>Carregando...</p>
                    ) : disciplinas.length === 0 ? (
                        <p className="painel-aviso">Você não tem disciplinas atribuídas neste ano letivo. Procure a secretaria.</p>
                    ) : (
                        <div className="painel-form">
                            <div className="painel-campo">
                                <label htmlFor="bimestre">Bimestre</label>
                                <select id="bimestre" value={bimestre ?? ''} disabled={!disciplinaId}
                                    onChange={(e) => disciplinaId && abrir(disciplinaId, Number(e.target.value))}>
                                    {bimestre === null && <option value="">Em andamento</option>}
                                    {[1, 2, 3, 4].map((n) => <option key={n} value={n}>{n}º bimestre</option>)}
                                </select>
                            </div>
                            <div className="painel-campo">
                                <label htmlFor="disciplina">Disciplina</label>
                                <select id="disciplina" value={disciplinaId ?? ''}
                                    onChange={(e) => escolherDisciplina(Number(e.target.value))}>
                                    <option value="">Selecione</option>
                                    {disciplinas.map((d) => (
                                        <option key={d.id} value={d.id}>{d.nome} – {d.turma_nome} ({d.ano})</option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    )}
                    {erro && <p className="painel-erro" role="alert">{erro}</p>}
                    {mensagem && <p className="painel-sucesso" role="status">{mensagem}</p>}
                </section>

                {estado && (
                    <section className="painel-card">
                        <h2>{estado.disciplina.nome} – {estado.disciplina.turma} – {estado.bimestre.numero}º bimestre</h2>
                        <p className="painel-ajuda">
                            Notas de 0 a 10, com até uma casa decimal. Deixe em branco quem ainda não tem nota.
                            {estado.sem_nota > 0 && ` ${estado.sem_nota} aluno(s) sem nota.`}
                            {estado.pendentes_publicacao > 0 && ` ${estado.pendentes_publicacao} nota(s) ainda não publicada(s).`}
                        </p>
                        {estado.alunos.length === 0 ? (
                            <p>Nenhum aluno matriculado nesta turma.</p>
                        ) : (
                            <div className="painel-tabela-wrapper">
                                <table className="painel-tabela">
                                    <thead>
                                        <tr><th>Aluno</th><th>Nota</th><th>Situação</th></tr>
                                    </thead>
                                    <tbody>
                                        {estado.alunos.map((a) => {
                                            const valor = valores[a.matricula] ?? ''
                                            const invalido = valor.trim() !== '' && !NOTA_VALIDA.test(valor.trim())
                                            return (
                                                <tr key={a.matricula}>
                                                    <td>{a.nome}</td>
                                                    <td>
                                                        <input
                                                            className={`painel-nota ${invalido ? 'painel-campo-invalido' : ''}`}
                                                            inputMode="decimal"
                                                            aria-label={`Nota de ${a.nome}`}
                                                            aria-invalid={invalido}
                                                            value={valor}
                                                            onChange={(e) => setValores({ ...valores, [a.matricula]: e.target.value })}
                                                        />
                                                    </td>
                                                    <td>{a.valor === null ? '-' : a.publicada ? 'Publicada' : 'Rascunho'}</td>
                                                </tr>
                                            )
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        )}
                        <div className="painel-acoes painel-espaco">
                            <button type="button" className="painel-botao" onClick={handleSalvar} disabled={salvando || !alterado}>
                                {salvando ? 'Salvando...' : 'Salvar'}
                            </button>
                            <button type="button" className="painel-botao-secundario" onClick={handlePublicar}
                                disabled={salvando || alterado || estado.pendentes_publicacao === 0}
                                title={alterado ? 'Salve as alterações antes de publicar' : undefined}>
                                Publicar notas do bimestre
                            </button>
                        </div>
                    </section>
                )}
            </main>
            <RodapeLegal />
        </div>
    )
}
