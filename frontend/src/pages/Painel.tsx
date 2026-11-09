import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { formatar, listarAlunosNaSituacao, obterPainel } from '../api/painel'
import type {
    AlunoNaSituacao, DadosPainel, DisciplinaDoProfessor, Pendencia, PainelAluno, PainelGestor,
    PainelProfessor, Situacao,
} from '../api/painel'
import { mensagemDeErro } from '../api/erros'
import { BarrasComMinimo, EvolucaoBimestral, PercentuaisPorTurma } from '../components/GraficosPainel'
import { TopoPortal } from '../components/TopoPortal'
import { RodapeLegal } from '../components/RodapeLegal'
import './MuralAvisos.css'
import './PainelSecretaria.css'
import './Painel.css'

const ESCALA_MEDIA = { minimo: 6, rotuloMinimo: 'Mínimo 6,0', marcas: [0, 2, 4, 6, 8, 10] }
const ESCALA_FREQUENCIA = { minimo: 75, rotuloMinimo: 'Mínimo 75%', marcas: [0, 25, 50, 75, 100], sufixo: '%' }
const SEM_DADOS = 'Ainda não há notas ou chamadas registradas neste bimestre.'

function Numero({ rotulo, valor, detalhe, alerta = false }: {
    rotulo: string
    valor: string | number
    detalhe?: string
    alerta?: boolean
}) {
    return (
        <div className={`numero-card${alerta ? ' numero-card-alerta' : ''}`}>
            <span className="numero-rotulo">{rotulo}</span>
            <strong className="numero-valor">{alerta && <span aria-hidden="true">⚠ </span>}{valor}</strong>
            {detalhe && <span className="numero-detalhe">{detalhe}</span>}
        </div>
    )
}

function Pendencias({ pendencias, mostrarProfessor }: { pendencias: Pendencia[]; mostrarProfessor: boolean }) {
    return (
        <section className="painel-card">
            <h2>Notas ainda não publicadas</h2>
            {pendencias.length === 0 ? (
                <p className="painel-ajuda">Todas as disciplinas estão com as notas do bimestre publicadas.</p>
            ) : (
                <div className="painel-tabela-wrapper">
                    <table className="painel-tabela">
                        <thead>
                            <tr>
                                <th>Disciplina</th>
                                <th>Turma</th>
                                {mostrarProfessor && <th>Professor</th>}
                                <th>Alunos sem nota publicada</th>
                            </tr>
                        </thead>
                        <tbody>
                            {pendencias.map((p) => (
                                <tr key={p.disciplina_id}>
                                    <td>{p.disciplina}</td>
                                    <td>{p.turma}</td>
                                    {mostrarProfessor && <td>{p.professor}</td>}
                                    <td>{p.sem_nota_publicada}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </section>
    )
}

function SeletorBimestre({ valor, onChange }: { valor: number; onChange: (numero: number) => void }) {
    return (
        <div className="painel-campo painel-seletor">
            <label htmlFor="bimestre">Bimestre</label>
            <select id="bimestre" value={valor} onChange={(e) => onChange(Number(e.target.value))}>
                {[1, 2, 3, 4].map((n) => <option key={n} value={n}>{n}º bimestre</option>)}
            </select>
        </div>
    )
}

function VisaoAluno({ dados, onTrocarAluno }: { dados: PainelAluno; onTrocarAluno: (id: number) => void }) {
    const { resumo, disciplinas = [], evolucao = [] } = dados
    return (
        <>
            {dados.alunos.length > 1 && (
                <div className="painel-campo painel-seletor">
                    <label htmlFor="aluno">Aluno</label>
                    <select id="aluno" value={dados.aluno?.id} onChange={(e) => onTrocarAluno(Number(e.target.value))}>
                        {dados.alunos.map((a) => <option key={a.id} value={a.id}>{a.nome}</option>)}
                    </select>
                </div>
            )}
            {dados.aluno === null && <p className="painel-aviso">Nenhum aluno vinculado à sua conta. Procure a secretaria.</p>}
            {dados.aluno && dados.ano && (
                <p className="painel-ajuda painel-subtitulo">{dados.aluno.nome} · Turma {dados.turma} · {dados.ano}</p>
            )}
            {dados.aluno && dados.sem_dados && <p className="painel-aviso">{SEM_DADOS}</p>}
            {resumo && !dados.sem_dados && (
                <>
                    <div className="numeros-grid">
                        <Numero rotulo="Média geral" valor={formatar(resumo.media_geral)} detalhe="Mínimo 6,0"
                            alerta={resumo.media_geral !== null && resumo.media_geral < 6} />
                        <Numero rotulo="Frequência geral" valor={formatar(resumo.frequencia_geral, '%')} detalhe="Mínimo 75%"
                            alerta={resumo.frequencia_geral !== null && resumo.frequencia_geral < 75} />
                        <Numero rotulo="Disciplinas abaixo da média" valor={resumo.disciplinas_abaixo_media}
                            alerta={resumo.disciplinas_abaixo_media > 0} />
                        <Numero rotulo="Disciplinas abaixo da frequência" valor={resumo.disciplinas_abaixo_frequencia}
                            alerta={resumo.disciplinas_abaixo_frequencia > 0} />
                    </div>
                    <div className="graficos-grid">
                        <section className="painel-card">
                            <BarrasComMinimo titulo="Média por disciplina" {...ESCALA_MEDIA}
                                itens={disciplinas.map((d) => ({ nome: d.disciplina, valor: d.media }))} />
                        </section>
                        <section className="painel-card">
                            <BarrasComMinimo titulo="Frequência por disciplina" {...ESCALA_FREQUENCIA}
                                itens={disciplinas.map((d) => ({ nome: d.disciplina, valor: d.frequencia }))} />
                        </section>
                    </div>
                    <section className="painel-card">
                        <EvolucaoBimestral titulo="Evolução da média por bimestre" pontos={evolucao} />
                    </section>
                    <section className="painel-card">
                        <h2>Situação por disciplina</h2>
                        <p className="painel-ajuda">Médias de anos em andamento são parciais.</p>
                        <div className="painel-tabela-wrapper">
                            <table className="painel-tabela">
                                <thead>
                                    <tr><th>Disciplina</th><th>Média</th><th>Faltas</th><th>Frequência</th></tr>
                                </thead>
                                <tbody>
                                    {disciplinas.map((d) => (
                                        <tr key={d.id}>
                                            <td>{d.disciplina}</td>
                                            <td className={d.abaixo_media ? 'painel-abaixo' : ''}>
                                                {formatar(d.media)}{d.abaixo_media && ' (abaixo do mínimo)'}
                                            </td>
                                            <td>{d.faltas}</td>
                                            <td className={d.abaixo_frequencia ? 'painel-abaixo' : ''}>
                                                {formatar(d.frequencia, '%')}{d.abaixo_frequencia && ' (abaixo do mínimo)'}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <Link to={dados.aluno ? `/boletim?aluno=${dados.aluno.id}` : '/boletim'} className="painel-link">Ver boletim completo</Link>
                    </section>
                </>
            )}
        </>
    )
}

const TITULOS: Record<Situacao, string> = {
    abaixo_media: 'Alunos com média abaixo de 6,0',
    abaixo_frequencia: 'Alunos com frequência abaixo de 75%',
}

function VisaoProfessor({ dados, onTrocarBimestre }: { dados: PainelProfessor; onTrocarBimestre: (n: number) => void }) {
    const [selecao, setSelecao] = useState<{ disciplina: DisciplinaDoProfessor; situacao: Situacao } | null>(null)
    const [lista, setLista] = useState<AlunoNaSituacao[]>([])
    const [erro, setErro] = useState('')

    async function abrirLista(disciplina: DisciplinaDoProfessor, situacao: Situacao) {
        setSelecao({ disciplina, situacao })
        setLista([])
        setErro('')
        try {
            setLista(await listarAlunosNaSituacao(disciplina.id, situacao))
        } catch (error) {
            setErro(mensagemDeErro(error, 'Não foi possível carregar a lista de alunos.'))
        }
    }

    if (dados.disciplinas.length === 0) {
        return <p className="painel-aviso">Nenhuma disciplina atribuída a você neste ano letivo.</p>
    }
    const totalMedia = dados.disciplinas.reduce((soma, d) => soma + d.abaixo_media, 0)
    const totalFrequencia = dados.disciplinas.reduce((soma, d) => soma + d.abaixo_frequencia, 0)

    return (
        <>
            {dados.bimestre && <SeletorBimestre valor={dados.bimestre.numero} onChange={onTrocarBimestre} />}
            {dados.sem_dados ? (
                <p className="painel-aviso">{SEM_DADOS}</p>
            ) : (
                <>
                    <div className="numeros-grid">
                        <Numero rotulo="Disciplinas" valor={dados.disciplinas.length} />
                        <Numero rotulo="Casos abaixo da média" valor={totalMedia} detalhe="Soma das disciplinas" alerta={totalMedia > 0} />
                        <Numero rotulo="Casos abaixo da frequência" valor={totalFrequencia} detalhe="Soma das disciplinas" alerta={totalFrequencia > 0} />
                        <Numero rotulo="Disciplinas com notas pendentes" valor={dados.pendencias.length} alerta={dados.pendencias.length > 0} />
                    </div>
                    <section className="painel-card">
                        <BarrasComMinimo titulo="Média da turma no bimestre" {...ESCALA_MEDIA}
                            itens={dados.disciplinas.map((d) => ({ nome: `${d.disciplina} – ${d.turma}`, valor: d.media_bimestre }))} />
                    </section>
                    <section className="painel-card">
                        <h2>Acompanhamento por disciplina</h2>
                        <p className="painel-ajuda">
                            A média do bimestre usa as notas publicadas. Os totais abaixo do mínimo seguem o boletim,
                            com a média e a frequência do ano. Clique em um total para ver os alunos.
                        </p>
                        <div className="painel-tabela-wrapper">
                            <table className="painel-tabela">
                                <thead>
                                    <tr>
                                        <th>Disciplina</th><th>Turma</th><th>Alunos</th><th>Média no bimestre</th>
                                        <th>Abaixo de 6,0</th><th>Abaixo de 75%</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {dados.disciplinas.map((d) => (
                                        <tr key={d.id}>
                                            <td>{d.disciplina}</td>
                                            <td>{d.turma}</td>
                                            <td>{d.alunos}</td>
                                            <td>{formatar(d.media_bimestre)}</td>
                                            <td>
                                                <button type="button" className="painel-botao-link" disabled={d.abaixo_media === 0}
                                                    aria-label={`Ver ${d.abaixo_media} alunos abaixo da média em ${d.disciplina}, ${d.turma}`}
                                                    onClick={() => abrirLista(d, 'abaixo_media')}>{d.abaixo_media}</button>
                                            </td>
                                            <td>
                                                <button type="button" className="painel-botao-link" disabled={d.abaixo_frequencia === 0}
                                                    aria-label={`Ver ${d.abaixo_frequencia} alunos abaixo da frequência em ${d.disciplina}, ${d.turma}`}
                                                    onClick={() => abrirLista(d, 'abaixo_frequencia')}>{d.abaixo_frequencia}</button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </section>
                    {selecao && (
                        <section className="painel-card">
                            <h2>{TITULOS[selecao.situacao]}</h2>
                            <p className="painel-ajuda">{selecao.disciplina.disciplina} – {selecao.disciplina.turma}, em ordem alfabética.</p>
                            {erro && <p className="painel-erro" role="alert">{erro}</p>}
                            <div className="painel-tabela-wrapper">
                                <table className="painel-tabela">
                                    <thead><tr><th>Aluno</th><th>Média</th><th>Frequência</th></tr></thead>
                                    <tbody>
                                        {lista.map((a) => (
                                            <tr key={a.id}>
                                                <td>{a.nome}</td>
                                                <td>{formatar(a.media)}</td>
                                                <td>{formatar(a.frequencia, '%')}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </section>
                    )}
                </>
            )}
            <Pendencias pendencias={dados.pendencias} mostrarProfessor={false} />
        </>
    )
}

function VisaoGestor({ dados, onTrocarBimestre }: { dados: PainelGestor; onTrocarBimestre: (n: number) => void }) {
    const { resumo, evolucao = [] } = dados
    return (
        <>
            {dados.bimestre && <SeletorBimestre valor={dados.bimestre.numero} onChange={onTrocarBimestre} />}
            {!dados.bimestre && <p className="painel-aviso">Cadastre o ano letivo e os bimestres para ver os indicadores.</p>}
            {dados.bimestre && dados.sem_dados && <p className="painel-aviso">{SEM_DADOS}</p>}
            {resumo && !dados.sem_dados && (
                <>
                    <div className="numeros-grid">
                        <Numero rotulo="Alunos matriculados" valor={resumo.alunos} />
                        <Numero rotulo="Média geral" valor={formatar(resumo.media_geral)} detalhe="Mínimo 6,0"
                            alerta={resumo.media_geral !== null && resumo.media_geral < 6} />
                        <Numero rotulo="Alunos abaixo da média" valor={formatar(resumo.percentual_abaixo_media, '%')}
                            detalhe="Em ao menos uma disciplina" />
                        <Numero rotulo="Alunos abaixo da frequência" valor={formatar(resumo.percentual_abaixo_frequencia, '%')}
                            detalhe="Em ao menos uma disciplina" />
                        <Numero rotulo="Disciplinas com notas pendentes" valor={dados.pendencias.length}
                            alerta={dados.pendencias.length > 0} />
                        <Numero rotulo="Contas sem aceite do termo" valor={dados.contas_sem_aceite}
                            alerta={dados.contas_sem_aceite > 0} />
                    </div>
                    <div className="graficos-grid">
                        <section className="painel-card">
                            <BarrasComMinimo titulo="Média geral por turma" {...ESCALA_MEDIA}
                                itens={dados.turmas.map((t) => ({ nome: t.turma, valor: t.media_geral }))} />
                        </section>
                        <section className="painel-card">
                            <EvolucaoBimestral titulo="Média da escola por bimestre" pontos={evolucao} />
                        </section>
                    </div>
                    <section className="painel-card">
                        <PercentuaisPorTurma itens={dados.turmas.map((t) => ({
                            nome: t.turma,
                            abaixoMedia: t.percentual_abaixo_media,
                            abaixoFrequencia: t.percentual_abaixo_frequencia,
                        }))} />
                    </section>
                    <section className="painel-card">
                        <h2>Indicadores por turma</h2>
                        <div className="painel-tabela-wrapper">
                            <table className="painel-tabela">
                                <thead>
                                    <tr>
                                        <th>Turma</th><th>Alunos</th><th>Média geral</th>
                                        <th>Abaixo da média</th><th>Abaixo da frequência</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {dados.turmas.map((t) => (
                                        <tr key={t.id}>
                                            <td>{t.turma}</td>
                                            <td>{t.alunos}</td>
                                            <td>{formatar(t.media_geral)}</td>
                                            <td>{formatar(t.percentual_abaixo_media, '%')}</td>
                                            <td>{formatar(t.percentual_abaixo_frequencia, '%')}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </section>
                </>
            )}
            {dados.sem_dados && (
                <div className="numeros-grid">
                    <Numero rotulo="Contas sem aceite do termo" valor={dados.contas_sem_aceite}
                        alerta={dados.contas_sem_aceite > 0} />
                </div>
            )}
            {dados.bimestre && <Pendencias pendencias={dados.pendencias} mostrarProfessor />}
        </>
    )
}

export function Painel() {
    const [dados, setDados] = useState<DadosPainel | null>(null)
    const [filtros, setFiltros] = useState<{ aluno?: number; bimestre?: number }>({})
    const [erro, setErro] = useState('')

    useEffect(() => {
        obterPainel(filtros)
            .then((resposta) => {
                setErro('')
                setDados(resposta)
            })
            .catch((error) => setErro(mensagemDeErro(error, 'Não foi possível carregar o painel.')))
    }, [filtros])

    return (
        <div className="mural-page">
            <TopoPortal />
            <main className="painel-conteudo painel-indicadores">
                <h1>Painel</h1>
                {erro && <p className="painel-erro" role="alert">{erro}</p>}
                {dados?.perfil === 'aluno' && (
                    <VisaoAluno dados={dados} onTrocarAluno={(aluno) => setFiltros({ aluno })} />
                )}
                {dados?.perfil === 'professor' && (
                    <VisaoProfessor key={dados.bimestre?.numero} dados={dados} onTrocarBimestre={(bimestre) => setFiltros({ bimestre })} />
                )}
                {dados?.perfil === 'gestor' && (
                    <VisaoGestor dados={dados} onTrocarBimestre={(bimestre) => setFiltros({ bimestre })} />
                )}
            </main>
            <RodapeLegal />
        </div>
    )
}
