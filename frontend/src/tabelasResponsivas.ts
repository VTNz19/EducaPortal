/**
 * No celular (RNF13), cada linha de tabela vira um cartão, com o nome da coluna ao lado de cada valor.
 *
 * O CSS (celular.css) mostra o nome a partir do atributo data-rotulo, que este módulo copia do cabeçalho
 * para cada célula. Vale para todas as tabelas com três colunas ou mais, inclusive as dos documentos
 * de privacidade, que vêm de Markdown e não têm como receber o atributo no próprio JSX.
 */
const MINIMO_DE_COLUNAS = 3

function rotular(tabela: HTMLTableElement) {
    const titulos = [...tabela.querySelectorAll('thead th')].map((th) => th.textContent?.trim() ?? '')
    if (titulos.length < MINIMO_DE_COLUNAS) {
        tabela.classList.remove('tabela-cartoes')
        return
    }
    tabela.classList.add('tabela-cartoes')
    for (const linha of tabela.querySelectorAll('tbody tr')) {
        let coluna = 0
        for (const celula of (linha as HTMLTableRowElement).cells) {
            const rotulo = titulos[coluna] ?? ''
            if (celula.getAttribute('data-rotulo') !== rotulo) celula.setAttribute('data-rotulo', rotulo)
            coluna += celula.colSpan || 1
        }
    }
}

function rotularTudo(raiz: ParentNode) {
    raiz.querySelectorAll('table').forEach((tabela) => rotular(tabela))
}

export function ativarTabelasResponsivas() {
    rotularTudo(document)
    let agendado = false
    new MutationObserver(() => {
        if (agendado) return
        agendado = true
        requestAnimationFrame(() => {
            agendado = false
            rotularTudo(document)
        })
    }).observe(document.body, { childList: true, subtree: true, characterData: true })
}
