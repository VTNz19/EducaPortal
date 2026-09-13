import { useEffect, useState } from 'react'
import type { Aviso } from '../api/avisos'
import { listarAvisos } from '../api/avisos'
import { AvisoForm } from '../components/AvisoForm'
import { AvisoList } from '../components/AvisoList'

export function MuralAvisos() {
    const [avisos, setAvisos] = useState<Aviso[]>([])
    const [carregando, setCarregando] = useState(true)

    async function carregarAvisos() {
        setCarregando(true)
        const dados = await listarAvisos()
        setAvisos(dados)
        setCarregando(false)
    }

    useEffect(() => {
        carregarAvisos()
    }, [])

    return (
        <main>
            <h1>Mural de Avisos</h1>
            <AvisoForm onAvisoCriado={carregarAvisos} />
            {carregando ? <p>Carregando avisos...</p> : <AvisoList avisos={avisos} onAvisoExcluido={carregarAvisos} />}
        </main>
    )
}
