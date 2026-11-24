import { useEffect, useState } from 'react'
import termoOriginal from '../../../docs/termo-de-uso.md?raw'
import politicaOriginal from '../../../docs/politica-de-privacidade.md?raw'
import {
    listarVersoes,
    NOMES_DOCUMENTOS,
    obterDocumento,
    proximaVersao,
    publicarDocumento,
} from '../api/documentos'
import type { DocumentoPublicado, TipoDocumento, VersaoDocumento } from '../api/documentos'
import { mensagemDeErro } from '../api/erros'
import { ConteudoMarkdown } from '../components/DocumentoLegal'
import { RodapeLegal } from '../components/RodapeLegal'
import { TopoPortal } from '../components/TopoPortal'
import './MuralAvisos.css'
import './PainelSecretaria.css'
import './Painel.css'
import './DocumentosLegais.css'

const ORIGINAIS: Record<TipoDocumento, string> = { termo: termoOriginal, politica: politicaOriginal }
const TIPOS: TipoDocumento[] = ['termo', 'politica']

function dataHora(valor: string) {
    return new Date(valor).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

/** Tela da Direção para publicar novas versões do Termo de Uso e da Política de Privacidade (RF23). */
export function DocumentosLegais() {
    const [tipo, setTipo] = useState<TipoDocumento>('termo')
    const [vigente, setVigente] = useState<DocumentoPublicado | null>(null)
    const [versoes, setVersoes] = useState<VersaoDocumento[]>([])
    const [texto, setTexto] = useState('')
    const [resumo, setResumo] = useState('')
    const [confirmado, setConfirmado] = useState(false)
    const [previa, setPrevia] = useState(false)
    const [publicando, setPublicando] = useState(false)
    const [erro, setErro] = useState('')

    useEffect(() => {
        let ativo = true
        Promise.all([obterDocumento(tipo), listarVersoes(tipo)])
            .then(([doc, lista]) => {
                if (!ativo) return
                setVigente(doc)
                setVersoes(lista)
                setTexto(doc.conteudo ?? ORIGINAIS[tipo])
                setResumo('')
                setConfirmado(false)
                setPrevia(false)
            })
            .catch((error) => { if (ativo) setErro(mensagemDeErro(error, 'Não foi possível carregar o documento.')) })
        return () => { ativo = false }
    }, [tipo])

    const textoVigente = vigente ? vigente.conteudo ?? ORIGINAIS[tipo] : ''
    const alterado = vigente !== null && texto.trim() !== textoVigente.trim()
    const novaVersao = vigente ? proximaVersao(vigente.versao) : ''
    const podePublicar = alterado && resumo.trim() !== '' && confirmado && !publicando

    function trocarDocumento(novo: TipoDocumento) {
        if (novo === tipo) return
        setVigente(null)
        setErro('')
        setTipo(novo)
    }

    async function handlePublicar() {
        setErro('')
        setPublicando(true)
        try {
            await publicarDocumento(tipo, texto, resumo.trim())
            // quem publicou também precisa aceitar a nova versão: recarrega para ir à tela de aceite
            window.location.assign('/aceite-termos')
        } catch (error) {
            setErro(mensagemDeErro(error, 'Não foi possível publicar a nova versão.'))
            setPublicando(false)
        }
    }

    return (
        <div className="mural-page">
            <TopoPortal />
            <main className="painel-conteudo">
                <h1>Documentos legais</h1>
                <p className="painel-ajuda">
                    Publique aqui uma nova versão do Termo de Uso e Aceite ou da Política de Privacidade. Cada
                    publicação recebe um novo número de versão, fica guardada no histórico e faz com que todos os
                    usuários, inclusive você, precisem aceitar os documentos de novo no próximo acesso.
                </p>

                <div className="documentos-abas" role="tablist" aria-label="Documento">
                    {TIPOS.map((t) => (
                        <button key={t} type="button" role="tab" aria-selected={tipo === t}
                            className={tipo === t ? 'painel-botao' : 'painel-botao-secundario'}
                            onClick={() => trocarDocumento(t)} disabled={publicando}>
                            {NOMES_DOCUMENTOS[t]}
                        </button>
                    ))}
                </div>

                {erro && <p className="painel-erro" role="alert">{erro}</p>}

                {!vigente ? (
                    !erro && <p>Carregando...</p>
                ) : (
                    <>
                        <section className="painel-card">
                            <h2>{NOMES_DOCUMENTOS[tipo]}</h2>
                            <p className="documentos-vigente">
                                Versão vigente: <strong>{vigente.versao}</strong>
                                {vigente.publicado_em
                                    ? ` · publicada em ${dataHora(vigente.publicado_em)}${vigente.publicado_por ? ` por ${vigente.publicado_por}` : ''}`
                                    : ' · texto original do sistema'}
                            </p>

                            <div className="documentos-barra">
                                <span className="painel-ajuda-inline">
                                    O texto usa Markdown: # para títulos, **negrito** e - no início da linha para listas.
                                    Atualize também a versão e a data escritas no início do documento.
                                </span>
                                <button type="button" className="painel-botao-secundario" onClick={() => setPrevia((p) => !p)}>
                                    {previa ? 'Voltar a editar' : 'Ver como vai ficar'}
                                </button>
                            </div>

                            {previa ? (
                                <div className="documentos-previa legal-page">
                                    <ConteudoMarkdown conteudo={texto} />
                                </div>
                            ) : (
                                <div className="painel-campo">
                                    <label htmlFor="texto-documento">Texto do documento</label>
                                    <textarea id="texto-documento" className="documentos-editor" value={texto}
                                        spellCheck onChange={(e) => setTexto(e.target.value)} />
                                </div>
                            )}

                            <div className="painel-campo">
                                <label htmlFor="resumo-documento">O que mudou nesta versão</label>
                                <input id="resumo-documento" type="text" maxLength={300} value={resumo}
                                    placeholder="Ex.: Inclui o prazo de guarda dos anexos das tarefas"
                                    onChange={(e) => setResumo(e.target.value)} />
                            </div>

                            <label className="painel-opcao">
                                <input type="checkbox" checked={confirmado} onChange={(e) => setConfirmado(e.target.checked)} />
                                <span>
                                    Entendo que, ao publicar a versão {novaVersao}, todos os usuários precisarão aceitar
                                    os documentos de novo e que esta ação não pode ser desfeita.
                                </span>
                            </label>

                            {!alterado && <p className="painel-ajuda">Altere o texto para publicar uma nova versão.</p>}

                            <div className="painel-acoes">
                                <button type="button" className="painel-botao" onClick={handlePublicar} disabled={!podePublicar}>
                                    {publicando ? 'Publicando...' : `Publicar versão ${novaVersao}`}
                                </button>
                                {alterado && (
                                    <button type="button" className="painel-botao-secundario" disabled={publicando}
                                        onClick={() => { setTexto(textoVigente); setPrevia(false) }}>
                                        Descartar alterações
                                    </button>
                                )}
                            </div>
                        </section>

                        <section className="painel-card">
                            <h2>Histórico de versões</h2>
                            {versoes.length === 0 ? (
                                <p className="painel-ajuda">
                                    Nenhuma versão foi publicada pelo portal ainda. Vale o texto original do sistema
                                    (versão {vigente.versao}).
                                </p>
                            ) : (
                                <div className="painel-tabela-wrapper">
                                    <table className="painel-tabela">
                                        <thead>
                                            <tr><th>Versão</th><th>Publicada em</th><th>Por</th><th>O que mudou</th></tr>
                                        </thead>
                                        <tbody>
                                            {versoes.map((v) => (
                                                <tr key={v.versao}>
                                                    <td>{v.versao}</td>
                                                    <td>{v.publicado_em ? dataHora(v.publicado_em) : '-'}</td>
                                                    <td>{v.publicado_por ?? '-'}</td>
                                                    <td>{v.resumo}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </section>
                    </>
                )}
            </main>
            <RodapeLegal />
        </div>
    )
}
