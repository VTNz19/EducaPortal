import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { redefinirSenha } from '../api/senha'
import './Login.css'
import { CampoSenha } from '../components/CampoSenha'

const TAMANHO_MINIMO_SENHA = 8

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
        if (novaSenha.length < TAMANHO_MINIMO_SENHA) {
            setErro(`A senha deve ter no mínimo ${TAMANHO_MINIMO_SENHA} caracteres.`)
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
                                <CampoSenha
                                    id="nova-senha"
                                    value={novaSenha}
                                    onChange={(e) => setNovaSenha(e.target.value)}
                                    minLength={TAMANHO_MINIMO_SENHA}
                                    autoComplete="new-password"
                                    aria-describedby="regra-senha"
                                    required
                                />
                                <p id="regra-senha" className={`login-field-regra${novaSenha && novaSenha.length < TAMANHO_MINIMO_SENHA ? ' login-field-regra-falta' : ''}`}>
                                    Mínimo de {TAMANHO_MINIMO_SENHA} caracteres{novaSenha ? ` (${novaSenha.length} digitado${novaSenha.length === 1 ? '' : 's'})` : ''}.
                                </p>
                            </div>

                            <div className="login-field">
                                <label htmlFor="confirmar-senha">Confirmar nova senha</label>
                                <CampoSenha
                                    id="confirmar-senha"
                                    value={confirmarSenha}
                                    onChange={(e) => setConfirmarSenha(e.target.value)}
                                    autoComplete="new-password"
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
