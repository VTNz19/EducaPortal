import politica from '../../../docs/politica-de-privacidade.md?raw'
import { DocumentoVigente } from '../components/DocumentoLegal'

export function PoliticaDePrivacidade() {
    return <DocumentoVigente tipo="politica" padrao={politica} />
}
