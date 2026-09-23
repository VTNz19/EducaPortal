import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { redefinirSenha } from '../api/senha'
import './Login.css'

export function RedefinirSenha() {
    const [searchParams] = useSearchParams()
    const token = searchParams.get('token') ?? ''
    const navigate = useNavigate()

    const [novaSenha, setNovaSenha] = useState('')
    const [confirmarSenha, setConfirmarSenha] = useState('')
    const [enviando, setEnviando] = useState(false)
    const [erro, setErro] = useState('')
    const [sucesso, setSucesso] = useState(false)

    async function handleSubmit(event: FormEvent) {
        event.preventDefault()
        setErro('')

        if (!token) {
            setErro('Link inválido: token não encontrado na URL.')
            return
        }
        if (novaSenha.length < 6) {
            setErro('A senha deve ter ao menos 6 caracteres.')
            return
        }
        if (novaSenha !== confirmarSenha) {
            setErro('As senhas não coincidem.')
            return
        }

        setEnviando(true)
        try {
            await redefinirSenha(token, novaSenha)
            setSucesso(true)
            setTimeout(() => navigate('/login'), 2500)
        } catch {
            setErro('Não foi possível redefinir a senha. O link pode estar expirado.')
        } finally {
            setEnviando(false)
        }
    }

    return (
        <div className="login-page">
            <aside className="login-brand">
                <span className="login-brand-logo">🎓 EducaPortal</span>
                <h1>Criar nova senha</h1>
                <p>Defina uma nova senha de acesso para sua conta no EducaPortal.</p>
            </aside>

            <section className="login-form-side">
                <div className="login-form-card">
                    <h2>Redefinir senha</h2>

                    {sucesso ? (
                        <p className="login-subtitulo">
                            Senha redefinida com sucesso! Redirecionando para o login...
                        </p>
                    ) : (
                        <form onSubmit={handleSubmit} noValidate>
                            {erro && <p className="login-erro-geral" role="alert">{erro}</p>}

                            <div className="login-field">
                                <label htmlFor="nova-senha">Nova senha</label>
                                <input
                                    id="nova-senha"
                                    type="password"
                                    value={novaSenha}
                                    onChange={(e) => setNovaSenha(e.target.value)}
                                    required
                                />
                            </div>

                            <div className="login-field">
                                <label htmlFor="confirmar-senha">Confirmar nova senha</label>
                                <input
                                    id="confirmar-senha"
                                    type="password"
                                    value={confirmarSenha}
                                    onChange={(e) => setConfirmarSenha(e.target.value)}
                                    required
                                />
                            </div>

                            <button type="submit" className="login-submit" disabled={enviando}>
                                {enviando ? 'Salvando...' : 'Redefinir senha'}
                            </button>
                        </form>
                    )}

                    <Link to="/login" className="login-esqueci-senha">Voltar para o login</Link>
                </div>
            </section>
        </div>
    )
}
