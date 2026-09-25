import termo from '../../../docs/termo-de-uso.md?raw'
import { DocumentoLegal } from '../components/DocumentoLegal'

export function TermoDeUso() {
    return <DocumentoLegal conteudo={termo} />
}
