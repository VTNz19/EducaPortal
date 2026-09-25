import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { solicitarRedefinicaoSenha } from '../api/senha'
import './Login.css'

interface EsqueciSenhaProps {
    primeiroAcesso?: boolean
}

const TEXTOS = {
    redefinir: {
        tituloLateral: 'Esqueceu sua senha?',
        descricao: 'Informe seu e-mail cadastrado e enviaremos um link para você criar uma nova senha.',
        titulo: 'Recuperar senha',
        botao: 'Enviar link de redefinição',
        enviado: 'Se esse e-mail estiver cadastrado, você vai receber um link de redefinição em instantes. Confere sua caixa de entrada (e o spam).',
    },
    primeiroAcesso: {
        tituloLateral: 'Primeiro acesso',
        descricao: 'Sua conta foi criada pela secretaria da escola. Informe seu e-mail e enviaremos um link para você criar sua senha.',
        titulo: 'Criar minha senha',
        botao: 'Enviar link de acesso',
        enviado: 'Se esse e-mail estiver cadastrado, você vai receber um link para criar sua senha em instantes. Confere sua caixa de entrada (e o spam).',
    },
}

export function EsqueciSenha({ primeiroAcesso = false }: EsqueciSenhaProps) {
    const textos = primeiroAcesso ? TEXTOS.primeiroAcesso : TEXTOS.redefinir
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
                <h1>{textos.tituloLateral}</h1>
                <p>{textos.descricao}</p>
            </aside>

            <section className="login-form-side">
                <div className="login-form-card">
                    <h2>{textos.titulo}</h2>

                    {enviado ? (
                        <p className="login-subtitulo">{textos.enviado}</p>
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
                                {enviando ? 'Enviando...' : textos.botao}
                            </button>
                        </form>
                    )}

                    <Link to="/login" className="login-esqueci-senha">Voltar para o login</Link>
                </div>
            </section>
        </div>
    )
}
