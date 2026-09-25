import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { buscarUsuario, exportarDadosUsuario, listarLogsUsuario, NOMES_PAPEIS } from '../api/usuarios'
import type { RegistroLog, UsuarioDetalhe } from '../api/usuarios'
import { useAuth } from '../context/AuthContext'
import './MuralAvisos.css'
import './PainelSecretaria.css'
import { RodapeLegal } from '../components/RodapeLegal'


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
    const { usuario, logout } = useAuth()
    const [perfil, setPerfil] = useState<UsuarioDetalhe | null>(null)
    const [logs, setLogs] = useState<RegistroLog[]>([])
    const [carregando, setCarregando] = useState(true)
    const [exportando, setExportando] = useState(false)
    const [erro, setErro] = useState('')

    useEffect(() => {
        async function carregar() {
            setCarregando(true)
            setErro('')
            try {
                const [dados, registros] = await Promise.all([
                    buscarUsuario(usuarioId),
                    listarLogsUsuario(usuarioId),
                ])
                setPerfil(dados)
                setLogs(registros)
            } catch {
                setErro('Não foi possível carregar este usuário.')
            } finally {
                setCarregando(false)
            }
        }
        carregar()
    }, [usuarioId])

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

    return (
        <div className="mural-page">
            <header className="mural-topbar">
                <span className="mural-logo">🎓 EducaPortal</span>
                <div className="mural-topbar-usuario">
                    <Link to="/mural" className="mural-topbar-link">Mural de avisos</Link>
                    {usuario && <span>{usuario.nome}</span>}
                    <button type="button" onClick={logout}>Sair</button>
                </div>
            </header>

            <main className="painel-conteudo">
                <Link to="/secretaria" className="painel-voltar">&larr; Voltar para o painel</Link>

                {carregando && <p>Carregando...</p>}

                {!carregando && !perfil && <p className="painel-erro">{erro}</p>}

                {!carregando && perfil && (
                    <>
                        <section className="painel-card">
                            <div className="perfil-cabecalho">
                                <h2>{perfil.nome}</h2>
                                <button
                                    type="button"
                                    className="painel-botao"
                                    onClick={handleExportar}
                                    disabled={exportando}
                                >
                                    {exportando ? 'Exportando...' : 'Exportar dados (JSON)'}
                                </button>
                            </div>
                            <dl className="perfil-dados">
                                <dt>E-mail</dt>
                                <dd>{perfil.email}</dd>
                                <dt>Papel</dt>
                                <dd>{NOMES_PAPEIS[perfil.role] ?? perfil.role}</dd>
                                <dt>Situação</dt>
                                <dd>{perfil.is_active ? 'Ativa' : 'Inativa'}</dd>
                                <dt>Conta criada em</dt>
                                <dd>{new Date(perfil.date_joined).toLocaleString('pt-BR')}</dd>
                            </dl>
                            {erro && <p className="painel-erro" role="alert">{erro}</p>}
                        </section>

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
                    </>
                )}
            </main>
            <RodapeLegal />
        </div>
    )
}
