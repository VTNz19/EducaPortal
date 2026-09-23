import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { solicitarRedefinicaoSenha } from '../api/senha'
import './Login.css'

export function EsqueciSenha() {
    const [email, setEmail] = useState('')
    const [enviando, setEnviando] = useState(false)
    const [enviado, setEnviado] = useState(false)
    const [erro, setErro] = useState('')

    async function handleSubmit(event: FormEvent) {
        event.preventDefault()
        setErro('')
        setEnviando(true)
        try {
            await solicitarRedefinicaoSenha(email)
            setEnviado(true)
        } catch {
            setErro('Não foi possível enviar o e-mail. Tente novamente.')
        } finally {
            setEnviando(false)
        }
    }

    return (
        <div className="login-page">
            <aside className="login-brand">
                <span className="login-brand-logo">🎓 EducaPortal</span>
                <h1>Esqueceu sua senha?</h1>
                <p>Informe seu e-mail cadastrado e enviaremos um link para você criar uma nova senha.</p>
            </aside>

            <section className="login-form-side">
                <div className="login-form-card">
                    <h2>Recuperar senha</h2>

                    {enviado ? (
                        <p className="login-subtitulo">
                            Se esse e-mail estiver cadastrado, você vai receber um link de
                            redefinição em instantes. Confere sua caixa de entrada (e o spam).
                        </p>
                    ) : (
                        <form onSubmit={handleSubmit} noValidate>
                            {erro && <p className="login-erro-geral" role="alert">{erro}</p>}

                            <div className="login-field">
                                <label htmlFor="email">E-mail</label>
                                <input
                                    id="email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>

                            <button type="submit" className="login-submit" disabled={enviando}>
                                {enviando ? 'Enviando...' : 'Enviar link de redefinição'}
                            </button>
                        </form>
                    )}

                    <Link to="/login" className="login-esqueci-senha">Voltar para o login</Link>
                </div>
            </section>
        </div>
    )
}
