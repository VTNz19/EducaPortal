import politica from '../../../docs/politica-de-privacidade.md?raw'
import { DocumentoLegal } from '../components/DocumentoLegal'

export function PoliticaDePrivacidade() {
    return <DocumentoLegal conteudo={politica} />
}
