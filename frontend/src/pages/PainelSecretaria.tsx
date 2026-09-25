import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { isAxiosError } from 'axios'
import { criarUsuario, listarUsuarios, NOMES_PAPEIS } from '../api/usuarios'
import type { NovoUsuario, UsuarioResumo } from '../api/usuarios'
import { useAuth } from '../context/AuthContext'
import './MuralAvisos.css'
import './PainelSecretaria.css'
import { RodapeLegal } from '../components/RodapeLegal'


const FORM_VAZIO: NovoUsuario = { first_name: '', last_name: '', email: '', role: 'aluno' }

function extrairErro(error: unknown): string {
    if (isAxiosError(error) && error.response?.data && typeof error.response.data === 'object') {
        const mensagens = Object.values(error.response.data as Record<string, unknown>).flat()
        if (mensagens.length > 0) return mensagens.join(' ')
    }
    return 'Não foi possível criar a conta. Verifique os campos e tente novamente.'
}

export function PainelSecretaria() {
    const { usuario, logout } = useAuth()
    const [usuarios, setUsuarios] = useState<UsuarioResumo[]>([])
    const [carregando, setCarregando] = useState(true)
    const [form, setForm] = useState<NovoUsuario>(FORM_VAZIO)
    const [enviando, setEnviando] = useState(false)
    const [erro, setErro] = useState('')
    const [mensagem, setMensagem] = useState('')

    async function carregarUsuarios() {
        setCarregando(true)
        setUsuarios(await listarUsuarios())
        setCarregando(false)
    }

    useEffect(() => {
        carregarUsuarios()
    }, [])

    async function handleSubmit(event: FormEvent) {
        event.preventDefault()
        setErro('')
        setMensagem('')
        setEnviando(true)
        try {
            const criado = await criarUsuario(form)
            setMensagem(
                criado.email_enviado
                    ? `Conta de ${criado.nome} criada. Enviamos um e-mail para ${criado.email} definir a senha.`
                    : `Conta de ${criado.nome} criada, mas o e-mail não pôde ser enviado. A pessoa pode usar "Esqueci minha senha" na tela de login.`
            )
            setForm(FORM_VAZIO)
            carregarUsuarios()
        } catch (error) {
            setErro(extrairErro(error))
        } finally {
            setEnviando(false)
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
                <h1>Painel da Secretaria</h1>

                <section className="painel-card">
                    <h2>Nova conta</h2>
                    <p className="painel-ajuda">
                        A pessoa recebe um e-mail para criar a própria senha. A secretaria
                        não define nem vê senhas.
                    </p>

                    <form onSubmit={handleSubmit} className="painel-form">
                        <div className="painel-campo">
                            <label htmlFor="first_name">Nome</label>
                            <input
                                id="first_name"
                                value={form.first_name}
                                onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                                required
                            />
                        </div>
                        <div className="painel-campo">
                            <label htmlFor="last_name">Sobrenome</label>
                            <input
                                id="last_name"
                                value={form.last_name}
                                onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                                required
                            />
                        </div>
                        <div className="painel-campo">
                            <label htmlFor="email">E-mail</label>
                            <input
                                id="email"
                                type="email"
                                value={form.email}
                                onChange={(e) => setForm({ ...form, email: e.target.value })}
                                required
                            />
                        </div>
                        <div className="painel-campo">
                            <label htmlFor="role">Papel</label>
                            <select
                                id="role"
                                value={form.role}
                                onChange={(e) => setForm({ ...form, role: e.target.value as NovoUsuario['role'] })}
                            >
                                <option value="aluno">Aluno</option>
                                <option value="responsavel">Responsável</option>
                                <option value="professor">Professor</option>
                            </select>
                        </div>
                        <button type="submit" className="painel-botao" disabled={enviando}>
                            {enviando ? 'Criando...' : 'Criar conta'}
                        </button>
                    </form>

                    {erro && <p className="painel-erro" role="alert">{erro}</p>}
                    {mensagem && <p className="painel-sucesso" role="status">{mensagem}</p>}
                </section>

                <section className="painel-card">
                    <h2>Contas cadastradas</h2>
                    {carregando ? (
                        <p>Carregando...</p>
                    ) : (
                        <div className="painel-tabela-wrapper">
                            <table className="painel-tabela">
                                <thead>
                                    <tr>
                                        <th>Nome</th>
                                        <th>E-mail</th>
                                        <th>Papel</th>
                                        <th>Situação</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {usuarios.map((u) => (
                                        <tr key={u.id}>
                                            <td>
                                                <Link to={`/secretaria/usuarios/${u.id}`} className="painel-link">{u.nome}</Link>
                                            </td>
                                            <td>{u.email}</td>
                                            <td>{NOMES_PAPEIS[u.role] ?? u.role}</td>
                                            <td>{u.is_active ? 'Ativa' : 'Inativa'}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </section>
            </main>
            <RodapeLegal />
        </div>
    )
}
