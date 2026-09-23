import { Link } from 'react-router-dom'
import './LegalPage.css'

export function TermoDeUso() {
    return (
        <div className="legal-page">
            <Link to="/login" className="legal-voltar">&larr; Voltar para o login</Link>

            <h1>Termo de Uso — EducaPortal</h1>
            <p className="legal-atualizado">Última atualização: 22 de setembro de 2026</p>

            <h2>1. Sobre o EducaPortal</h2>
            <p>
                O EducaPortal é uma plataforma web voltada à gestão escolar, que
                centraliza avisos, notas, faltas e a comunicação entre a escola, o
                corpo docente e os alunos/responsáveis. Este Termo de Uso regula o
                acesso e a utilização do sistema por todos os seus usuários.
            </p>
            <p>
                Ao criar uma conta ou utilizar o EducaPortal, você concorda com as
                condições descritas neste documento e com a nossa{' '}
                <Link to="/politica-de-privacidade">Política de Privacidade</Link>.
            </p>

            <h2>2. Quem pode usar o sistema</h2>
            <p>
                O acesso ao EducaPortal é restrito e feito por meio de login e senha
                individuais, concedidos pela instituição de ensino. Existem três
                perfis de acesso:
            </p>
            <ul>
                <li><strong>Administrador (Secretaria):</strong> responsável pela gestão geral do sistema, cadastro de usuários e supervisão do conteúdo publicado.</li>
                <li><strong>Professor:</strong> responsável por publicar avisos, lançar notas e registrar faltas das turmas sob sua responsabilidade.</li>
                <li><strong>Aluno/Responsável:</strong> utiliza o sistema para acompanhar avisos, notas e faltas. Quando o aluno é menor de idade, o cadastro e o acompanhamento da conta são de responsabilidade de seu responsável legal.</li>
            </ul>
            <p>
                Não é permitido compartilhar credenciais de acesso com terceiros,
                nem utilizar conta de outra pessoa.
            </p>

            <h2>3. Responsabilidades de cada papel</h2>
            <h3>Administrador</h3>
            <ul>
                <li>Manter os dados cadastrais da instituição e dos usuários atualizados;</li>
                <li>Conceder e revogar acessos de forma adequada;</li>
                <li>Zelar pelo cumprimento deste Termo e da legislação aplicável, incluindo a LGPD.</li>
            </ul>
            <h3>Professor</h3>
            <ul>
                <li>Publicar avisos, notas e faltas de forma correta e no prazo devido;</li>
                <li>Utilizar linguagem adequada e profissional em toda comunicação feita pela plataforma;</li>
                <li>Não divulgar informações de alunos fora dos canais e finalidades previstos neste Termo.</li>
            </ul>
            <h3>Aluno/Responsável</h3>
            <ul>
                <li>Manter seus dados cadastrais atualizados;</li>
                <li>Acompanhar avisos, notas e faltas publicados pela escola;</li>
                <li>Zelar pela confidencialidade da própria senha de acesso.</li>
            </ul>

            <h2>4. Regras de conduta ao publicar avisos e tarefas</h2>
            <p>
                Usuários com permissão para publicar avisos (Administradores e
                Professores) devem observar as seguintes regras:
            </p>
            <ul>
                <li>O conteúdo publicado deve ser verdadeiro, claro e relacionado à vida escolar;</li>
                <li>É proibida a publicação de conteúdo ofensivo, discriminatório, difamatório ou que exponha indevidamente dados pessoais de alunos ou de terceiros;</li>
                <li>Avisos fixados devem ser usados apenas para comunicados de caráter urgente ou de alta relevância;</li>
                <li>Toda publicação, edição e exclusão de avisos é registrada em log de auditoria, identificando o autor, a data/hora e o endereço IP de origem.</li>
            </ul>

            <h2>5. Uso de dados de menores de idade</h2>
            <p>
                Grande parte dos usuários do EducaPortal são crianças e
                adolescentes. O tratamento de dados desses titulares observa o
                disposto no Art. 14 da LGPD, sendo realizado no melhor interesse do
                titular e com a participação de um responsável legal, conforme
                detalhado na nossa Política de Privacidade.
            </p>

            <h2>6. Suspensão e encerramento de conta</h2>
            <p>
                A instituição de ensino, por meio de um Administrador, pode
                suspender ou encerrar o acesso de um usuário em caso de
                descumprimento deste Termo, uso indevido da plataforma, ou a pedido
                do próprio titular/responsável legal.
            </p>

            <h2>7. Alterações neste Termo</h2>
            <p>
                Este Termo de Uso pode ser atualizado periodicamente para refletir
                mudanças legais, técnicas ou operacionais do EducaPortal. A versão
                vigente estará sempre disponível dentro da própria plataforma.
            </p>

            <h2>8. Contato</h2>
            <p>
                Em caso de dúvidas sobre este Termo de Uso, entre em contato com a
                coordenação/secretaria da instituição de ensino responsável pelo seu
                acesso ao EducaPortal.
            </p>
        </div>
    )
}
