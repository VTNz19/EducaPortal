import { useEffect, useState } from 'react'
import { obterDocumento } from '../api/documentos'
import type { TipoDocumento } from '../api/documentos'

/**
 * Texto vigente do documento: a última versão publicada pela Direção (RF23) ou, se não houver,
 * o texto que acompanha o sistema. Se a API não responder, também usa o texto do sistema.
 */
export function useDocumento(tipo: TipoDocumento, padrao: string) {
    const [conteudo, setConteudo] = useState<string | null>(null)

    useEffect(() => {
        let ativo = true
        obterDocumento(tipo)
            .then((doc) => { if (ativo) setConteudo(doc.conteudo ?? padrao) })
            .catch(() => { if (ativo) setConteudo(padrao) })
        return () => { ativo = false }
    }, [tipo, padrao])

    return conteudo
}
