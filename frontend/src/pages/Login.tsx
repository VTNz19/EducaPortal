import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import './Login.css'

function validarEmail(email: string): string {
    if (!email.trim()) return 'Informe o e-mail.'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'E-mail inválido.'
    return ''
}

function validarSenha(senha: string): string {
    if (!senha) return 'Informe a senha.'
    if (senha.length < 6) return 'A senha deve ter ao menos 6 caracteres.'
    return ''
}

export function Login() {
    const [email, setEmail] = useState('')
    const [senha, setSenha] = useState('')
    const [erroEmail, setErroEmail] = useState('')
    const [erroSenha, setErroSenha] = useState('')
    const [erroGeral, setErroGeral] = useState('')
    const [enviando, setEnviando] = useState(false)
    const { login } = useAuth()
    const navigate = useNavigate()

    async function handleSubmit(event: FormEvent) {
        event.preventDefault()
        const msgEmail = validarEmail(email)
        const msgSenha = validarSenha(senha)
        setErroEmail(msgEmail)
        setErroSenha(msgSenha)
        setErroGeral('')

        if (msgEmail || msgSenha) return

        setEnviando(true)
        try {
            await login(email, senha)
            navigate('/mural')
        } catch {
            setErroGeral('E-mail ou senha inválidos.')
        } finally {
            setEnviando(false)
        }
    }

    return (
        <div className="login-page">
            <aside className="login-brand">
                <span className="login-brand-logo">🎓 EducaPortal</span>
                <h1>Notas, faltas e boletim, sem sair de uma única tela.</h1>
                <p>
                    Professores, alunos e responsáveis acompanham tudo em uma
                    única plataforma, de qualquer lugar.
                </p>
            </aside>

            <section className="login-form-side">
                <div className="login-form-card">
                    <h2>Entrar</h2>
                    <p className="login-subtitulo">
                        Informe suas credenciais para acessar o sistema.
                    </p>

                    <form onSubmit={handleSubmit} noValidate>
                        {erroGeral && (
                            <p className="login-erro-geral" role="alert">{erroGeral}</p>
                        )}

                        <div className="login-field">
                            <label htmlFor="email">E-mail</label>
                            <input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                onBlur={() => setErroEmail(validarEmail(email))}
                                className={erroEmail ? 'invalido' : ''}
                                autoComplete="username"
                            />
                            {erroEmail && <p className="login-field-erro">{erroEmail}</p>}
                        </div>

                        <div className="login-field">
                            <label htmlFor="senha">Senha</label>
                            <input
                                id="senha"
                                type="password"
                                value={senha}
                                onChange={(e) => setSenha(e.target.value)}
                                onBlur={() => setErroSenha(validarSenha(senha))}
                                className={erroSenha ? 'invalido' : ''}
                                autoComplete="current-password"
                            />
                            {erroSenha && <p className="login-field-erro">{erroSenha}</p>}
                        </div>

                        <button type="submit" className="login-submit" disabled={enviando}>
                            {enviando ? 'Entrando...' : 'Entrar'}
                        </button>

                        <Link to="/esqueci-senha" className="login-esqueci-senha">
                            Esqueci minha senha
                        </Link>
                    </form>

                    <div className="login-perfis">
                        <strong>Perfis de acesso:</strong>
                        <ul>
                            <li>Administrador</li>
                            <li>Professor</li>
                            <li>Aluno/Responsável</li>
                        </ul>
                        <div className="login-rodape-links">
                            <Link to="/termo-de-uso">Termo de uso</Link>
                            <Link to="/politica-de-privacidade">Política de privacidade</Link>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    )
}
