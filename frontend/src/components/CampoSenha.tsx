import { useState } from 'react'
import type { InputHTMLAttributes } from 'react'
import './CampoSenha.css'

type CampoSenhaProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'type'>

function OlhoAberto() {
    return (
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">
            <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z" />
            <circle cx="12" cy="12" r="3" />
        </svg>
    )
}

function OlhoFechado() {
    return (
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">
            <path d="M10.6 5.1A10.4 10.4 0 0 1 12 5c6.4 0 10 7 10 7a17.6 17.6 0 0 1-2.6 3.5" />
            <path d="M6.6 6.6A17.4 17.4 0 0 0 2 12s3.6 7 10 7a9.9 9.9 0 0 0 5.4-1.6" />
            <path d="M9.9 9.9a3 3 0 0 0 4.2 4.2" />
            <path d="M3 3l18 18" />
        </svg>
    )
}

export function CampoSenha(props: CampoSenhaProps) {
    const [visivel, setVisivel] = useState(false)
    const rotulo = visivel ? 'Ocultar senha' : 'Mostrar senha'
    return (
        <div className="campo-senha">
            <input {...props} type={visivel ? 'text' : 'password'} />
            <button
                type="button"
                className="campo-senha-botao"
                onClick={() => setVisivel((v) => !v)}
                aria-label={rotulo}
                aria-pressed={visivel}
                aria-controls={props.id}
                title={rotulo}
            >
                {visivel ? <OlhoFechado /> : <OlhoAberto />}
            </button>
        </div>
    )
}
