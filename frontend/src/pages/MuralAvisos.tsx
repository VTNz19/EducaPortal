import { useEffect, useState } from 'react'
import type { Aviso } from '../api/avisos'
import { listarAvisos } from '../api/avisos'
import { AvisoForm } from '../components/AvisoForm'
import type { OpcaoTurma } from '../components/AvisoForm'
import { listarAnosLetivos, listarDisciplinas, listarTurmas } from '../api/academico'
import { AvisoList } from '../components/AvisoList'
import { useAuth } from '../context/AuthContext'
import './MuralAvisos.css'
import { RodapeLegal } from '../components/RodapeLegal'
import { TopoPortal } from '../components/TopoPortal'


export function MuralAvisos() {
    const [avisos, setAvisos] = useState<Aviso[]>([])
    const [carregando, setCarregando] = useState(true)
    const [mostrarForm, setMostrarForm] = useState(false)
    const [turmas, setTurmas] = useState<OpcaoTurma[]>([])
    const { usuario } = useAuth()

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

    useEffect(() => {
        if (usuario?.role === 'professor') {
            listarDisciplinas().then((disciplinas) => {
                const unicas = new Map(disciplinas.map((d) => [d.turma, { id: d.turma, nome: d.turma_nome }]))
                setTurmas([...unicas.values()])
            })
        } else if (usuario?.role === 'secretaria' || usuario?.role === 'direcao') {
            listarAnosLetivos().then(async (anos) => {
                const atual = anos.find((a) => a.ativo)
                if (atual) setTurmas((await listarTurmas(atual.id)).map((t) => ({ id: t.id, nome: t.nome })))
            })
        }
    }, [usuario?.role])

    function podeGerenciar(aviso: Aviso) {
        return ehGestor || (usuario?.role === 'professor' && aviso.autor === usuario?.id)
    }

    function handleAvisoCriado() {
        setMostrarForm(false)
        carregarAvisos()
    }

    return (
        <div className="mural-page">
            <TopoPortal />

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

                {mostrarForm && <AvisoForm turmas={turmas} onSalvo={handleAvisoCriado} />}

                {carregando ? (
                    <p>Carregando avisos...</p>
                ) : (
                    <AvisoList
                        avisos={avisos}
                        turmas={turmas}
                        onAvisoAtualizado={carregarAvisos}
                        podeGerenciar={podeGerenciar}
                    />
                )}
            </main>
            <RodapeLegal />
        </div>
    )
}
