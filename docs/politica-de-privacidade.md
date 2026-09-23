# Política de Privacidade — EducaPortal

Última atualização: 22 de setembro de 2026

## 1. Introdução

Esta Política de Privacidade descreve como o EducaPortal coleta, usa,
armazena e protege os dados pessoais de seus usuários, em conformidade com a
Lei Geral de Proteção de Dados (Lei nº 13.709/2018 — LGPD).

## 2. Quem é o controlador dos dados

O controlador dos dados pessoais tratados no EducaPortal é a instituição de
ensino que opera a plataforma, representada administrativamente pela
Secretaria (perfil Administrador). Dúvidas ou solicitações relacionadas a
dados pessoais podem ser enviadas para o contato informado na Seção 10 desta
Política.

## 3. Quais dados pessoais coletamos

- **Dados de identificação:** nome completo, nome de usuário e e-mail;
- **Dados de perfil:** papel de acesso (Administrador, Professor ou
  Aluno/Responsável);
- **Dados acadêmicos:** notas, faltas e avisos publicados ou visualizados;
- **Dados de acesso e segurança:** data/hora de login, tentativas de login
  (sucesso ou falha) e endereço IP de origem, mantidos em log de auditoria;
- **Dados de menores de idade:** quando o titular dos dados é uma criança ou
  adolescente, o tratamento é realizado no melhor interesse do titular, nos
  termos do Art. 14 da LGPD, com a participação e o consentimento de um
  responsável legal.

## 4. Finalidade do tratamento

Os dados pessoais coletados são utilizados exclusivamente para:

- Autenticar o acesso dos usuários à plataforma (login, emissão e renovação
  de tokens de sessão);
- Viabilizar a comunicação escolar (mural de avisos, notas e faltas);
- Garantir a segurança do sistema, por meio do registro de logs de
  auditoria;
- Permitir a recuperação de senha, via envio de e-mail transacional.

Não realizamos tratamento de dados pessoais para fins de publicidade ou
venda a terceiros.

## 5. Quem tem acesso a cada dado

| Dado | Quem acessa |
|---|---|
| Nome, e-mail, papel | Administrador; o próprio titular |
| Notas e faltas de um aluno | Administrador; Professores das turmas do aluno; o próprio aluno/responsável |
| Avisos publicados | Todos os usuários autenticados (leitura); autor e Administrador (gestão) |
| Log de auditoria (ações, IP) | Somente Administradores, com acesso restrito e somente leitura |

## 6. Compartilhamento com terceiros

Para o envio de e-mails transacionais de recuperação de senha, o EducaPortal
utiliza o serviço externo **Resend** (ver [docs/integracao-api-externa.md](integracao-api-externa.md)).
Nessa operação, é compartilhado apenas o endereço de e-mail e o conteúdo da
mensagem enviada — nenhum outro dado pessoal é transmitido a esse ou a
qualquer outro serviço externo.

## 7. Direitos do titular (Art. 18 da LGPD)

O titular dos dados (ou seu responsável legal, quando aplicável) tem direito
a, mediante solicitação:

- Confirmação da existência de tratamento de seus dados;
- Acesso aos dados pessoais armazenados;
- Correção de dados incompletos, inexatos ou desatualizados;
- Anonimização, bloqueio ou eliminação de dados desnecessários ou tratados
  em desconformidade com a LGPD;
- Portabilidade dos dados a outro fornecedor de serviço;
- Eliminação dos dados pessoais tratados com consentimento do titular;
- Informação sobre as entidades com as quais o controlador compartilhou
  dados;
- Revogação do consentimento, quando aplicável.

Solicitações podem ser feitas pelo contato indicado na Seção 10.

## 8. Tempo de retenção

- **Dados cadastrais e acadêmicos:** mantidos durante todo o período em que
  o usuário estiver vinculado à instituição de ensino;
- **Logs de auditoria:** mantidos pelo prazo necessário para fins de
  segurança e auditoria, podendo ser conservados mesmo após o encerramento
  da conta, conforme necessidade legítima da instituição;
- **Tokens de redefinição de senha:** expiram em 1 hora e são descartados
  (marcados como usados) após a primeira utilização ou expiração.

Encerrado o vínculo do usuário com a instituição, os dados pessoais são
eliminados ou anonimizados, ressalvadas as hipóteses legais de retenção
(Art. 16 da LGPD).

## 9. Segurança dos dados

- Senhas nunca são armazenadas em texto puro: utilizamos o algoritmo de
  hashing padrão do Django (PBKDF2);
- A autenticação é feita por tokens JWT de curta duração (access token de
  30 minutos), reduzindo a janela de exposição em caso de vazamento;
- O acesso a funcionalidades administrativas e de gestão é restrito por
  perfil de usuário (controle de permissões por papel);
- Toda ação sensível (login, criação/edição/exclusão de avisos, redefinição
  de senha) é registrada em log de auditoria.

## 10. Contato do controlador

Para exercer seus direitos como titular de dados ou esclarecer dúvidas sobre
esta Política, entre em contato com a Secretaria (Administrador) da
instituição de ensino responsável pelo seu acesso ao EducaPortal.

## 11. Alterações nesta Política

Esta Política de Privacidade pode ser atualizada para refletir mudanças
legais, técnicas ou operacionais. A versão vigente estará sempre disponível
dentro da própria plataforma.
