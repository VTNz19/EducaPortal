import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { baixarBoletimPdf, listarAlunosDoBoletim, obterBoletim } from '../api/diario'
import type { Boletim as DadosBoletim } from '../api/diario'
import { mensagemDeErro } from '../api/erros'
import { useAuth } from '../context/AuthContext'
import { TopoPortal } from '../components/TopoPortal'
import { RodapeLegal } from '../components/RodapeLegal'
import './MuralAvisos.css'
import './PainelSecretaria.css'


function numero(valor: number | null, sufixo = '') {
    return valor === null ? '—' : `${valor.toFixed(1).replace('.', ',')}${sufixo}`
}

export function Boletim() {
    const { usuario } = useAuth()
    const ehGestor = usuario?.role === 'secretaria' || usuario?.role === 'direcao'
    const [params] = useSearchParams()
    const [alunos, setAlunos] = useState<{ id: number; nome: string }[]>([])
    const [alunoId, setAlunoId] = useState<number | null>(params.get('aluno') ? Number(params.get('aluno')) : null)
    const [ano, setAno] = useState<number | undefined>(undefined)
    const [boletim, setBoletim] = useState<DadosBoletim | null>(null)
    const [erro, setErro] = useState('')
    const [baixando, setBaixando] = useState(false)

    async function handleBaixarPdf() {
        if (!boletim) return
        setBaixando(true)
        setErro('')
        try {
            await baixarBoletimPdf(boletim.aluno.id, ano)
        } catch {
            setErro('Não foi possível gerar o PDF do boletim.')
        } finally {
            setBaixando(false)
        }
    }

    useEffect(() => {
        if (ehGestor) return
        listarAlunosDoBoletim().then((lista) => {
            setAlunos(lista)
            if (lista.length > 0) setAlunoId((atual) => atual ?? lista[0].id)
        })
    }, [ehGestor])

    useEffect(() => {
        if (alunoId === null) return
        obterBoletim(alunoId, ano)
            .then((dados) => {
                setErro('')
                setBoletim(dados)
            })
            .catch((error) => {
                setBoletim(null)
                setErro(mensagemDeErro(error, 'Não foi possível carregar o boletim.'))
            })
    }, [alunoId, ano])

    const semNotas = boletim?.disciplinas.every((d) => Object.values(d.notas).every((n) => n === null)) ?? false

    return (
        <div className="mural-page">
            <TopoPortal />
            <main className="painel-conteudo">
                {ehGestor && boletim && (
                    <Link to={`/secretaria/usuarios/${boletim.aluno.id}`} className="painel-voltar">&larr; Voltar para o perfil</Link>
                )}
                <h1>Boletim</h1>

                <section className="painel-card">
                    <div className="painel-form">
                        {alunos.length > 1 && (
                            <div className="painel-campo">
                                <label htmlFor="aluno">Aluno</label>
                                <select id="aluno" value={alunoId ?? ''} onChange={(e) => { setAno(undefined); setAlunoId(Number(e.target.value)) }}>
                                    {alunos.map((a) => <option key={a.id} value={a.id}>{a.nome}</option>)}
                                </select>
                            </div>
                        )}
                        {boletim && boletim.anos.length > 1 && (
                            <div className="painel-campo">
                                <label htmlFor="ano">Ano letivo</label>
                                <select id="ano" value={ano ?? boletim.ano} onChange={(e) => setAno(Number(e.target.value))}>
                                    {boletim.anos.map((a) => <option key={a} value={a}>{a}</option>)}
                                </select>
                            </div>
                        )}
                    </div>
                    {!ehGestor && alunos.length === 0 && (
                        <p className="painel-ajuda">Nenhum aluno vinculado à sua conta. Procure a secretaria.</p>
                    )}
                    {erro && <p className="painel-erro" role="alert">{erro}</p>}
                </section>

                {boletim && (
                    <section className="painel-card">
                        <div className="perfil-cabecalho">
                            <h2>{boletim.aluno.nome}</h2>
                            <button type="button" className="painel-botao" onClick={handleBaixarPdf}
                                disabled={baixando || semNotas}>
                                {baixando ? 'Gerando...' : 'Baixar PDF'}
                            </button>
                        </div>
                        <p className="painel-ajuda">
                            Turma {boletim.turma} – {boletim.ano}. Média mínima 6,0 e frequência mínima de 75%
                            (destacadas em vermelho quando abaixo). Médias de anos em andamento são parciais.
                        </p>
                        {semNotas && <p className="painel-aviso">Ainda não há notas publicadas neste ano letivo.</p>}
                        <div className="painel-tabela-wrapper">
                            <table className="painel-tabela painel-boletim">
                                <thead>
                                    <tr>
                                        <th>Disciplina</th>
                                        <th>1º</th><th>2º</th><th>3º</th><th>4º</th>
                                        <th>Média</th><th>Faltas</th><th>Frequência</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {boletim.disciplinas.map((d) => (
                                        <tr key={d.disciplina_id}>
                                            <td>
                                                <strong>{d.disciplina}</strong>
                                                <span className="painel-ajuda-inline">{d.professor}</span>
                                            </td>
                                            {(['1', '2', '3', '4'] as const).map((b) => (
                                                <td key={b} className={d.notas[b] !== null && d.notas[b]! < 6 ? 'painel-abaixo' : ''}>
                                                    {numero(d.notas[b])}
                                                </td>
                                            ))}
                                            <td className={d.abaixo_media ? 'painel-abaixo' : ''}>
                                                <strong>{numero(d.media)}</strong>
                                                {d.media_parcial && <span className="painel-ajuda-inline">parcial</span>}
                                            </td>
                                            <td>{d.faltas}</td>
                                            <td className={d.abaixo_frequencia ? 'painel-abaixo' : ''}>{numero(d.frequencia, '%')}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </section>
                )}
            </main>
            <RodapeLegal />
        </div>
    )
}
