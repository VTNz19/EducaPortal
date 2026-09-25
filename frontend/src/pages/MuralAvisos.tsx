import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import type { Aviso } from '../api/avisos'
import { listarAvisos } from '../api/avisos'
import { AvisoForm } from '../components/AvisoForm'
import { AvisoList } from '../components/AvisoList'
import { useAuth } from '../context/AuthContext'
import './MuralAvisos.css'
import { RodapeLegal } from '../components/RodapeLegal'


export function MuralAvisos() {
    const [avisos, setAvisos] = useState<Aviso[]>([])
    const [carregando, setCarregando] = useState(true)
    const [mostrarForm, setMostrarForm] = useState(false)
    const { usuario, logout } = useAuth()

    async function carregarAvisos() {
        setCarregando(true)
        const dados = await listarAvisos()
        setAvisos(dados)
        setCarregando(false)
    }

    useEffect(() => {
        carregarAvisos()
    }, [])

    const ehGestor = usuario?.role === 'secretaria' || usuario?.role === 'direcao'
    const podePublicar = ehGestor || usuario?.role === 'professor'

    // Só controla quais botões aparecem. Quem realmente bloqueia é o back-end.
    function podeGerenciar(aviso: Aviso) {
        return ehGestor || (usuario?.role === 'professor' && aviso.autor === usuario?.id)
    }

    function handleAvisoCriado() {
        setMostrarForm(false)
        carregarAvisos()
    }

    return (
        <div className="mural-page">
            <header className="mural-topbar">
                <span className="mural-logo">🎓 EducaPortal</span>
                <div className="mural-topbar-usuario">
                    {ehGestor && (
                        <Link to="/secretaria" className="mural-topbar-link">Painel da secretaria</Link>
                    )}
                    {usuario && <span>{usuario.nome}</span>}
                    <button type="button" onClick={logout}>Sair</button>
                </div>
            </header>

            <main className="mural-conteudo">
                <h1>Mural de Avisos</h1>

                {podePublicar && (
                    <div className="mural-acoes">
                        <button
                            type="button"
                            className="mural-botao-enviar"
                            onClick={() => setMostrarForm((valor) => !valor)}
                        >
                            {mostrarForm ? 'Cancelar' : 'Enviar aviso'}
                        </button>
                    </div>
                )}

                {mostrarForm && <AvisoForm onAvisoCriado={handleAvisoCriado} />}

                {carregando ? (
                    <p>Carregando avisos...</p>
                ) : (
                    <AvisoList
                        avisos={avisos}
                        onAvisoAtualizado={carregarAvisos}
                        podeGerenciar={podeGerenciar}
                    />
                )}
            </main>
            <RodapeLegal />
        </div>
    )
}
