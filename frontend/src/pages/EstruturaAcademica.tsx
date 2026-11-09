import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import {
    ativarAnoLetivo, criarAnoLetivo, criarDisciplina, criarTurma, excluirDisciplina, excluirTurma,
    listarAnosLetivos, listarDisciplinas, listarTurmas, NOMES_TURNOS, trocarProfessor,
} from '../api/academico'
import type { AnoLetivo, Bimestre, Disciplina, Turma, Turno } from '../api/academico'
import { listarPorPerfil } from '../api/usuarios'
import type { UsuarioResumo } from '../api/usuarios'
import { mensagemDeErro } from '../api/erros'
import { TopoPortal } from '../components/TopoPortal'
import { RodapeLegal } from '../components/RodapeLegal'
import './MuralAvisos.css'
import './PainelSecretaria.css'


const BIMESTRES_VAZIOS: Bimestre[] = [1, 2, 3, 4].map((numero) => ({ numero, inicio: '', fim: '' }))

function dataBR(iso: string) {
    return new Date(`${iso}T00:00:00`).toLocaleDateString('pt-BR')
}

export function EstruturaAcademica() {
    const [anos, setAnos] = useState<AnoLetivo[]>([])
    const [anoSelecionado, setAnoSelecionado] = useState<number | null>(null)
    const [turmas, setTurmas] = useState<Turma[]>([])
    const [turmaSelecionada, setTurmaSelecionada] = useState<number | null>(null)
    const [disciplinas, setDisciplinas] = useState<Disciplina[]>([])
    const [professores, setProfessores] = useState<UsuarioResumo[]>([])
    const [erro, setErro] = useState('')
    const [mensagem, setMensagem] = useState('')

    const [novoAno, setNovoAno] = useState({ ano: new Date().getFullYear() + 1, ativo: false, bimestres: BIMESTRES_VAZIOS })
    const [novaTurma, setNovaTurma] = useState({ nome: '', serie: '', turno: 'manha' as Turno })
    const [novaDisciplina, setNovaDisciplina] = useState({ nome: '', carga_horaria: 80, professor: 0 })

    function avisar(texto: string) {
        setErro('')
        setMensagem(texto)
    }

    function falhar(error: unknown, padrao: string) {
        setMensagem('')
        setErro(mensagemDeErro(error, padrao))
    }

    async function carregarAnos() {
        const lista = await listarAnosLetivos()
        setAnos(lista)
        if (anoSelecionado === null && lista.length > 0) {
            setAnoSelecionado((lista.find((a) => a.ativo) ?? lista[0]).id)
        }
    }

    useEffect(() => {
        carregarAnos()
        listarPorPerfil('professor').then(setProfessores)
    }, [])

    useEffect(() => {
        if (anoSelecionado === null) return
        setTurmaSelecionada(null)
        setDisciplinas([])
        listarTurmas(anoSelecionado).then(setTurmas)
    }, [anoSelecionado])

    useEffect(() => {
        if (turmaSelecionada === null) return
        listarDisciplinas(turmaSelecionada).then(setDisciplinas)
    }, [turmaSelecionada])

    function alterarBimestre(numero: number, campo: 'inicio' | 'fim', valor: string) {
        setNovoAno({
            ...novoAno,
            bimestres: novoAno.bimestres.map((b) => (b.numero === numero ? { ...b, [campo]: valor } : b)),
        })
    }

    async function handleCriarAno(event: FormEvent) {
        event.preventDefault()
        try {
            const criado = await criarAnoLetivo(novoAno)
            avisar(`Ano letivo ${criado.ano} cadastrado.`)
            setNovoAno({ ano: criado.ano + 1, ativo: false, bimestres: BIMESTRES_VAZIOS })
            setAnoSelecionado(criado.id)
            carregarAnos()
        } catch (error) {
            falhar(error, 'Não foi possível cadastrar o ano letivo.')
        }
    }

    async function handleAtivar(ano: AnoLetivo) {
        try {
            await ativarAnoLetivo(ano.id)
            avisar(`${ano.ano} agora é o ano letivo atual.`)
            carregarAnos()
        } catch (error) {
            falhar(error, 'Não foi possível ativar o ano letivo.')
        }
    }

    async function handleCriarTurma(event: FormEvent) {
        event.preventDefault()
        if (anoSelecionado === null) return
        try {
            const criada = await criarTurma({ ano_letivo: anoSelecionado, ...novaTurma })
            avisar(`Turma ${criada.nome} cadastrada.`)
            setNovaTurma({ ...novaTurma, nome: '' })
            setTurmas(await listarTurmas(anoSelecionado))
        } catch (error) {
            falhar(error, 'Não foi possível cadastrar a turma.')
        }
    }

    async function handleExcluirTurma(turma: Turma) {
        if (!window.confirm(`Excluir a turma ${turma.nome}?`)) return
        try {
            await excluirTurma(turma.id)
            avisar(`Turma ${turma.nome} excluída.`)
            if (turmaSelecionada === turma.id) setTurmaSelecionada(null)
            setTurmas(await listarTurmas(turma.ano_letivo))
        } catch (error) {
            falhar(error, 'Não foi possível excluir a turma.')
        }
    }

    async function handleCriarDisciplina(event: FormEvent) {
        event.preventDefault()
        if (turmaSelecionada === null) return
        try {
            const criada = await criarDisciplina({ turma: turmaSelecionada, ...novaDisciplina })
            avisar(`Disciplina ${criada.nome} cadastrada para ${criada.professor_nome}.`)
            setNovaDisciplina({ ...novaDisciplina, nome: '' })
            setDisciplinas(await listarDisciplinas(turmaSelecionada))
        } catch (error) {
            falhar(error, 'Não foi possível cadastrar a disciplina.')
        }
    }

    async function handleTrocarProfessor(disciplina: Disciplina, professor: number) {
        try {
            const atualizada = await trocarProfessor(disciplina.id, professor)
            avisar(`${atualizada.nome} agora é com ${atualizada.professor_nome}.`)
            setDisciplinas(disciplinas.map((d) => (d.id === atualizada.id ? atualizada : d)))
        } catch (error) {
            falhar(error, 'Não foi possível trocar o professor.')
        }
    }

    async function handleExcluirDisciplina(disciplina: Disciplina) {
        if (!window.confirm(`Excluir a disciplina ${disciplina.nome}?`)) return
        try {
            await excluirDisciplina(disciplina.id)
            avisar(`Disciplina ${disciplina.nome} excluída.`)
            setDisciplinas(disciplinas.filter((d) => d.id !== disciplina.id))
        } catch (error) {
            falhar(error, 'Não foi possível excluir a disciplina.')
        }
    }

    const ano = anos.find((a) => a.id === anoSelecionado)
    const turma = turmas.find((t) => t.id === turmaSelecionada)

    return (
        <div className="mural-page">
            <TopoPortal />

            <main className="painel-conteudo">
                <h1>Estrutura acadêmica</h1>

                {erro && <p className="painel-erro painel-alerta" role="alert">{erro}</p>}
                {mensagem && <p className="painel-sucesso painel-alerta" role="status">{mensagem}</p>}

                <section className="painel-card">
                    <h2>1. Ano letivo</h2>
                    <p className="painel-ajuda">
                        O ano letivo é dividido em 4 bimestres, que não podem se sobrepor. Só um ano fica ativo por vez:
                        é nele que os alunos são matriculados.
                    </p>

                    {anos.length > 0 && (
                        <div className="painel-tabela-wrapper">
                            <table className="painel-tabela">
                                <thead>
                                    <tr><th>Ano</th><th>Bimestres</th><th>Situação</th><th></th></tr>
                                </thead>
                                <tbody>
                                    {anos.map((a) => (
                                        <tr key={a.id}>
                                            <td><strong>{a.ano}</strong></td>
                                            <td className="painel-ajuda-inline">
                                                {a.bimestres.map((b) => `${b.numero}º: ${dataBR(b.inicio)} a ${dataBR(b.fim)}`).join(' · ')}
                                            </td>
                                            <td>{a.ativo ? 'Atual' : '-'}</td>
                                            <td>
                                                {!a.ativo && (
                                                    <button type="button" className="painel-botao-secundario" onClick={() => handleAtivar(a)}>
                                                        Tornar atual
                                                    </button>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                    <form onSubmit={handleCriarAno} className="painel-subform">
                        <h3>Cadastrar ano letivo</h3>
                        <div className="painel-form">
                            <div className="painel-campo">
                                <label htmlFor="ano">Ano</label>
                                <input id="ano" type="number" min={2000} value={novoAno.ano} required
                                    onChange={(e) => setNovoAno({ ...novoAno, ano: Number(e.target.value) })} />
                            </div>
                            <label className="painel-opcao">
                                <input type="checkbox" checked={novoAno.ativo}
                                    onChange={(e) => setNovoAno({ ...novoAno, ativo: e.target.checked })} />
                                Tornar este o ano letivo atual
                            </label>
                        </div>
                        <div className="painel-bimestres">
                            {novoAno.bimestres.map((b) => (
                                <fieldset key={b.numero} className="painel-bimestre">
                                    <legend>{b.numero}º bimestre</legend>
                                    <label>Início
                                        <input type="date" value={b.inicio} required
                                            onChange={(e) => alterarBimestre(b.numero, 'inicio', e.target.value)} />
                                    </label>
                                    <label>Fim
                                        <input type="date" value={b.fim} required
                                            onChange={(e) => alterarBimestre(b.numero, 'fim', e.target.value)} />
                                    </label>
                                </fieldset>
                            ))}
                        </div>
                        <button type="submit" className="painel-botao">Cadastrar ano letivo</button>
                    </form>
                </section>

                <section className="painel-card">
                    <h2>2. Turmas</h2>
                    {anos.length === 0 ? (
                        <p className="painel-ajuda">Cadastre um ano letivo primeiro.</p>
                    ) : (
                        <>
                            <div className="painel-form">
                                <div className="painel-campo">
                                    <label htmlFor="ano-turmas">Ano letivo</label>
                                    <select id="ano-turmas" value={anoSelecionado ?? ''}
                                        onChange={(e) => setAnoSelecionado(Number(e.target.value))}>
                                        {anos.map((a) => <option key={a.id} value={a.id}>{a.ano}{a.ativo ? ' (atual)' : ''}</option>)}
                                    </select>
                                </div>
                            </div>

                            {turmas.length === 0 ? (
                                <p className="painel-ajuda painel-espaco">Nenhuma turma cadastrada em {ano?.ano}.</p>
                            ) : (
                                <div className="painel-tabela-wrapper painel-espaco">
                                    <table className="painel-tabela">
                                        <thead>
                                            <tr><th>Turma</th><th>Série</th><th>Turno</th><th>Alunos</th><th></th></tr>
                                        </thead>
                                        <tbody>
                                            {turmas.map((t) => (
                                                <tr key={t.id} className={t.id === turmaSelecionada ? 'painel-linha-ativa' : ''}>
                                                    <td><strong>{t.nome}</strong></td>
                                                    <td>{t.serie}</td>
                                                    <td>{t.turno_nome}</td>
                                                    <td>{t.total_alunos}</td>
                                                    <td className="painel-acoes-linha">
                                                        <button type="button" className="painel-botao-secundario"
                                                            onClick={() => setTurmaSelecionada(t.id)}>Disciplinas</button>
                                                        <button type="button" className="painel-botao-perigo"
                                                            onClick={() => handleExcluirTurma(t)}>Excluir</button>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}

                            <form onSubmit={handleCriarTurma} className="painel-subform">
                                <h3>Cadastrar turma em {ano?.ano}</h3>
                                <div className="painel-form">
                                    <div className="painel-campo">
                                        <label htmlFor="t-nome">Nome</label>
                                        <input id="t-nome" placeholder="Ex.: 3º A" value={novaTurma.nome} required
                                            onChange={(e) => setNovaTurma({ ...novaTurma, nome: e.target.value })} />
                                    </div>
                                    <div className="painel-campo">
                                        <label htmlFor="t-serie">Série</label>
                                        <input id="t-serie" placeholder="Ex.: 3ª série" value={novaTurma.serie} required
                                            onChange={(e) => setNovaTurma({ ...novaTurma, serie: e.target.value })} />
                                    </div>
                                    <div className="painel-campo">
                                        <label htmlFor="t-turno">Turno</label>
                                        <select id="t-turno" value={novaTurma.turno}
                                            onChange={(e) => setNovaTurma({ ...novaTurma, turno: e.target.value as Turno })}>
                                            {Object.entries(NOMES_TURNOS).map(([valor, nome]) => (
                                                <option key={valor} value={valor}>{nome}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <button type="submit" className="painel-botao">Cadastrar turma</button>
                                </div>
                            </form>
                        </>
                    )}
                </section>

                <section className="painel-card">
                    <h2>3. Disciplinas {turma ? `do ${turma.nome}` : ''}</h2>
                    {!turma ? (
                        <p className="painel-ajuda">Escolha uma turma acima, no botão "Disciplinas".</p>
                    ) : (
                        <>
                            <p className="painel-ajuda">
                                Cada disciplina pertence só a esta turma e tem um professor responsável. É ele quem vai
                                lançar as notas e as faltas.
                            </p>
                            {professores.length === 0 && (
                                <p className="painel-aviso">Cadastre o professor no painel de contas antes de criar a disciplina.</p>
                            )}

                            {disciplinas.length > 0 && (
                                <div className="painel-tabela-wrapper">
                                    <table className="painel-tabela">
                                        <thead>
                                            <tr><th>Disciplina</th><th>Carga horária</th><th>Professor</th><th></th></tr>
                                        </thead>
                                        <tbody>
                                            {disciplinas.map((d) => (
                                                <tr key={d.id}>
                                                    <td><strong>{d.nome}</strong></td>
                                                    <td>{d.carga_horaria} aulas</td>
                                                    <td>
                                                        <select aria-label={`Professor de ${d.nome}`} value={d.professor}
                                                            onChange={(e) => handleTrocarProfessor(d, Number(e.target.value))}>
                                                            {professores.map((p) => <option key={p.id} value={p.id}>{p.nome}</option>)}
                                                        </select>
                                                    </td>
                                                    <td>
                                                        <button type="button" className="painel-botao-perigo"
                                                            onClick={() => handleExcluirDisciplina(d)}>Excluir</button>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}

                            <form onSubmit={handleCriarDisciplina} className="painel-subform">
                                <h3>Cadastrar disciplina no {turma.nome}</h3>
                                <div className="painel-form">
                                    <div className="painel-campo">
                                        <label htmlFor="d-nome">Nome</label>
                                        <input id="d-nome" placeholder="Ex.: Matemática" value={novaDisciplina.nome} required
                                            onChange={(e) => setNovaDisciplina({ ...novaDisciplina, nome: e.target.value })} />
                                    </div>
                                    <div className="painel-campo">
                                        <label htmlFor="d-carga">Carga horária (aulas no ano)</label>
                                        <input id="d-carga" type="number" min={1} value={novaDisciplina.carga_horaria} required
                                            onChange={(e) => setNovaDisciplina({ ...novaDisciplina, carga_horaria: Number(e.target.value) })} />
                                    </div>
                                    <div className="painel-campo">
                                        <label htmlFor="d-professor">Professor</label>
                                        <select id="d-professor" value={novaDisciplina.professor || ''} required
                                            onChange={(e) => setNovaDisciplina({ ...novaDisciplina, professor: Number(e.target.value) })}>
                                            <option value="">Selecione</option>
                                            {professores.map((p) => <option key={p.id} value={p.id}>{p.nome}</option>)}
                                        </select>
                                    </div>
                                    <button type="submit" className="painel-botao">Cadastrar disciplina</button>
                                </div>
                            </form>
                        </>
                    )}
                </section>
            </main>
            <RodapeLegal />
        </div>
    )
}
