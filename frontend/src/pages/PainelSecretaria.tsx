import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { criarUsuario, listarPorPerfil, listarUsuarios, NOMES_PAPEIS } from '../api/usuarios'
import type { FiltrosUsuarios, NovoUsuario, UsuarioResumo } from '../api/usuarios'
import { listarAnosLetivos, listarTurmas } from '../api/academico'
import type { AnoLetivo, Turma } from '../api/academico'
import { mensagemDeErro } from '../api/erros'
import { TopoPortal } from '../components/TopoPortal'
import { RodapeLegal } from '../components/RodapeLegal'
import './MuralAvisos.css'
import './PainelSecretaria.css'


const FORM_VAZIO: NovoUsuario = { first_name: '', last_name: '', email: '', role: 'aluno', turma: null, responsaveis: [] }
const FILTROS_VAZIOS: FiltrosUsuarios = { busca: '', role: '', turma: '', ativo: '' }

export function PainelSecretaria() {
    const [usuarios, setUsuarios] = useState<UsuarioResumo[]>([])
    const [total, setTotal] = useState(0)
    const [carregando, setCarregando] = useState(true)
    const [filtros, setFiltros] = useState<FiltrosUsuarios>(FILTROS_VAZIOS)

    const [anoAtual, setAnoAtual] = useState<AnoLetivo | null>(null)
    const [turmas, setTurmas] = useState<Turma[]>([])
    const [responsaveis, setResponsaveis] = useState<UsuarioResumo[]>([])
    const [buscaResponsavel, setBuscaResponsavel] = useState('')

    const [form, setForm] = useState<NovoUsuario>(FORM_VAZIO)
    const [enviando, setEnviando] = useState(false)
    const [erro, setErro] = useState('')
    const [mensagem, setMensagem] = useState('')

    async function carregarUsuarios(f: FiltrosUsuarios = filtros) {
        setCarregando(true)
        const pagina = await listarUsuarios(f)
        setUsuarios(pagina.usuarios)
        setTotal(pagina.total)
        setCarregando(false)
    }

    async function carregarApoio() {
        const anos = await listarAnosLetivos()
        const atual = anos.find((a) => a.ativo) ?? null
        setAnoAtual(atual)
        setTurmas(atual ? await listarTurmas(atual.id) : [])
        setResponsaveis(await listarPorPerfil('responsavel'))
    }

    useEffect(() => {
        carregarUsuarios(FILTROS_VAZIOS)
        carregarApoio()
    }, [])

    function alternarResponsavel(id: number) {
        const atuais = form.responsaveis ?? []
        setForm({ ...form, responsaveis: atuais.includes(id) ? atuais.filter((r) => r !== id) : [...atuais, id] })
    }

    async function handleSubmit(event: FormEvent) {
        event.preventDefault()
        setErro('')
        setMensagem('')
        setEnviando(true)
        try {
            const dados: NovoUsuario = { first_name: form.first_name, last_name: form.last_name, email: form.email, role: form.role }
            if (form.role === 'aluno') {
                dados.turma = form.turma
                dados.responsaveis = form.responsaveis
            }
            const criado = await criarUsuario(dados)
            setMensagem(
                criado.email_enviado
                    ? `Conta de ${criado.nome} criada. Enviamos um e-mail para ${criado.email} definir a senha.`
                    : `Conta de ${criado.nome} criada, mas o e-mail não pôde ser enviado. A pessoa pode usar "Primeiro acesso" na tela de login.`
            )
            setForm({ ...FORM_VAZIO, role: form.role, turma: form.turma })
            setBuscaResponsavel('')
            carregarUsuarios()
            if (form.role === 'responsavel') setResponsaveis(await listarPorPerfil('responsavel'))
        } catch (error) {
            setErro(mensagemDeErro(error, 'Não foi possível criar a conta. Verifique os campos e tente novamente.'))
        } finally {
            setEnviando(false)
        }
    }

    function aplicarFiltros(event: FormEvent) {
        event.preventDefault()
        carregarUsuarios()
    }

    function limparFiltros() {
        setFiltros(FILTROS_VAZIOS)
        carregarUsuarios(FILTROS_VAZIOS)
    }

    const responsaveisFiltrados = responsaveis.filter((r) =>
        `${r.nome} ${r.email}`.toLowerCase().includes(buscaResponsavel.toLowerCase()))

    return (
        <div className="mural-page">
            <TopoPortal />

            <main className="painel-conteudo">
                <h1>Painel da Secretaria</h1>

                <section className="painel-card">
                    <h2>Nova conta</h2>
                    <p className="painel-ajuda">
                        A pessoa recebe um e-mail para criar a própria senha. A secretaria não define nem vê senhas.
                        Cadastre primeiro o responsável: no cadastro do aluno, é preciso escolher a turma e ao menos um responsável.
                    </p>

                    <form onSubmit={handleSubmit}>
                        <div className="painel-form">
                            <div className="painel-campo">
                                <label htmlFor="role">Perfil</label>
                                <select
                                    id="role"
                                    value={form.role}
                                    onChange={(e) => setForm({ ...form, role: e.target.value as NovoUsuario['role'] })}
                                >
                                    <option value="aluno">Aluno</option>
                                    <option value="responsavel">Responsável</option>
                                    <option value="professor">Professor</option>
                                </select>
                            </div>
                            <div className="painel-campo">
                                <label htmlFor="first_name">Nome</label>
                                <input id="first_name" value={form.first_name} required
                                    onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
                            </div>
                            <div className="painel-campo">
                                <label htmlFor="last_name">Sobrenome</label>
                                <input id="last_name" value={form.last_name} required
                                    onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
                            </div>
                            <div className="painel-campo">
                                <label htmlFor="email">E-mail</label>
                                <input id="email" type="email" value={form.email} required
                                    onChange={(e) => setForm({ ...form, email: e.target.value })} />
                            </div>

                            {form.role === 'aluno' && (
                                <div className="painel-campo">
                                    <label htmlFor="turma">Turma ({anoAtual ? anoAtual.ano : 'sem ano letivo ativo'})</label>
                                    <select id="turma" value={form.turma ?? ''} required
                                        onChange={(e) => setForm({ ...form, turma: e.target.value ? Number(e.target.value) : null })}>
                                        <option value="">Selecione a turma</option>
                                        {turmas.map((t) => (
                                            <option key={t.id} value={t.id}>{t.nome} – {t.turno_nome}</option>
                                        ))}
                                    </select>
                                </div>
                            )}
                        </div>

                        {form.role === 'aluno' && turmas.length === 0 && (
                            <p className="painel-aviso">
                                Ainda não há turmas no ano letivo atual.{' '}
                                <Link to="/secretaria/estrutura" className="painel-link">Cadastre uma turma</Link> antes de cadastrar alunos.
                            </p>
                        )}

                        {form.role === 'aluno' && responsaveis.length === 0 && (
                            <p className="painel-aviso">
                                Ainda não há responsáveis cadastrados. Cadastre um responsável antes de cadastrar alunos.
                            </p>
                        )}

                        {form.role === 'aluno' && responsaveis.length > 0 && (
                            <div className="painel-campo painel-selecao">
                                <label htmlFor="busca-responsavel">Responsáveis pelo aluno ({form.responsaveis?.length ?? 0} selecionados)</label>
                                <input id="busca-responsavel" placeholder="Buscar por nome ou e-mail" value={buscaResponsavel}
                                    onChange={(e) => setBuscaResponsavel(e.target.value)} />
                                <div className="painel-lista-selecao">
                                    {responsaveisFiltrados.length === 0 && <p className="painel-ajuda">Nenhum responsável encontrado.</p>}
                                    {responsaveisFiltrados.map((r) => (
                                        <label key={r.id} className="painel-opcao">
                                            <input type="checkbox" checked={form.responsaveis?.includes(r.id) ?? false}
                                                onChange={() => alternarResponsavel(r.id)} />
                                            {r.nome} <span className="painel-ajuda-inline">{r.email}</span>
                                        </label>
                                    ))}
                                </div>
                            </div>
                        )}

                        <button type="submit" className="painel-botao painel-botao-espaco" disabled={enviando}>
                            {enviando ? 'Criando...' : 'Criar conta'}
                        </button>
                    </form>

                    {erro && <p className="painel-erro" role="alert">{erro}</p>}
                    {mensagem && <p className="painel-sucesso" role="status">{mensagem}</p>}
                </section>

                <section className="painel-card">
                    <h2>Contas cadastradas</h2>

                    <form className="painel-form painel-filtros" onSubmit={aplicarFiltros}>
                        <div className="painel-campo">
                            <label htmlFor="f-busca">Nome ou e-mail</label>
                            <input id="f-busca" value={filtros.busca}
                                onChange={(e) => setFiltros({ ...filtros, busca: e.target.value })} />
                        </div>
                        <div className="painel-campo">
                            <label htmlFor="f-role">Perfil</label>
                            <select id="f-role" value={filtros.role}
                                onChange={(e) => setFiltros({ ...filtros, role: e.target.value })}>
                                <option value="">Todos</option>
                                {Object.entries(NOMES_PAPEIS).map(([valor, nome]) => (
                                    <option key={valor} value={valor}>{nome}</option>
                                ))}
                            </select>
                        </div>
                        <div className="painel-campo">
                            <label htmlFor="f-turma">Turma</label>
                            <select id="f-turma" value={filtros.turma}
                                onChange={(e) => setFiltros({ ...filtros, turma: e.target.value ? Number(e.target.value) : '' })}>
                                <option value="">Todas</option>
                                {turmas.map((t) => <option key={t.id} value={t.id}>{t.nome}</option>)}
                            </select>
                        </div>
                        <div className="painel-campo">
                            <label htmlFor="f-ativo">Situação</label>
                            <select id="f-ativo" value={filtros.ativo}
                                onChange={(e) => setFiltros({ ...filtros, ativo: e.target.value as FiltrosUsuarios['ativo'] })}>
                                <option value="">Todas</option>
                                <option value="true">Ativa</option>
                                <option value="false">Inativa</option>
                            </select>
                        </div>
                        <div className="painel-acoes">
                            <button type="submit" className="painel-botao">Filtrar</button>
                            <button type="button" className="painel-botao-secundario" onClick={limparFiltros}>Limpar</button>
                        </div>
                    </form>

                    {carregando ? (
                        <p>Carregando...</p>
                    ) : usuarios.length === 0 ? (
                        <p>Nenhuma conta encontrada com esses filtros.</p>
                    ) : (
                        <>
                            <p className="painel-ajuda">
                                {total > usuarios.length
                                    ? `Mostrando ${usuarios.length} de ${total} contas. Use os filtros para encontrar uma conta específica.`
                                    : `${total} conta(s) encontrada(s).`}
                            </p>
                            <div className="painel-tabela-wrapper">
                                <table className="painel-tabela">
                                    <thead>
                                        <tr>
                                            <th>Nome</th>
                                            <th>E-mail</th>
                                            <th>Perfil</th>
                                            <th>Turma</th>
                                            <th>Situação</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {usuarios.map((u) => (
                                            <tr key={u.id}>
                                                <td>
                                                    <Link to={`/secretaria/usuarios/${u.id}`} className="painel-link">{u.nome}</Link>
                                                </td>
                                                <td>{u.email}</td>
                                                <td>{NOMES_PAPEIS[u.role] ?? u.role}</td>
                                                <td>{u.turma ?? '-'}</td>
                                                <td>{u.is_active ? 'Ativa' : 'Inativa'}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </>
                    )}
                </section>
            </main>
            <RodapeLegal />
        </div>
    )
}
