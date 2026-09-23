import { Link } from 'react-router-dom'
import './LegalPage.css'

export function PoliticaDePrivacidade() {
    return (
        <div className="legal-page">
            <Link to="/login" className="legal-voltar">&larr; Voltar para o login</Link>

            <h1>Política de Privacidade — EducaPortal</h1>
            <p className="legal-atualizado">Última atualização: 22 de setembro de 2026</p>

            <h2>1. Introdução</h2>
            <p>
                Esta Política de Privacidade descreve como o EducaPortal coleta,
                usa, armazena e protege os dados pessoais de seus usuários, em
                conformidade com a Lei Geral de Proteção de Dados (Lei nº
                13.709/2018 — LGPD).
            </p>

            <h2>2. Quem é o controlador dos dados</h2>
            <p>
                O controlador dos dados pessoais tratados no EducaPortal é a
                instituição de ensino que opera a plataforma, representada
                administrativamente pela Secretaria (perfil Administrador). Dúvidas
                ou solicitações relacionadas a dados pessoais podem ser enviadas
                para o contato informado na Seção 10 desta Política.
            </p>

            <h2>3. Quais dados pessoais coletamos</h2>
            <ul>
                <li><strong>Dados de identificação:</strong> nome completo, nome de usuário e e-mail;</li>
                <li><strong>Dados de perfil:</strong> papel de acesso (Administrador, Professor ou Aluno/Responsável);</li>
                <li><strong>Dados acadêmicos:</strong> notas, faltas e avisos publicados ou visualizados;</li>
                <li><strong>Dados de acesso e segurança:</strong> data/hora de login, tentativas de login (sucesso ou falha) e endereço IP de origem, mantidos em log de auditoria;</li>
                <li><strong>Dados de menores de idade:</strong> quando o titular dos dados é uma criança ou adolescente, o tratamento é realizado no melhor interesse do titular, nos termos do Art. 14 da LGPD, com a participação e o consentimento de um responsável legal.</li>
            </ul>

            <h2>4. Finalidade do tratamento</h2>
            <p>Os dados pessoais coletados são utilizados exclusivamente para:</p>
            <ul>
                <li>Autenticar o acesso dos usuários à plataforma (login, emissão e renovação de tokens de sessão);</li>
                <li>Viabilizar a comunicação escolar (mural de avisos, notas e faltas);</li>
                <li>Garantir a segurança do sistema, por meio do registro de logs de auditoria;</li>
                <li>Permitir a recuperação de senha, via envio de e-mail transacional.</li>
            </ul>
            <p>Não realizamos tratamento de dados pessoais para fins de publicidade ou venda a terceiros.</p>

            <h2>5. Quem tem acesso a cada dado</h2>
            <table>
                <thead>
                    <tr><th>Dado</th><th>Quem acessa</th></tr>
                </thead>
                <tbody>
                    <tr><td>Nome, e-mail, papel</td><td>Administrador; o próprio titular</td></tr>
                    <tr><td>Notas e faltas de um aluno</td><td>Administrador; Professores das turmas do aluno; o próprio aluno/responsável</td></tr>
                    <tr><td>Avisos publicados</td><td>Todos os usuários autenticados (leitura); autor e Administrador (gestão)</td></tr>
                    <tr><td>Log de auditoria (ações, IP)</td><td>Somente Administradores, com acesso restrito e somente leitura</td></tr>
                </tbody>
            </table>

            <h2>6. Compartilhamento com terceiros</h2>
            <p>
                Para o envio de e-mails transacionais de recuperação de senha, o
                EducaPortal utiliza o serviço externo <strong>Resend</strong>. Nessa
                operação, é compartilhado apenas o endereço de e-mail e o conteúdo
                da mensagem enviada — nenhum outro dado pessoal é transmitido a
                esse ou a qualquer outro serviço externo.
            </p>

            <h2>7. Direitos do titular (Art. 18 da LGPD)</h2>
            <p>
                O titular dos dados (ou seu responsável legal, quando aplicável) tem
                direito a, mediante solicitação:
            </p>
            <ul>
                <li>Confirmação da existência de tratamento de seus dados;</li>
                <li>Acesso aos dados pessoais armazenados;</li>
                <li>Correção de dados incompletos, inexatos ou desatualizados;</li>
                <li>Anonimização, bloqueio ou eliminação de dados desnecessários ou tratados em desconformidade com a LGPD;</li>
                <li>Portabilidade dos dados a outro fornecedor de serviço;</li>
                <li>Eliminação dos dados pessoais tratados com consentimento do titular;</li>
                <li>Informação sobre as entidades com as quais o controlador compartilhou dados;</li>
                <li>Revogação do consentimento, quando aplicável.</li>
            </ul>
            <p>Solicitações podem ser feitas pelo contato indicado na Seção 10.</p>

            <h2>8. Tempo de retenção</h2>
            <ul>
                <li><strong>Dados cadastrais e acadêmicos:</strong> mantidos durante todo o período em que o usuário estiver vinculado à instituição de ensino;</li>
                <li><strong>Logs de auditoria:</strong> mantidos pelo prazo necessário para fins de segurança e auditoria, podendo ser conservados mesmo após o encerramento da conta, conforme necessidade legítima da instituição;</li>
                <li><strong>Tokens de redefinição de senha:</strong> expiram em 1 hora e são descartados (marcados como usados) após a primeira utilização ou expiração.</li>
            </ul>
            <p>
                Encerrado o vínculo do usuário com a instituição, os dados pessoais
                são eliminados ou anonimizados, ressalvadas as hipóteses legais de
                retenção (Art. 16 da LGPD).
            </p>

            <h2>9. Segurança dos dados</h2>
            <ul>
                <li>Senhas nunca são armazenadas em texto puro: utilizamos o algoritmo de hashing padrão do Django (PBKDF2);</li>
                <li>A autenticação é feita por tokens JWT de curta duração (access token de 30 minutos), reduzindo a janela de exposição em caso de vazamento;</li>
                <li>O acesso a funcionalidades administrativas e de gestão é restrito por perfil de usuário;</li>
                <li>Toda ação sensível (login, criação/edição/exclusão de avisos, redefinição de senha) é registrada em log de auditoria.</li>
            </ul>

            <h2>10. Contato do controlador</h2>
            <p>
                Para exercer seus direitos como titular de dados ou esclarecer
                dúvidas sobre esta Política, entre em contato com a Secretaria
                (Administrador) da instituição de ensino responsável pelo seu acesso
                ao EducaPortal.
            </p>

            <h2>11. Alterações nesta Política</h2>
            <p>
                Esta Política de Privacidade pode ser atualizada para refletir
                mudanças legais, técnicas ou operacionais. A versão vigente estará
                sempre disponível dentro da própria plataforma.
            </p>
        </div>
    )
}
