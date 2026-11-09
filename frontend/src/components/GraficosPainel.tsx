import {
    Bar, BarChart, CartesianGrid, Cell, LabelList, Legend, Line, LineChart, ReferenceLine,
    ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { formatar } from '../api/painel'
import type { PontoEvolucao } from '../api/painel'

const COR_SERIE_1 = '#2a78d6'
const COR_SERIE_2 = '#eb6834'
const COR_CRITICO = '#d03b3b'
const COR_GRADE = '#e1e0d9'
const COR_LINHA_BASE = '#c3c2b7'
const COR_TEXTO = '#52514e'

const TEXTO_EIXO = { fontSize: 12, fill: COR_TEXTO }
const CONTORNO_DO_ROTULO = { paintOrder: 'stroke', stroke: '#fff', strokeWidth: 4 }
const ALTURA_POR_BARRA = 44
const ALTURA_DAS_MARGENS = 56

interface ItemBarra {
    nome: string
    valor: number | null
}

interface BarrasComMinimoProps {
    titulo: string
    itens: ItemBarra[]
    minimo: number
    rotuloMinimo: string
    marcas: number[]
    sufixo?: string
}

export function BarrasComMinimo({ titulo, itens, minimo, rotuloMinimo, marcas, sufixo = '' }: BarrasComMinimoProps) {
    const comValor = itens.filter((i) => i.valor !== null)
    const descricao = comValor.map((i) => `${i.nome}: ${formatar(i.valor, sufixo)}`).join('; ')
    return (
        <figure className="grafico">
            <figcaption>{titulo}</figcaption>
            {comValor.length === 0 ? (
                <p className="painel-ajuda">Ainda não há dados para este gráfico.</p>
            ) : (
                <>
                    <div role="img" aria-label={`${titulo}. ${descricao}`}>
                        <ResponsiveContainer width="100%" height={comValor.length * ALTURA_POR_BARRA + ALTURA_DAS_MARGENS}>
                            <BarChart data={comValor} layout="vertical" margin={{ top: 18, right: 44, bottom: 0, left: 8 }}>
                                <CartesianGrid horizontal={false} stroke={COR_GRADE} />
                                <XAxis type="number" domain={[0, marcas[marcas.length - 1]]} ticks={marcas} tick={TEXTO_EIXO} stroke={COR_LINHA_BASE} tickLine={false} />
                                <YAxis type="category" dataKey="nome" width={150} tick={TEXTO_EIXO} stroke={COR_LINHA_BASE} tickLine={false} />
                                <Tooltip
                                    cursor={{ fill: 'rgba(11, 11, 11, 0.04)' }}
                                    formatter={(valor) => [formatar(Number(valor), sufixo), titulo]}
                                />
                                <Bar dataKey="valor" barSize={20} radius={[0, 4, 4, 0]} isAnimationActive={false}>
                                    {comValor.map((item) => (
                                        <Cell key={item.nome} fill={(item.valor ?? 0) < minimo ? COR_CRITICO : COR_SERIE_1} />
                                    ))}
                                    <LabelList
                                        dataKey="valor"
                                        position="right"
                                        fontSize={12}
                                        fill={COR_TEXTO}
                                        style={CONTORNO_DO_ROTULO}
                                        formatter={(valor) => formatar(Number(valor), sufixo)}
                                    />
                                </Bar>
                                <ReferenceLine
                                    x={minimo}
                                    stroke={COR_TEXTO}
                                    label={{ value: rotuloMinimo, position: 'top', fontSize: 12, fill: COR_TEXTO }}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <p className="grafico-legenda">
                        <span className="grafico-chave grafico-chave-ok" /> No mínimo ou acima
                        <span className="grafico-chave grafico-chave-abaixo" /> Abaixo do mínimo
                    </p>
                </>
            )}
        </figure>
    )
}

export function EvolucaoBimestral({ titulo, pontos }: { titulo: string; pontos: PontoEvolucao[] }) {
    const dados = pontos.map((p) => ({ nome: `${p.bimestre}º bim.`, media: p.media }))
    const descricao = dados.map((d) => `${d.nome}: ${formatar(d.media)}`).join('; ')
    return (
        <figure className="grafico">
            <figcaption>{titulo}</figcaption>
            <div role="img" aria-label={`${titulo}. ${descricao}`}>
                <ResponsiveContainer width="100%" height={240}>
                    <LineChart data={dados} margin={{ top: 18, right: 44, bottom: 0, left: -16 }}>
                        <CartesianGrid vertical={false} stroke={COR_GRADE} />
                        <XAxis dataKey="nome" tick={TEXTO_EIXO} stroke={COR_LINHA_BASE} tickLine={false} />
                        <YAxis domain={[0, 10]} ticks={[0, 2, 4, 6, 8, 10]} tick={TEXTO_EIXO} stroke={COR_LINHA_BASE} tickLine={false} />
                        <Tooltip formatter={(valor) => [formatar(Number(valor)), 'Média']} />
                        <ReferenceLine
                            y={6}
                            stroke={COR_TEXTO}
                            label={{ value: 'Mínimo 6,0', position: 'insideTopRight', fontSize: 12, fill: COR_TEXTO }}
                        />
                        <Line
                            type="linear"
                            dataKey="media"
                            stroke={COR_SERIE_1}
                            strokeWidth={2}
                            dot={{ r: 5, fill: COR_SERIE_1, stroke: '#fff', strokeWidth: 2 }}
                            activeDot={{ r: 6 }}
                            isAnimationActive={false}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </figure>
    )
}

interface ItemPercentual {
    nome: string
    abaixoMedia: number | null
    abaixoFrequencia: number | null
}

export function PercentuaisPorTurma({ itens }: { itens: ItemPercentual[] }) {
    const titulo = 'Alunos abaixo do mínimo por turma (%)'
    const descricao = itens
        .map((i) => `${i.nome}: ${formatar(i.abaixoMedia, '%')} na média e ${formatar(i.abaixoFrequencia, '%')} na frequência`)
        .join('; ')
    return (
        <figure className="grafico">
            <figcaption>{titulo}</figcaption>
            <div role="img" aria-label={`${titulo}. ${descricao}`}>
                <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={itens} barGap={2} margin={{ top: 18, right: 16, bottom: 0, left: -16 }}>
                        <CartesianGrid vertical={false} stroke={COR_GRADE} />
                        <XAxis dataKey="nome" tick={TEXTO_EIXO} stroke={COR_LINHA_BASE} tickLine={false} />
                        <YAxis domain={[0, 100]} tick={TEXTO_EIXO} stroke={COR_LINHA_BASE} tickLine={false} />
                        <Tooltip
                            cursor={{ fill: 'rgba(11, 11, 11, 0.04)' }}
                            formatter={(valor, nome) => [formatar(Number(valor), '%'), nome]}
                        />
                        <Legend
                            itemSorter={null}
                            wrapperStyle={{ fontSize: 13 }}
                            formatter={(nome) => <span style={{ color: COR_TEXTO }}>{nome}</span>}
                        />
                        <Bar dataKey="abaixoMedia" name="Abaixo da média" fill={COR_SERIE_1} maxBarSize={24} radius={[4, 4, 0, 0]} isAnimationActive={false} />
                        <Bar dataKey="abaixoFrequencia" name="Abaixo da frequência" fill={COR_SERIE_2} maxBarSize={24} radius={[4, 4, 0, 0]} isAnimationActive={false} />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </figure>
    )
}
