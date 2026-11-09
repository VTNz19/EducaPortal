import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { isAxiosError } from 'axios'
import { buscarUsuario, exportarDadosUsuario, listarLogsUsuario, listarPorPerfil, NOMES_PAPEIS } from '../api/usuarios'
import type { RegistroLog, UsuarioDetalhe, UsuarioResumo } from '../api/usuarios'
import {
    desvincularResponsavel, listarTurmas, rematricularAluno, transferirAluno, vincularResponsavel,
} from '../api/academico'
import type { Turma } from '../api/academico'
import { mensagemDeErro } from '../api/erros'
import { useAuth } from '../context/AuthContext'
import { TopoPortal } from '../components/TopoPortal'
import { RodapeLegal } from '../components/RodapeLegal'
import './MuralAvisos.css'
import './PainelSecretaria.css'


const NOMES_ACOES: Record<string, string> = {
    login_sucesso: 'Login realizado',
    login_falha: 'Tentativa de login falhou',
    aviso_criado: 'Aviso criado',
    aviso_editado: 'Aviso editado',
    aviso_excluido: 'Aviso excluído',
    esqueci_senha_solicitado: 'Pediu redefinição de senha',
    esqueci_senha_falha_envio: 'Falha ao enviar e-mail de redefinição',
    senha_redefinida: 'Senha redefinida',
    usuario_criado: 'Criou uma conta',
    convite_falha_envio: 'Falha ao enviar e-mail de primeiro acesso',
    dados_exportados: 'Exportou dados de um usuário',
    termos_aceitos: 'Aceitou o termo de uso',
    matricula_criada: 'Matrícula criada',
    matricula_transferida: 'Transferência de turma',
    vinculo_criado: 'Vínculo de responsável criado',
    vinculo_removido: 'Vínculo de responsável removido',
    ano_letivo_criado: 'Ano letivo cadastrado',
    ano_letivo_editado: 'Ano letivo alterado',
    turma_criada: 'Turma cadastrada',
    turma_excluida: 'Turma excluída',
    disciplina_criada: 'Disciplina cadastrada',
    disciplina_excluida: 'Disciplina excluída',
    professor_alterado: 'Professor da disciplina alterado',
    notas_lancadas: 'Lançou notas',
    notas_publicadas: 'Publicou notas',
    nota_alterada: 'Corrigiu nota publicada',
    chamada_registrada: 'Registrou chamada',
    chamada_alterada: 'Corrigiu chamada',
    notificacao_falha_envio: 'Falha ao enviar aviso por e-mail',
    aviso_notificado: 'Aviso enviado por e-mail',
    aviso_falha_envio: 'Falha ao enviar aviso do mural por e-mail',
    boletim_emitido: 'Emitiu boletim em PDF',
}

const NOMES_SITUACAO: Record<string, string> = {
    ativa: 'Ativa',
    transferida: 'Transferida',
    encerrada: 'Encerrada',
}

function dataBR(iso: string) {
    return new Date(`${iso}T00:00:00`).toLocaleDateString('pt-BR')
}

function baixarJson(dados: unknown, nomeArquivo: string) {
    const blob = new Blob([JSON.stringify(dados, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = nomeArquivo
    link.click()
    URL.revokeObjectURL(url)
}

export function PerfilUsuario() {
    const { id } = useParams()
    const usuarioId = Number(id)
    const ehDirecao = useAuth().usuario?.role === 'direcao'
    const [perfil, setPerfil] = useState<UsuarioDetalhe | null>(null)
    const [logs, setLogs] = useState<RegistroLog[]>([])
    const [carregando, setCarregando] = useState(true)
    const [exportando, setExportando] = useState(false)
    const [erro, setErro] = useState('')
    const [mensagem, setMensagem] = useState('')
    const [turmas, setTurmas] = useState<Turma[]>([])
    const [responsaveis, setResponsaveis] = useState<UsuarioResumo[]>([])
    const [turmaDestino, setTurmaDestino] = useState('')
    const [responsavelNovo, setResponsavelNovo] = useState('')

    useEffect(() => {
        async function carregar() {
            setCarregando(true)
            setErro('')
            setMensagem('')
            try {
                const [dados, registros] = await Promise.all([
                    buscarUsuario(usuarioId),
                    ehDirecao ? listarLogsUsuario(usuarioId) : Promise.resolve([]),
                ])
                setPerfil(dados)
                setLogs(registros)
                if (dados.role === 'aluno') {
                    const [listaTurmas, listaResponsaveis] = await Promise.all([
                        listarTurmas(), listarPorPerfil('responsavel'),
                    ])
                    setTurmas(listaTurmas)
                    setResponsaveis(listaResponsaveis)
                }
            } catch {
                setErro('Não foi possível carregar este usuário.')
            } finally {
                setCarregando(false)
            }
        }
        carregar()
    }, [usuarioId, ehDirecao])

    async function handleExportar() {
        setExportando(true)
        setErro('')
        try {
            const dados = await exportarDadosUsuario(usuarioId)
            const hoje = new Date().toISOString().slice(0, 10)
            baixarJson(dados, `educaportal-usuario-${usuarioId}-${hoje}.json`)
        } catch {
            setErro('Não foi possível exportar os dados.')
        } finally {
            setExportando(false)
        }
    }

    async function executar(operacao: () => Promise<UsuarioDetalhe>, sucesso: string) {
        setErro('')
        setMensagem('')
        try {
            setPerfil(await operacao())
            setMensagem(sucesso)
            setTurmaDestino('')
            setResponsavelNovo('')
        } catch (error) {
            setErro(mensagemDeErro(error, 'Não foi possível concluir a operação.'))
        }
    }

    async function handleDesvincular(responsavel: number, nome: string) {
        setErro('')
        setMensagem('')
        try {
            setPerfil(await desvincularResponsavel(usuarioId, responsavel))
            setMensagem(`Vínculo com ${nome} removido.`)
        } catch (error) {
            if (isAxiosError(error) && error.response?.status === 409) {
                if (window.confirm(error.response.data.detail)) {
                    await executar(() => desvincularResponsavel(usuarioId, responsavel, true), `Vínculo com ${nome} removido.`)
                }
                return
            }
            setErro(mensagemDeErro(error, 'Não foi possível remover o vínculo.'))
        }
    }

    const matriculaAtiva = perfil?.matriculas.find((m) => m.situacao === 'ativa')
    const anoAtivo = matriculaAtiva?.ano
    const turmasMesmoAno = turmas.filter((t) => t.ano === anoAtivo && t.id !== matriculaAtiva?.turma_id)
    const turmasOutrosAnos = turmas.filter((t) => t.ano !== anoAtivo)
    const destino = turmas.find((t) => t.id === Number(turmaDestino))
    const vinculados = new Set(perfil?.vinculos.map((v) => v.id))

    function handleMudarTurma() {
        if (!destino) return
        if (destino.ano === anoAtivo) {
            executar(() => transferirAluno(usuarioId, destino.id), `Aluno transferido para ${destino.nome}.`)
        } else {
            executar(() => rematricularAluno(usuarioId, destino.id), `Aluno rematriculado em ${destino.nome} (${destino.ano}).`)
        }
    }

    return (
        <div className="mural-page">
            <TopoPortal />

            <main className="painel-conteudo">
                <Link to="/secretaria" className="painel-voltar">&larr; Voltar para o painel</Link>

                {carregando && <p>Carregando...</p>}

                {!carregando && !perfil && <p className="painel-erro">{erro}</p>}

                {!carregando && perfil && (
                    <>
                        <section className="painel-card">
                            <div className="perfil-cabecalho">
                                <h2>{perfil.nome}</h2>
                                {ehDirecao && (
                                    <button
                                        type="button"
                                        className="painel-botao"
                                        onClick={handleExportar}
                                        disabled={exportando}
                                    >
                                        {exportando ? 'Exportando...' : 'Exportar dados (JSON)'}
                                    </button>
                                )}
                            </div>
                            <dl className="perfil-dados">
                                <dt>E-mail</dt>
                                <dd>{perfil.email}</dd>
                                <dt>Perfil</dt>
                                <dd>{NOMES_PAPEIS[perfil.role] ?? perfil.role}</dd>
                                <dt>Situação</dt>
                                <dd>{perfil.is_active ? 'Ativa' : 'Inativa'}</dd>
                                <dt>Conta criada em</dt>
                                <dd>{new Date(perfil.date_joined).toLocaleString('pt-BR')}</dd>
                            </dl>
                            {erro && <p className="painel-erro" role="alert">{erro}</p>}
                            {mensagem && <p className="painel-sucesso" role="status">{mensagem}</p>}
                        </section>

                        {perfil.role === 'aluno' && (
                            <section className="painel-card">
                                <div className="perfil-cabecalho">
                                    <h2>Matrícula</h2>
                                    <Link to={`/boletim?aluno=${perfil.id}`} className="painel-botao-secundario">Ver boletim</Link>
                                </div>
                                <p className="painel-ajuda">
                                    {matriculaAtiva
                                        ? `Turma atual: ${matriculaAtiva.turma} (${matriculaAtiva.ano}).`
                                        : 'Sem matrícula ativa.'}{' '}
                                    O histórico de matrículas nunca é apagado.
                                </p>
                                <div className="painel-tabela-wrapper">
                                    <table className="painel-tabela">
                                        <thead>
                                            <tr><th>Ano</th><th>Turma</th><th>Situação</th><th>Início</th><th>Fim</th></tr>
                                        </thead>
                                        <tbody>
                                            {perfil.matriculas.map((m) => (
                                                <tr key={m.id}>
                                                    <td>{m.ano}</td>
                                                    <td>{m.turma}</td>
                                                    <td>{NOMES_SITUACAO[m.situacao]}</td>
                                                    <td>{dataBR(m.data_inicio)}</td>
                                                    <td>{m.data_fim ? dataBR(m.data_fim) : '-'}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>

                                <div className="painel-form painel-subform">
                                    <div className="painel-campo">
                                        <label htmlFor="turma-destino">Nova turma</label>
                                        <select id="turma-destino" value={turmaDestino} onChange={(e) => setTurmaDestino(e.target.value)}>
                                            <option value="">Selecione</option>
                                            {turmasMesmoAno.length > 0 && (
                                                <optgroup label={`Transferir em ${anoAtivo}`}>
                                                    {turmasMesmoAno.map((t) => <option key={t.id} value={t.id}>{t.nome}</option>)}
                                                </optgroup>
                                            )}
                                            {turmasOutrosAnos.length > 0 && (
                                                <optgroup label="Rematricular em outro ano">
                                                    {turmasOutrosAnos.map((t) => <option key={t.id} value={t.id}>{t.nome} ({t.ano})</option>)}
                                                </optgroup>
                                            )}
                                        </select>
                                    </div>
                                    <button type="button" className="painel-botao" disabled={!destino} onClick={handleMudarTurma}>
                                        {destino && destino.ano !== anoAtivo ? 'Rematricular' : 'Transferir'}
                                    </button>
                                </div>
                            </section>
                        )}

                        {(perfil.role === 'aluno' || perfil.role === 'responsavel') && (
                            <section className="painel-card">
                                <h2>{perfil.role === 'aluno' ? 'Responsáveis' : 'Alunos vinculados'}</h2>
                                {perfil.vinculos.length === 0 ? (
                                    <p className="painel-ajuda">Nenhum vínculo cadastrado.</p>
                                ) : (
                                    <ul className="painel-lista">
                                        {perfil.vinculos.map((v) => (
                                            <li key={v.id}>
                                                <Link to={`/secretaria/usuarios/${v.id}`} className="painel-link">{v.nome}</Link>
                                                <span className="painel-ajuda-inline">{v.email}</span>
                                                {perfil.role === 'aluno' && (
                                                    <button type="button" className="painel-botao-perigo"
                                                        onClick={() => handleDesvincular(v.id, v.nome)}>Desvincular</button>
                                                )}
                                            </li>
                                        ))}
                                    </ul>
                                )}

                                {perfil.role === 'aluno' ? (
                                    <div className="painel-form painel-subform">
                                        <div className="painel-campo">
                                            <label htmlFor="responsavel-novo">Vincular responsável já cadastrado</label>
                                            <select id="responsavel-novo" value={responsavelNovo}
                                                onChange={(e) => setResponsavelNovo(e.target.value)}>
                                                <option value="">Selecione</option>
                                                {responsaveis.filter((r) => !vinculados.has(r.id)).map((r) => (
                                                    <option key={r.id} value={r.id}>{r.nome} ({r.email})</option>
                                                ))}
                                            </select>
                                        </div>
                                        <button type="button" className="painel-botao" disabled={!responsavelNovo}
                                            onClick={() => executar(() => vincularResponsavel(usuarioId, Number(responsavelNovo)), 'Responsável vinculado.')}>
                                            Vincular
                                        </button>
                                    </div>
                                ) : (
                                    <p className="painel-ajuda painel-espaco">
                                        Para vincular este responsável a outro aluno, abra o perfil do aluno.
                                    </p>
                                )}
                            </section>
                        )}

                        {ehDirecao && (
                            <section className="painel-card">
                                <h2>Registro de atividades</h2>
                                <p className="painel-ajuda">
                                    Ações feitas por esta pessoa no sistema. A tela mostra as 200
                                    mais recentes; a exportação inclui o histórico completo.
                                </p>
                                {logs.length === 0 ? (
                                    <p>Nenhuma atividade registrada.</p>
                                ) : (
                                    <div className="painel-tabela-wrapper">
                                        <table className="painel-tabela">
                                            <thead>
                                                <tr>
                                                    <th>Data e hora</th>
                                                    <th>Ação</th>
                                                    <th>Detalhes</th>
                                                    <th>IP</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {logs.map((log) => (
                                                    <tr key={log.id}>
                                                        <td>{new Date(log.criado_em).toLocaleString('pt-BR')}</td>
                                                        <td>{NOMES_ACOES[log.acao] ?? log.acao}</td>
                                                        <td className="perfil-detalhes">{log.detalhes || '-'}</td>
                                                        <td>{log.endereco_ip ?? '-'}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                            </section>
                        )}
                    </>
                )}
            </main>
            <RodapeLegal />
        </div>
    )
}
