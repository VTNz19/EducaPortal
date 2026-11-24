import termo from '../../../docs/termo-de-uso.md?raw'
import { DocumentoVigente } from '../components/DocumentoLegal'

export function TermoDeUso() {
    return <DocumentoVigente tipo="termo" padrao={termo} />
}
