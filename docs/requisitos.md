# Requisitos Funcionais e Não Funcionais — EducaPortal

**Versão:** 3.1 — 8 de novembro de 2026

## 1. Convenções

Cada requisito funcional (RF) segue o modelo de descrição de casos de uso
adotado na orientação do PFC:

- **Sumário:** o que o requisito permite fazer.
- **Ator primário** e **atores secundários.**
- **Pré-condições:** o que precisa ser verdade antes de começar.
- **Fluxo principal:** o caminho mais comum, passo a passo.
- **Fluxo alternativo (n):** caminho que se desvia do principal no passo *n*,
  com passos identificados por letras.
- **Fluxo de exceção (n):** tratamento de um erro ou impedimento ocorrido no
  passo *n*.
- **Pós-condições:** o estado do sistema ao final.

Em seguida vêm as regras de negócio (RN), os critérios de aceite (CA), no
formato "Dado..., quando..., então...", e a situação de implementação.

As regras de negócio têm numeração única no documento (RN01, RN02...), para
que possam ser citadas nos diagramas e nos testes. Os critérios de aceite são
numerados dentro de cada requisito.

O campo **Situação** indica:

- **Implementado:** funciona na versão atual do sistema.
- **Parcial:** parte do requisito funciona; o restante tem data prevista no
  cronograma (seção 1.3).
- **Previsto:** especificado neste documento e com data prevista no
  cronograma (seção 1.3).

### 1.1 Atores

| Ator | Descrição |
|---|---|
| Secretaria | Cadastra turmas, disciplinas e contas, matricula alunos, vincula responsáveis e publica avisos |
| Direção | Possui as permissões da Secretaria e é o super usuário do sistema: é o único perfil que consulta o histórico de atividades e exporta os dados de um titular (RF06 e RF07) |
| Gestor | Termo usado neste documento para "Secretaria ou Direção" |
| Professor | Publica avisos e tarefas e lança notas e faltas das disciplinas atribuídas a ele |
| Aluno | Consulta o mural, as tarefas e as próprias notas, faltas e boletim |
| Responsável | Consulta o mural e as notas, faltas, tarefas e boletim dos alunos vinculados a ele |
| Visitante | Pessoa não autenticada |
| Sistema | Ações executadas automaticamente pelo EducaPortal |
| Serviço de e-mail | Serviço externo Brevo, usado para convites, redefinição de senha e notificações |

### 1.2 Resumo dos requisitos funcionais

| ID | Nome | Ator primário | Situação | Previsão |
|---|---|---|---|---|
| RF01 | Autenticar usuário | Todos os perfis | Implementado | — |
| RF02 | Controlar o acesso por perfil | Sistema | Implementado | — |
| RF03 | Cadastrar usuário | Gestor | Implementado | — |
| RF04 | Definir ou redefinir senha por e-mail | Todos os perfis | Implementado | — |
| RF05 | Aceitar o Termo de Uso e Aceite | Todos os perfis | Implementado | — |
| RF06 | Consultar usuários e histórico de atividades | Gestor; histórico só Direção | Implementado | — |
| RF07 | Exportar os dados de um titular | Direção | Implementado | — |
| RF08 | Publicar aviso no mural | Gestor, Professor | Implementado | — |
| RF09 | Gerenciar aviso publicado | Gestor, Professor | Implementado | — |
| RF10 | Consultar o mural de avisos | Todos os perfis | Implementado | — |
| RF11 | Registrar log de auditoria | Sistema | Implementado | — |
| RF12 | Consultar os documentos de privacidade | Todos, inclusive Visitante | Implementado | — |
| RF13 | Gerenciar ano letivo, turmas e disciplinas | Gestor | Implementado | — |
| RF14 | Alterar matrícula e vínculos de responsáveis | Gestor | Implementado | — |
| RF15 | Lançar notas | Professor | Implementado | — |
| RF16 | Registrar faltas | Professor | Implementado | — |
| RF17 | Calcular médias e frequência | Sistema | Implementado | — |
| RF18 | Emitir boletim em PDF | Aluno, Responsável, Gestor | Implementado | — |
| RF19 | Publicar tarefa com anexos | Professor | Previsto | 30/11/2026 |
| RF20 | Gerenciar o calendário escolar | Gestor | Previsto | 30/11/2026 |
| RF21 | Exibir painel de indicadores | Todos os perfis | Parcial | 30/11/2026 |
| RF22 | Aplicar a retenção e o descarte de dados | Sistema | Previsto | 30/11/2026 |

As notificações por e-mail deixaram de ser um requisito separado. Cada
requisito que gera uma notificação (RF08, RF15, RF16 e RF19) descreve o envio
no próprio fluxo.

### 1.3 Cronograma

| Etapa | Prazo | Requisitos | Situação |
|---|---|---|---|
| 1 – Núcleo acadêmico | 26/10/2026 | RF13 e RF14; cadastro de aluno com turma e responsável (RF03); filtros na lista de contas (RF06); sessão máxima de 8 horas (RF01) | Concluída |
| 2 – Notas e frequência | 09/11/2026 | RF15, RF16 e RF17 | Concluída |
| 3 – Boletim e comunicação | 16/11/2026 | RF18; avisos por turma, período de exibição e notificação por e-mail (RF08 a RF10); tela de edição de aviso (RF09) | Concluída antes do prazo |
| 4 – Complementos e implantação | 30/11/2026 | RF19, RF20, RF21 e RF22; implantação na Vercel e no Railway (RNF04) | Em andamento: RF21 parcial |

As etapas 1 a 3 entregam as funcionalidades principais do sistema: cadastro
acadêmico, notas, faltas, médias, boletim e comunicação automática com alunos
e responsáveis. Em 8 de novembro de 2026, 18 dos 22 requisitos funcionais estão
implementados e o RF21 está parcial.

## 2. Requisitos funcionais

### RF01 – Autenticar usuário

**Sumário:** Permite que usuários cadastrados e ativos entrem no sistema com
e-mail e senha, liberando apenas as funcionalidades do seu perfil, e encerrem
a sessão.

**Ator primário:** Usuário (Secretaria, Direção, Professor, Aluno ou
Responsável).

**Atores secundários:** Não se aplica.

**Pré-condições:** O usuário possui conta ativa e senha definida (RF04).

**Fluxo principal:**

1. O usuário informa e-mail e senha na tela de login.
2. O sistema valida o formato dos campos.
3. O sistema verifica as credenciais.
4. O sistema inicia a sessão, registra `login_sucesso` no log de auditoria e
   direciona o usuário ao mural de avisos.
5. Ao escolher "Sair", o sistema encerra a sessão e retorna à tela de login.

**Fluxo alternativo (4): Termo vigente não aceito**

a) O sistema direciona o usuário à página de aceite do termo (RF05) em vez do
   mural.

**Fluxo de exceção (2): Formato de e-mail inválido**

a) O sistema exibe "E-mail inválido." sem enviar a requisição ao servidor.

**Fluxo de exceção (3): Credenciais inválidas ou conta inativa**

a) O sistema exibe "E-mail ou senha inválidos.".
b) O sistema registra `login_falha` no log de auditoria, com o e-mail
   informado e o endereço IP.
c) O caso de uso retorna ao passo 1.

**Fluxo de exceção (4): Sessão expirada**

a) Ao fim do prazo da RN03, o sistema encerra a sessão e retorna à tela de
   login com a mensagem "Sua sessão expirou. Entre novamente.".

**Pós-condições:** Sessão iniciada e login registrado no log, ou acesso
recusado e tentativa registrada no log.

**Regras de negócio:**

- RN01 – A senha não é armazenada em texto puro, apenas o seu hash.
- RN02 – A mensagem de falha é a mesma para e-mail inexistente, senha
  incorreta e conta inativa, sem revelar qual dado está errado.
- RN03 – A sessão expira após 30 minutos sem uso. Enquanto o usuário estiver
  usando o sistema, ela é renovada automaticamente por até 8 horas; depois
  disso, é necessário um novo login.
- RN04 – Contas inativas não podem se autenticar.

**Critérios de aceite:**

- CA01 – Dado um usuário ativo, quando informar e-mail e senha corretos, então
  o sistema deverá abrir o mural de avisos.
- CA02 – Dado um usuário com senha incorreta, quando tentar entrar, então o
  sistema deverá exibir "E-mail ou senha inválidos." e registrar o evento
  `login_falha`.
- CA03 – Dado um usuário inativo, quando informar as credenciais corretas,
  então o sistema deverá recusar o acesso com a mesma mensagem do CA02.
- CA04 – Dado um usuário autenticado, quando clicar em "Sair", então o sistema
  deverá voltar à tela de login e bloquear as páginas internas.
- CA05 – Dado um e-mail em formato inválido, quando o usuário tentar entrar,
  então o sistema deverá exibir "E-mail inválido." sem enviar a requisição.
- CA06 – Dado um usuário que entrou há mais de 8 horas, quando fizer uma nova
  requisição, então o sistema deverá exigir um novo login.

**Situação:** Implementado.

---

### RF02 – Controlar o acesso por perfil

**Sumário:** Restringe cada funcionalidade aos perfis autorizados, tanto nas
telas quanto na API.

**Ator primário:** Sistema.

**Atores secundários:** Não se aplica.

**Pré-condições:** O usuário está autenticado (RF01).

**Fluxo principal:**

1. O usuário acessa uma página ou faz uma requisição à API.
2. O sistema identifica o perfil do usuário.
3. O sistema verifica se o perfil tem permissão para a operação.
4. O sistema executa a operação.

**Fluxo de exceção (3): Perfil sem permissão**

a) A API responde com o código 403 e a mensagem "Você não tem permissão para
   executar essa ação.".
b) A interface redireciona o usuário ao mural.

**Fluxo de exceção (1): Usuário não autenticado**

a) A API responde com o código 401.
b) A interface redireciona o usuário à tela de login.

**Pós-condições:** Operação executada somente quando o perfil tem permissão.

**Regras de negócio:**

- RN05 – Os perfis são Secretaria, Direção, Professor, Aluno e Responsável.
  Cada conta possui exatamente um perfil.
- RN06 – A verificação de permissão ocorre no back-end. A interface apenas
  oculta o que o perfil não pode usar.
- RN07 – Usuário não autenticado só acessa a página inicial, o login, o
  primeiro acesso, a recuperação de senha e os documentos de privacidade.

**Critérios de aceite:**

- CA01 – Dado um aluno autenticado, quando acessar o endereço do painel da
  secretaria, então o sistema deverá redirecioná-lo ao mural.
- CA02 – Dado um aluno autenticado, quando enviar diretamente à API um pedido
  de criação de aviso, então a API deverá responder com o código 403.
- CA03 – Dado um visitante, quando acessar o endereço do mural, então o
  sistema deverá redirecioná-lo à tela de login.

**Situação:** Implementado.

---

### RF03 – Cadastrar usuário

**Sumário:** Permite ao gestor cadastrar contas de professor, aluno e
responsável. O aluno é matriculado em uma turma e vinculado a pelo menos um
responsável já cadastrado no mesmo ato do cadastro. A pessoa recebe um convite
por e-mail para definir a própria senha.

**Ator primário:** Gestor (Secretaria ou Direção).

**Atores secundários:** Serviço de e-mail.

**Pré-condições:** O gestor está autenticado e aceitou o termo vigente (RF05).
Para cadastrar aluno, existe ao menos uma turma no ano letivo atual (RF13) e
ao menos um responsável já cadastrado.

**Fluxo principal:**

1. O gestor escolhe "Novo usuário" no painel da secretaria.
2. O sistema apresenta um formulário com nome, sobrenome, e-mail e perfil.
3. O gestor preenche os dados e seleciona o perfil Professor.
4. O sistema valida os dados.
5. O sistema cria a conta sem senha e registra `usuario_criado` no log.
6. O sistema envia o e-mail de primeiro acesso com o link de definição de
   senha (RF04).
7. O sistema informa que a conta foi criada e que o convite foi enviado.

**Fluxo alternativo (3): Cadastro de aluno**

a) O gestor seleciona o perfil Aluno.
b) O sistema exibe o ano letivo atual e a lista de turmas desse ano.
c) O gestor seleciona a turma do aluno.
d) O gestor busca por nome ou e-mail e seleciona um ou mais responsáveis já
   cadastrados.
e) O sistema valida os dados e cria, no mesmo ato, a conta, a matrícula na
   turma e os vínculos, registrando `usuario_criado`, `matricula_criada` e
   `vinculo_criado` no log.
f) O caso de uso continua no passo 6.

**Fluxo alternativo (3): Cadastro de responsável**

a) O gestor seleciona o perfil Responsável.
b) O sistema valida os dados e cria a conta, sem vínculos, registrando
   `usuario_criado` no log.
c) O caso de uso continua no passo 6.

**Fluxo de exceção (4): E-mail já cadastrado**

a) O sistema informa "Já existe uma conta com este e-mail." e mantém os
   demais dados preenchidos.
b) Se a conta existente for de responsável, o sistema oferece o atalho
   "Vincular a outro aluno" (RF14).

**Fluxo de exceção (4): Campo obrigatório vazio**

a) O sistema indica o campo que precisa ser preenchido e não cria a conta.

**Fluxo de exceção (Cadastro de aluno, b): Nenhuma turma no ano letivo**

a) O sistema informa "Cadastre uma turma antes de cadastrar alunos." e oferece
   o atalho para o RF13.

**Fluxo de exceção (Cadastro de aluno, d): Nenhum responsável cadastrado**

a) O sistema informa "Cadastre um responsável antes de cadastrar alunos." e não
   cria a conta.

**Fluxo de exceção (Cadastro de aluno, e): Nenhum responsável selecionado**

a) O sistema informa "Selecione ao menos um responsável." e não cria a conta.

**Fluxo de exceção (6): Falha no envio do convite**

a) A conta permanece criada.
b) O sistema registra `convite_falha_envio` no log.
c) O sistema informa que o e-mail não pôde ser enviado e que a pessoa pode
   usar "Primeiro acesso" na tela de login.

**Pós-condições:** Conta criada, com matrícula e vínculos (aluno), operação
registrada no log e convite enviado ou falha informada ao gestor.

**Regras de negócio:**

- RN08 – Pelo painel, só podem ser criadas contas de Aluno, Responsável e
  Professor. Contas de Secretaria e Direção são criadas pela equipe técnica.
- RN09 – O e-mail é único no sistema, sem diferenciar letras maiúsculas e
  minúsculas.
- RN10 – Nome e sobrenome são obrigatórios.
- RN11 – O gestor nunca define a senha de outra pessoa.
- RN12 – Se o e-mail de convite falhar, a conta continua criada. A falha é
  registrada no log e a pessoa pode usar "Primeiro acesso" na tela de login.
- RN13 – O aluno é matriculado no mesmo ato do cadastro. Não existe conta de
  aluno sem matrícula ativa no ano letivo atual.
- RN14 – Quem cadastra o aluno deve selecionar ao menos um responsável já
  cadastrado. Por isso, o responsável é cadastrado antes do aluno e, até
  receber um vínculo, não acessa dados acadêmicos.
- RN15 – Quando um responsável que já tem conta passa a responder por outro
  aluno (por exemplo, um irmão matriculado depois), o novo vínculo é feito no
  RF14, sem criar outra conta.

**Critérios de aceite:**

- CA01 – Dado um e-mail ainda não cadastrado, quando o gestor criar uma conta
  de professor, então ela deverá aparecer na lista de usuários e a pessoa
  deverá receber o convite.
- CA02 – Dado um e-mail já cadastrado, quando o gestor tentar criar outra
  conta com ele, então o sistema deverá exibir "Já existe uma conta com este
  e-mail.".
- CA03 – Dado que o serviço de e-mail está indisponível, quando o gestor criar
  a conta, então a conta deverá ser criada e o sistema deverá avisar que o
  e-mail não pôde ser enviado.
- CA04 – Dado um professor autenticado, quando tentar acessar o cadastro de
  usuários, então o sistema deverá negar o acesso.
- CA05 – Dado o cadastro de um aluno sem turma selecionada, quando o gestor
  tentar salvar, então o sistema deverá recusar o cadastro.
- CA06 – Dado o cadastro do aluno A com o responsável R selecionado, quando R
  entrar no sistema, então deverá ver os dados acadêmicos do aluno A.
- CA07 – Dado o cadastro de um aluno sem responsável selecionado, quando o
  gestor tentar salvar, então o sistema deverá recusar o cadastro.

**Situação:** Implementado.

---

### RF04 – Definir ou redefinir senha por e-mail

**Sumário:** Permite que o usuário defina a senha no primeiro acesso ou crie
uma nova senha quando a esquecer, por meio de um link de uso único enviado ao
e-mail cadastrado.

**Ator primário:** Usuário (Secretaria, Direção, Professor, Aluno ou
Responsável).

**Atores secundários:** Serviço de e-mail.

**Pré-condições:** O usuário possui conta cadastrada (RF03).

**Fluxo principal:**

1. O usuário escolhe "Esqueci minha senha" e informa o e-mail.
2. O sistema exibe "Se o e-mail existir, enviamos um link de redefinição.".
3. O sistema gera um link e o envia ao e-mail, registrando
   `esqueci_senha_solicitado` no log.
4. O usuário abre o link, informa a nova senha e a confirma.
5. O sistema valida o link e a senha, grava a nova senha, marca o link como
   usado e registra `senha_redefinida` no log.

**Fluxo alternativo (1): Primeiro acesso**

a) O usuário escolhe "Primeiro acesso" ou abre o link do convite recebido no
   cadastro (RF03).
b) Se a conta ainda não tem senha, o e-mail enviado no passo 3 tem o texto de
   boas-vindas em vez do texto de redefinição.
c) O caso de uso continua no passo 4.

**Fluxo de exceção (3): E-mail não cadastrado**

a) O sistema não envia e-mail nem registra log, mas exibe a mesma mensagem do
   passo 2.

**Fluxo de exceção (3): Falha no envio do e-mail**

a) O sistema registra `esqueci_senha_falha_envio` no log, com a causa.
b) O sistema exibe "Não foi possível enviar o e-mail agora. Tente novamente
   mais tarde.".

**Fluxo de exceção (5): Link inválido, usado ou expirado**

a) O sistema exibe "Token inválido ou expirado." e registra
   `redefinir_senha_falha` no log, sem gravar o código do link.
b) O usuário pode solicitar um novo link (passo 1).

**Fluxo de exceção (5): Senhas diferentes ou muito curtas**

a) O sistema indica o erro no campo e não grava a senha.

**Pós-condições:** Senha definida e link marcado como usado, com registro no
log.

**Regras de negócio:**

- RN16 – O link vale por 1 hora e pode ser usado uma única vez.
- RN17 – Ao gerar um novo link, os links anteriores do mesmo usuário deixam de
  valer.
- RN18 – A resposta ao pedido é sempre a mesma, para não revelar quais e-mails
  estão cadastrados.
- RN19 – A senha deve ter no mínimo 6 caracteres e ser digitada duas vezes de
  forma idêntica.
- RN20 – O código do link nunca é gravado no log de auditoria.

**Critérios de aceite:**

- CA01 – Dado um link gerado há menos de 1 hora e ainda não usado, quando o
  usuário informar uma senha válida, então o sistema deverá gravá-la e
  permitir o login com ela.
- CA02 – Dado um link já usado ou gerado há mais de 1 hora, quando o usuário
  tentar usá-lo, então o sistema deverá exibir que o link é inválido ou está
  expirado.
- CA03 – Dado um e-mail não cadastrado, quando for solicitada a recuperação,
  então o sistema deverá exibir a mesma mensagem exibida para um e-mail
  cadastrado.
- CA04 – Dado que o usuário pediu dois links seguidos, quando usar o primeiro,
  então o sistema deverá recusá-lo.

**Situação:** Implementado.

---

### RF05 – Aceitar o Termo de Uso e Aceite

**Sumário:** Exige que o usuário aceite a versão vigente do Termo de Uso e
Aceite antes de usar as funcionalidades internas, registrando a versão aceita
e a data do aceite.

**Ator primário:** Usuário (Secretaria, Direção, Professor, Aluno ou
Responsável).

**Atores secundários:** Não se aplica.

**Pré-condições:** O usuário está autenticado (RF01) e ainda não aceitou a
versão vigente do termo.

**Fluxo principal:**

1. O sistema exibe a página de aceite, com links para o termo e para a
   Política de Privacidade.
2. O usuário marca "Li e aceito" e confirma.
3. O sistema registra a versão, a data e a hora do aceite e registra
   `termos_aceitos` no log.
4. O sistema libera o acesso ao mural.

**Fluxo alternativo (2): Usuário não aceita o termo**

a) O usuário escolhe "Sair".
b) O sistema encerra a sessão sem registrar aceite. As funcionalidades
   internas continuam bloqueadas no próximo login.

**Fluxo de exceção (3): Versão do termo alterada durante a leitura**

a) O sistema informa "O termo foi atualizado. Recarregue a página e leia a
   versão atual." e não registra o aceite.

**Pós-condições:** Aceite registrado na conta e no log de auditoria.

**Regras de negócio:**

- RN21 – Enquanto não houver aceite da versão vigente, a API recusa as
  operações internas.
- RN22 – Quando a versão do termo muda, todos os usuários precisam aceitar a
  nova versão no próximo acesso.
- RN23 – O botão de confirmação fica desabilitado enquanto "Li e aceito" não
  estiver marcado.

**Critérios de aceite:**

- CA01 – Dado um usuário que nunca aceitou o termo, quando fizer login, então
  o sistema deverá exibir a página de aceite em vez do mural.
- CA02 – Dado que a caixa "Li e aceito" está desmarcada, quando o usuário
  estiver na página de aceite, então o botão de confirmação deverá estar
  desabilitado.
- CA03 – Dado um usuário que aceitou a versão 2.0, quando a versão vigente
  passar a ser outra, então o sistema deverá solicitar um novo aceite.

**Situação:** Implementado.

---

### RF06 – Consultar usuários e histórico de atividades

**Sumário:** Permite ao gestor localizar contas cadastradas e à Direção consultar, no
perfil de cada pessoa, os dados da conta e o histórico de atividades
registrado no log de auditoria.

**Ator primário:** Gestor (Secretaria ou Direção); o histórico de atividades é exclusivo da Direção.

**Atores secundários:** Não se aplica.

**Pré-condições:** O gestor está autenticado e aceitou o termo vigente.

**Fluxo principal:**

1. O gestor acessa o painel da secretaria.
2. O sistema lista as contas em ordem alfabética, 20 por página, com nome,
   e-mail, perfil, turma (para alunos) e situação.
3. O gestor seleciona uma conta.
4. O sistema exibe os dados da conta, a matrícula ou os vínculos e o
   histórico de atividades, do mais recente para o mais antigo.

**Fluxo alternativo (2): Filtrar a lista**

a) O gestor informa um ou mais filtros: nome ou e-mail, perfil, turma e
   situação (ativa ou inativa).
b) O sistema exibe apenas as contas que atendem a todos os filtros.
c) O caso de uso continua no passo 3.

**Fluxo de exceção (Filtrar a lista, b): Nenhuma conta encontrada**

a) O sistema informa "Nenhuma conta encontrada com esses filtros." e mantém os
   filtros preenchidos.

**Pós-condições:** Nenhuma alteração de dados.

**Regras de negócio:**

- RN24 – A tela exibe no máximo os 200 registros mais recentes do histórico.
  O histórico completo está disponível na exportação (RF07).
- RN25 – O histórico é somente leitura e só pode ser consultado pela Direção,
  que atua como super usuário do sistema. A Secretaria vê a lista de contas e
  os dados cadastrais, mas não o histórico nem a exportação (RF07).

**Critérios de aceite:**

- CA01 – Dado um usuário que fez login, quando o gestor abrir o perfil dele,
  então o login deverá aparecer no histórico com data, hora e endereço IP.
- CA02 – Dado um aluno autenticado, quando tentar acessar o perfil de outro
  usuário, então o sistema deverá negar o acesso.
- CA04 – Dada a Secretaria autenticada, quando abrir o perfil de um usuário,
  então o histórico de atividades não deverá ser exibido, e a API deverá
  responder 403 se for chamada diretamente.
- CA03 – Dados os filtros "perfil Aluno" e "turma 3º A", quando o gestor
  aplicá-los, então a lista deverá conter apenas os alunos do 3º A.

**Situação:** Implementado.

---

### RF07 – Exportar os dados de um titular

**Sumário:** Permite à Direção exportar, em arquivo JSON, os dados da conta e
o histórico completo de atividades de um usuário, para atender aos pedidos de
acesso e portabilidade previstos na LGPD.

**Ator primário:** Direção (RN25).

**Atores secundários:** Não se aplica.

**Pré-condições:** A Direção está no perfil do usuário (RF06).

**Fluxo principal:**

1. A Direção clica em "Exportar dados (JSON)".
2. O sistema reúne os dados da conta e todo o histórico de atividades.
3. O sistema registra `dados_exportados` no log.
4. O navegador baixa o arquivo JSON.

**Fluxo de exceção (2): Conta removida durante a operação**

a) O sistema informa que a conta não foi encontrada e não gera o arquivo.

**Pós-condições:** Arquivo baixado e exportação registrada no log.

**Regras de negócio:**

- RN26 – O arquivo informa a data da geração e o e-mail de quem a gerou.
- RN27 – O arquivo não é guardado no servidor. Após a entrega ao titular, deve
  ser apagado do computador da Direção em até 7 dias (Plano de Retenção).
- RN28 – O arquivo não inclui o hash da senha.

**Critérios de aceite:**

- CA01 – Dado um usuário com histórico, quando a Direção exportar os dados,
  então o arquivo deverá conter os dados da conta e todos os registros do
  histórico.
- CA02 – Dada uma exportação concluída, quando a Direção consultar o próprio
  histórico, então deverá constar o evento `dados_exportados`.

**Situação:** Implementado.

---

### RF08 – Publicar aviso no mural

**Sumário:** Permite que gestores e professores publiquem avisos para toda a
escola ou para uma turma, com período de exibição e, se desejado,
notificação por e-mail aos destinatários.

**Ator primário:** Gestor ou Professor.

**Atores secundários:** Serviço de e-mail.

**Pré-condições:** O usuário está autenticado e aceitou o termo vigente.

**Fluxo principal:**

1. O usuário abre o formulário de novo aviso no mural.
2. O sistema apresenta os campos título, conteúdo, destino (toda a escola ou
   uma turma), data de início e data de fim da exibição, e a opção
   "Notificar por e-mail".
3. O usuário preenche título e conteúdo e mantém o destino "Toda a escola",
   o início na data atual e o fim em branco.
4. O sistema valida os campos.
5. O sistema grava o aviso, define o usuário como autor e registra
   `aviso_criado` no log.
6. O aviso passa a aparecer no mural de todos os usuários.

**Fluxo alternativo (3): Aviso para uma turma**

a) O usuário escolhe o destino "Turma" e seleciona a turma. O professor só vê
   na lista as turmas em que leciona.
b) O caso de uso continua no passo 4. No passo 6, o aviso aparece apenas para
   os alunos da turma, os responsáveis vinculados a eles, os professores da
   turma e os gestores.

**Fluxo alternativo (3): Período de exibição definido**

a) O usuário informa a data de início e/ou a data de fim da exibição.
b) O caso de uso continua no passo 4. O aviso só aparece no mural dos
   destinatários dentro desse período (RN34).

**Fluxo alternativo (6): Notificar por e-mail**

a) O usuário marcou "Notificar por e-mail".
b) Na data de início da exibição, o sistema envia aos destinatários um e-mail
   com o título do aviso e o link para o portal.
c) O sistema registra `aviso_notificado` no log, com a quantidade de
   destinatários.

**Fluxo de exceção (4): Título ou conteúdo vazio**

a) O sistema exibe "O título não pode ser vazio." ou "O conteúdo não pode ser
   vazio." no campo correspondente e não grava o aviso.

**Fluxo de exceção (4): Data de fim anterior à data de início**

a) O sistema exibe "A data de fim deve ser igual ou posterior à data de
   início." e não grava o aviso.

**Fluxo de exceção (Notificar por e-mail, b): Falha no envio**

a) O aviso permanece publicado.
b) O sistema registra `aviso_falha_envio` no log, com a causa.

**Pós-condições:** Aviso publicado e registrado no log; notificação enviada
ou falha registrada, quando solicitada.

**Regras de negócio:**

- RN29 – Título e conteúdo são obrigatórios e não podem conter apenas espaços.
- RN30 – O título tem no máximo 200 caracteres.
- RN31 – O autor é sempre o usuário autenticado, sem possibilidade de ser
  informado manualmente.
- RN32 – Avisos não devem conter dados pessoais de alunos além do necessário
  (orientação da Política de Privacidade).
- RN33 – O professor só publica avisos para toda a escola ou para turmas em
  que leciona. Gestores publicam para qualquer turma.
- RN34 – A data de início padrão é a data da publicação. A data de fim é
  opcional e, quando informada, não pode ser anterior à de início. Fora do
  período, o aviso só aparece para o autor e para os gestores, identificado
  como "agendado" ou "encerrado".
- RN35 – O e-mail de notificação contém apenas o título do aviso e o link
  para o portal. Uma falha no envio não impede a publicação.

**Critérios de aceite:**

- CA01 – Dado um professor autenticado, quando publicar um aviso com título e
  conteúdo, então o aviso deverá aparecer no mural com o nome dele e a data.
- CA02 – Dado um título vazio, quando o usuário tentar publicar, então o
  sistema deverá recusar o aviso e exibir "O título não pode ser vazio.".
- CA03 – Dado um aluno autenticado, quando acessar o mural, então o
  formulário de publicação não deverá ser exibido.
- CA04 – Dado um aviso para o 3º A, quando um aluno do 3º B acessar o mural,
  então o aviso não deverá aparecer.
- CA05 – Dado um aviso com fim em 20/11, quando um aluno acessar o mural em
  21/11, então o aviso não deverá aparecer.

**Situação:** Implementado.

---

### RF09 – Gerenciar aviso publicado

**Sumário:** Permite fixar, desafixar, editar e excluir avisos, respeitando a
autoria.

**Ator primário:** Gestor ou Professor.

**Atores secundários:** Não se aplica.

**Pré-condições:** O aviso existe e o usuário tem permissão sobre ele.

**Fluxo principal:**

1. O usuário localiza o aviso no mural.
2. O sistema exibe as ações permitidas ao usuário: fixar ou desafixar, editar
   e excluir.
3. O usuário indica a ação que deseja realizar.
4. O sistema verifica a permissão do usuário sobre o aviso.
5. O sistema executa a ação escolhida (fluxos alternativos) e registra a
   operação no log.

**Fluxo alternativo (3): Fixar ou desafixar**

a) O usuário escolhe "Fixar" ou "Desafixar".
b) O sistema altera a situação do aviso e o reposiciona no mural (RN38).

**Fluxo alternativo (3): Editar**

a) O usuário escolhe "Editar".
b) O sistema exibe o formulário preenchido com os dados atuais do aviso.
c) O usuário altera os campos desejados e confirma.
d) O sistema valida os campos com as mesmas regras do RF08 e grava a
   alteração, registrando `aviso_editado` no log.

**Fluxo alternativo (3): Excluir**

a) O usuário escolhe "Excluir".
b) O sistema pede confirmação.
c) O usuário confirma.
d) O sistema remove o aviso e registra `aviso_excluido` no log, com o título e
   o identificador.

**Fluxo de exceção (4): Usuário sem permissão sobre o aviso**

a) A API responde com o código 403 e nada é alterado.

**Fluxo de exceção (Editar, d): Dados inválidos**

a) O sistema exibe o erro no campo e mantém o aviso sem alteração.

**Fluxo de exceção (Excluir, c): Exclusão cancelada**

a) O usuário cancela a confirmação e o aviso permanece no mural.

**Pós-condições:** Aviso alterado ou excluído e operação registrada no log.

**Regras de negócio:**

- RN36 – Gestores podem gerenciar qualquer aviso. O professor só pode
  gerenciar os avisos que ele próprio publicou.
- RN37 – Se o autor de um aviso for removido, somente os gestores podem
  gerenciá-lo.
- RN38 – Avisos fixados aparecem antes dos demais no mural.
- RN39 – A exclusão remove o aviso definitivamente. O registro da exclusão
  permanece no log, com o título e o identificador do aviso.

**Critérios de aceite:**

- CA01 – Dado um aviso publicado pelo professor A, quando o professor B
  acessar o mural, então os botões de editar, fixar e excluir não deverão
  aparecer para esse aviso, e a API deverá recusar a operação se for chamada
  diretamente.
- CA02 – Dado um aviso fixado, quando o mural for carregado, então ele deverá
  aparecer antes dos avisos não fixados.
- CA03 – Dado um aviso excluído, quando o gestor consultar o histórico do
  autor da exclusão, então deverá constar o evento `aviso_excluido`.

**Situação:** Implementado.

---

### RF10 – Consultar o mural de avisos

**Sumário:** Exibe a cada usuário autenticado os avisos destinados a ele, com
os fixados primeiro e os demais do mais recente para o mais antigo.

**Ator primário:** Usuário (Secretaria, Direção, Professor, Aluno ou
Responsável).

**Atores secundários:** Não se aplica.

**Pré-condições:** O usuário está autenticado e aceitou o termo vigente.

**Fluxo principal:**

1. O usuário acessa o mural.
2. O sistema seleciona os avisos destinados ao usuário e dentro do período de
   exibição (RN40).
3. O sistema lista os avisos com título, conteúdo, autor, data e destino.

**Fluxo alternativo (2): Gestor ou autor**

a) Para gestores, e para o autor nos próprios avisos, o sistema também exibe
   os avisos agendados ou encerrados, identificados como tal.

**Fluxo de exceção (3): Nenhum aviso**

a) O sistema informa "Nenhum aviso publicado ainda.".

**Pós-condições:** Nenhuma alteração de dados.

**Regras de negócio:**

- RN40 – O aluno vê os avisos para toda a escola e para a própria turma. O
  responsável vê os avisos para toda a escola e para as turmas dos alunos
  vinculados. O professor vê os avisos para toda a escola e para as turmas em
  que leciona.
- RN41 – A listagem é paginada em 20 avisos por página.
- RN42 – Se o autor de um aviso for removido, o aviso continua no mural, sem
  o nome do autor.

**Critérios de aceite:**

- CA01 – Dado um aluno autenticado, quando acessar o mural, então deverá ver
  os avisos para toda a escola e para a turma dele, com os fixados no topo.
- CA02 – Dado que não há avisos, quando o usuário acessar o mural, então
  deverá ver "Nenhum aviso publicado ainda.".

**Situação:** Implementado.

---

### RF11 – Registrar log de auditoria

**Sumário:** Registra automaticamente as ações relevantes de segurança e de
alteração de dados, com usuário, ação, detalhes, endereço IP, data e hora.

**Ator primário:** Sistema.

**Atores secundários:** Não se aplica.

**Pré-condições:** Ocorrência de uma das ações listadas na RN43.

**Fluxo principal:**

1. Uma ação monitorada é executada.
2. O sistema grava um registro com o usuário, o código da ação, os detalhes, o
   endereço IP e a data e hora.

**Fluxo alternativo (2): Usuário não identificado**

a) Quando a ação não está ligada a uma conta (por exemplo, login com e-mail
   inexistente ou link de senha inválido), o registro é gravado sem usuário.

**Pós-condições:** Registro gravado e disponível para consulta (RF06, RF07).

**Regras de negócio:**

- RN43 – São registradas as ações: `login_sucesso`, `login_falha`,
  `termos_aceitos`, `usuario_criado`, `convite_falha_envio`,
  `esqueci_senha_solicitado`, `esqueci_senha_falha_envio`,
  `redefinir_senha_falha`, `senha_redefinida`, `aviso_criado`,
  `aviso_editado`, `aviso_excluido` e `dados_exportados`. Com os requisitos
  previstos, passam a ser registradas também as ações de matrícula, vínculo,
  notas, faltas, tarefas e notificações descritas em cada requisito.
- RN44 – Os registros não podem ser alterados nem excluídos por nenhum perfil,
  inclusive no painel administrativo.
- RN45 – Senhas e códigos de redefinição de senha nunca são gravados no log.
- RN46 – Se a conta do usuário for removida, os registros permanecem, sem a
  ligação com a conta.
- RN47 – Os registros são mantidos por 6 meses (Plano de Retenção, RF22).

**Critérios de aceite:**

- CA01 – Dada uma tentativa de login com senha errada, quando a tentativa for
  recusada, então deverá existir um registro `login_falha` com o e-mail
  informado e o endereço IP.
- CA02 – Dado um superusuário no painel administrativo, quando abrir um
  registro de log, então não deverão existir as opções de alterar ou excluir.

**Situação:** Implementado. A exclusão após 6 meses está prevista no RF22.

---

### RF12 – Consultar os documentos de privacidade

**Sumário:** Disponibiliza o Termo de Uso e Aceite, a Política de Privacidade
e o Plano de Retenção e Descarte de Dados em páginas acessíveis a qualquer
momento, inclusive sem login.

**Ator primário:** Usuário de qualquer perfil ou Visitante.

**Atores secundários:** Não se aplica.

**Pré-condições:** Nenhuma.

**Fluxo principal:**

1. O usuário clica em um dos links do rodapé ou da tela de login.
2. O sistema exibe o documento escolhido.

**Pós-condições:** Nenhuma alteração de dados.

**Regras de negócio:**

- RN48 – Os links aparecem no rodapé de todas as páginas.
- RN49 – Cada documento informa a sua versão e a data de vigência.

**Critérios de aceite:**

- CA01 – Dado um visitante, quando clicar em "Política de privacidade" na
  tela de login, então o documento deverá ser exibido sem pedir login.
- CA02 – Dado um usuário em qualquer página interna, quando olhar o rodapé,
  então deverá encontrar os links para os três documentos.

**Situação:** Implementado.

---

### RF13 – Gerenciar ano letivo, turmas e disciplinas

**Sumário:** Permite ao gestor montar a estrutura acadêmica do ano: cadastrar
o ano letivo com as datas dos 4 bimestres, cadastrar as turmas e cadastrar as
disciplinas de cada turma, atribuindo o professor responsável.

**Ator primário:** Gestor (Secretaria ou Direção).

**Atores secundários:** Não se aplica.

**Pré-condições:** O gestor está autenticado e aceitou o termo vigente. Os
professores já estão cadastrados (RF03).

**Fluxo principal:**

1. O gestor acessa "Estrutura acadêmica" no painel da secretaria.
2. O sistema apresenta as operações: ano letivo, turmas e disciplinas.
3. O gestor indica a operação desejada.
4. O sistema executa a operação (fluxos alternativos) e registra no log.
5. Se o gestor desejar continuar, o caso de uso retorna ao passo 2; caso
   contrário, termina.

**Fluxo alternativo (3): Cadastrar ano letivo**

a) O gestor informa o ano e as datas de início e fim de cada um dos 4
   bimestres.
b) O sistema valida as datas e grava o ano letivo, registrando
   `ano_letivo_criado` no log.

**Fluxo alternativo (3): Cadastrar turma**

a) O gestor seleciona o ano letivo e informa o nome (ex.: "3º A"), a série e
   o turno.
b) O sistema valida os dados e grava a turma, registrando `turma_criada` no
   log.

**Fluxo alternativo (3): Cadastrar disciplina da turma**

a) O gestor seleciona a turma e informa o nome da disciplina, a carga horária
   prevista e o professor responsável, escolhido entre as contas de
   professor.
b) O sistema valida os dados e grava a disciplina, registrando
   `disciplina_criada` no log.
c) A disciplina passa a aparecer na lista do professor para lançamento de
   notas e faltas (RF15 e RF16).

**Fluxo alternativo (3): Trocar o professor de uma disciplina**

a) O gestor seleciona a disciplina e escolhe outro professor.
b) O sistema grava a troca e registra `professor_alterado` no log. As notas e
   faltas já lançadas são mantidas.

**Fluxo de exceção (Cadastrar ano letivo, b): Bimestres com datas inválidas**

a) O sistema informa "As datas dos bimestres devem estar em ordem e não podem
   se sobrepor." e não grava o ano letivo.

**Fluxo de exceção (Cadastrar turma, b): Turma já existe**

a) O sistema informa "Já existe a turma 3º A em 2026." e não grava.

**Fluxo de exceção (Cadastrar disciplina da turma, a): Nenhum professor
cadastrado**

a) O sistema informa "Cadastre o professor antes de criar a disciplina." e
   oferece o atalho para o RF03.

**Pós-condições:** Ano letivo, turmas e disciplinas prontos para receber
matrículas (RF03) e lançamentos (RF15 e RF16).

**Regras de negócio:**

- RN50 – O ano letivo é dividido em 4 bimestres consecutivos, sem
  sobreposição de datas.
- RN51 – Não podem existir duas turmas com o mesmo nome no mesmo ano letivo.
- RN52 – Cada disciplina pertence a uma única turma e tem exatamente um
  professor responsável. A mesma matéria em turmas diferentes gera
  disciplinas diferentes (ex.: "Matemática – 3º A" e "Matemática – 3º B").
- RN53 – Turmas e disciplinas com notas lançadas não podem ser excluídas,
  apenas encerradas ao fim do ano letivo.

**Critérios de aceite:**

- CA01 – Dada uma turma "3º A" em 2026, quando o gestor tentar cadastrar outra
  "3º A" em 2026, então o sistema deverá recusar.
- CA02 – Dado um professor atribuído a "Matemática – 3º A", quando ele abrir o
  lançamento de notas, então deverá ver essa disciplina na lista.
- CA03 – Dado um 2º bimestre que começa antes do fim do 1º, quando o gestor
  tentar salvar o ano letivo, então o sistema deverá recusar.

**Situação:** Implementado.

---

### RF14 – Alterar matrícula e vínculos de responsáveis

**Sumário:** Permite ao gestor alterar a situação de alunos já cadastrados:
transferir de turma, rematricular no novo ano letivo e incluir ou remover
vínculos com responsáveis. A matrícula inicial e o primeiro vínculo são
feitos no cadastro (RF03).

**Ator primário:** Gestor (Secretaria ou Direção).

**Atores secundários:** Não se aplica.

**Pré-condições:** O aluno já está cadastrado e matriculado (RF03).

**Fluxo principal:**

1. O gestor busca o aluno e abre o cadastro dele (RF06).
2. O sistema exibe a turma atual, o histórico de matrículas e os
   responsáveis vinculados.
3. O gestor indica a operação desejada: transferir, rematricular, vincular ou
   desvincular responsável.
4. O sistema executa a operação (fluxos alternativos), registra no log e
   exibe a situação atualizada.

**Fluxo alternativo (3): Transferir de turma**

a) O gestor escolhe outra turma do mesmo ano letivo.
b) O sistema encerra a matrícula atual com a data da transferência e cria a
   nova matrícula, registrando `matricula_transferida` no log.

**Fluxo alternativo (3): Rematricular no novo ano letivo**

a) O gestor escolhe o ano letivo seguinte e a turma.
b) O sistema encerra a matrícula do ano anterior e cria a nova, registrando
   `matricula_criada` no log.

**Fluxo alternativo (3): Vincular responsável**

a) O gestor busca uma conta de responsável já existente.
b) O sistema cria o vínculo e registra `vinculo_criado` no log.

**Fluxo alternativo (3): Desvincular responsável**

a) O gestor seleciona o responsável a ser desvinculado e confirma.
b) O sistema remove o vínculo e registra `vinculo_removido` no log.

**Fluxo de exceção (Rematricular, b): Aluno já matriculado no ano**

a) O sistema informa "O aluno já tem matrícula ativa em 2027." e não cria a
   matrícula (RN54).

**Fluxo de exceção (Vincular responsável, b): Vínculo já existe**

a) O sistema informa "Este responsável já está vinculado ao aluno.".

**Fluxo de exceção (Desvincular responsável, a): Último aluno do
responsável**

a) O sistema avisa que o responsável ficará sem alunos vinculados e perderá o
   acesso aos dados acadêmicos, e pede nova confirmação.

**Fluxo de exceção (Desvincular responsável, a): Último responsável do aluno**

a) O sistema informa "O aluno precisa ter ao menos um responsável. Vincule
   outro antes de remover este." e mantém o vínculo.

**Pós-condições:** Matrícula ou vínculo alterado e registrado no log.

**Regras de negócio:**

- RN54 – O aluno tem uma única matrícula ativa por ano letivo.
- RN55 – O responsável só acessa dados acadêmicos dos alunos vinculados a
  ele.
- RN56 – Notas e faltas de uma matrícula encerrada nunca são apagadas e
  continuam no histórico do aluno.
- RN85 – O aluno mantém ao menos um responsável vinculado. Para trocar de
  responsável, o gestor vincula o novo antes de remover o anterior.

**Critérios de aceite:**

- CA01 – Dado um aluno já matriculado em 2026, quando o gestor tentar
  matriculá-lo em outra turma de 2026 sem usar a transferência, então o
  sistema deverá recusar.
- CA02 – Dado um responsável vinculado ao aluno A, quando tentar consultar as
  notas do aluno B, então o sistema deverá negar o acesso.
- CA03 – Dado um aluno transferido do 3º A para o 3º B, quando o gestor
  consultar o boletim, então as notas lançadas no 3º A deverão continuar
  visíveis.

**Situação:** Implementado.

---

### RF15 – Lançar notas

**Sumário:** Permite ao professor lançar, de forma rápida, a nota bimestral
de todos os alunos de uma disciplina e publicá-las para alunos e
responsáveis, que são avisados por e-mail.

**Ator primário:** Professor.

**Atores secundários:** Serviço de e-mail.

**Pré-condições:** O professor é o responsável pela disciplina (RF13) e há
alunos matriculados na turma (RF03).

**Fluxo principal:**

1. O professor acessa "Lançar notas".
2. O sistema apresenta o ano letivo atual e o bimestre em andamento já
   selecionados.
3. O professor confirma ou altera o ano letivo e o bimestre.
4. O sistema exibe apenas as disciplinas atribuídas ao professor naquele ano,
   cada uma identificada com a sua turma.
5. O professor seleciona a disciplina.
6. O sistema lista os alunos matriculados na turma, em ordem alfabética, com
   um campo de nota para cada um.
7. O professor informa as notas e escolhe "Salvar".
8. O sistema valida as notas, grava e registra `notas_lancadas` no log, com a
   disciplina e o bimestre.
9. O professor escolhe "Publicar notas do bimestre".
10. O sistema torna as notas visíveis para os alunos e responsáveis, envia a
    cada um deles um e-mail informando que há notas novas no portal e
    registra `notas_publicadas` no log.

**Fluxo alternativo (7): Lançamento parcial**

a) O professor preenche apenas parte das notas e escolhe "Salvar".
b) O sistema grava as notas informadas, que continuam visíveis apenas para o
   professor e para os gestores.
c) O caso de uso termina. O professor pode retornar mais tarde e continuar no
   passo 6.

**Fluxo alternativo (7): Corrigir nota já publicada**

a) O professor altera a nota de um aluno e escolhe "Salvar".
b) O sistema grava a nova nota e registra `nota_alterada` no log, com o valor
   anterior e o novo.
c) O sistema envia ao aluno e aos seus responsáveis um e-mail informando que
   houve atualização de nota no portal.

**Fluxo de exceção (4): Nenhuma disciplina atribuída**

a) O sistema informa "Você não tem disciplinas atribuídas neste ano letivo.
   Procure a secretaria.".

**Fluxo de exceção (8): Nota inválida**

a) O sistema destaca o campo e exibe "A nota deve estar entre 0 e 10, com até
   uma casa decimal.".
b) Nenhuma nota é gravada até que todos os campos preenchidos estejam
   válidos.

**Fluxo de exceção (9): Notas incompletas**

a) O sistema informa quantos alunos estão sem nota e pede confirmação para
   publicar mesmo assim.

**Fluxo de exceção (10): Falha no envio de e-mail**

a) As notas permanecem publicadas.
b) O sistema registra `notificacao_falha_envio` no log, com a causa.

**Pós-condições:** Notas gravadas e, quando publicadas, visíveis para alunos e
responsáveis; médias recalculadas (RF17); operações registradas no log.

**Regras de negócio:**

- RN57 – A nota vai de 0 a 10, com até uma casa decimal. Cada aluno tem uma
  nota por disciplina e por bimestre.
- RN58 – O professor só lança notas nas disciplinas atribuídas a ele (RN52).
- RN59 – As notas só ficam visíveis para alunos e responsáveis depois de
  publicadas pelo professor.
- RN60 – Toda alteração de nota publicada é registrada no log, com o valor
  anterior e o novo.
- RN61 – O e-mail de notificação nunca contém a nota. Ele apenas informa que
  há notas novas ou atualizadas e traz o link para o portal.

**Critérios de aceite:**

- CA01 – Dada uma nota 11, quando o professor tentar salvá-la, então o sistema
  deverá recusar e exibir a mensagem do fluxo de exceção.
- CA02 – Dado um professor de "Matemática – 3º A", quando abrir o lançamento,
  então não deverá ver "História – 3º A" nem "Matemática – 3º B".
- CA03 – Dadas notas salvas e não publicadas, quando o aluno consultar o
  boletim, então elas não deverão aparecer.
- CA04 – Dada a publicação das notas, quando o responsável receber o e-mail,
  então a mensagem não deverá conter o valor da nota.

**Situação:** Implementado.

---

### RF16 – Registrar faltas

**Sumário:** Permite ao professor registrar a chamada de cada aula de uma
disciplina, marcando os alunos ausentes, e avisa os responsáveis por e-mail
quando o aluno falta.

**Ator primário:** Professor.

**Atores secundários:** Serviço de e-mail.

**Pré-condições:** O professor é o responsável pela disciplina (RF13) e há
alunos matriculados na turma (RF03).

**Fluxo principal:**

1. O professor acessa "Chamada".
2. O sistema apresenta a data atual e as disciplinas atribuídas ao professor,
   cada uma identificada com a sua turma.
3. O professor seleciona a disciplina e informa a quantidade de aulas daquele
   dia (por exemplo, 2 aulas seguidas).
4. O sistema lista os alunos da turma, todos marcados como presentes.
5. O professor desmarca os alunos ausentes e confirma.
6. O sistema grava a chamada no bimestre correspondente à data e registra
   `chamada_registrada` no log.
7. O sistema envia aos responsáveis de cada aluno ausente um e-mail informando
   que há um registro de frequência novo no portal.

**Fluxo alternativo (2): Chamada de outra data**

a) O professor escolhe uma data anterior, dentro do bimestre em andamento.
b) O caso de uso continua no passo 3.

**Fluxo alternativo (3): Corrigir chamada já registrada**

a) O sistema identifica que já existe chamada para a disciplina naquela data e
   a exibe preenchida.
b) O professor corrige as presenças e confirma.
c) O sistema grava a correção e registra `chamada_alterada` no log, com os
   alunos alterados.

**Fluxo de exceção (2): Data futura ou fora do ano letivo**

a) O sistema informa "Escolha uma data entre o início do ano letivo e hoje." e
   não abre a chamada.

**Fluxo de exceção (2): Data de bimestre já encerrado**

a) O sistema informa que o bimestre está encerrado e que a correção deve ser
   solicitada à secretaria.

**Fluxo de exceção (7): Falha no envio de e-mail**

a) A chamada permanece gravada.
b) O sistema registra `notificacao_falha_envio` no log, com a causa.

**Pós-condições:** Chamada gravada; frequência recalculada (RF17);
responsáveis notificados ou falha registrada.

**Regras de negócio:**

- RN62 – Existe uma única chamada por disciplina e por data. Uma nova chamada
  na mesma data é tratada como correção.
- RN63 – A quantidade de aulas de uma chamada vai de 1 a 4. Cada falta conta
  para todas as aulas daquela chamada.
- RN64 – A data da chamada define o bimestre ao qual as aulas e faltas
  pertencem (RN50).
- RN65 – O professor só registra chamadas das disciplinas atribuídas a ele.
- RN66 – O e-mail ao responsável não informa a disciplina nem a quantidade de
  faltas; apenas avisa que há registro novo de frequência e traz o link para
  o portal.

**Critérios de aceite:**

- CA01 – Dada uma chamada de 2 aulas com o aluno A ausente, quando a chamada
  for gravada, então o aluno A deverá ter 2 faltas no bimestre.
- CA02 – Dada uma data futura, quando o professor tentar abrir a chamada,
  então o sistema deverá recusar.
- CA03 – Dado o aluno A ausente, quando a chamada for gravada, então os
  responsáveis do aluno A deverão receber o e-mail e os dos demais alunos,
  não.

**Situação:** Implementado.

---

### RF17 – Calcular médias e frequência

**Sumário:** Calcula automaticamente a média e o percentual de frequência de
cada aluno por disciplina, a partir das notas e chamadas registradas.

**Ator primário:** Sistema.

**Atores secundários:** Não se aplica.

**Pré-condições:** Existem notas (RF15) ou chamadas (RF16) registradas.

**Fluxo principal:**

1. Um usuário consulta o boletim (RF18) ou o painel (RF21).
2. O sistema calcula a média de cada disciplina com as notas publicadas.
3. O sistema calcula a frequência de cada disciplina com as chamadas
   registradas.
4. O sistema destaca as médias e frequências abaixo do mínimo (RN69).

**Fluxo alternativo (2): Ano letivo em andamento**

a) Se nem todos os bimestres têm nota publicada, o sistema calcula a média
   parcial com os bimestres disponíveis e a identifica como "parcial".

**Fluxo alternativo (3): Nenhuma chamada registrada**

a) O sistema exibe a frequência como "—" em vez de 0% ou 100%.

**Pós-condições:** Valores calculados disponíveis para consulta.

**Regras de negócio:**

- RN67 – A média anual da disciplina é a média aritmética das notas
  bimestrais publicadas, com uma casa decimal.
- RN68 – Frequência (%) = (aulas registradas − faltas) ÷ aulas registradas
  × 100.
- RN69 – A média mínima da escola é 6,0. O sistema destaca médias abaixo de
  6,0 e frequência abaixo de 75%, mínimo exigido pela LDB
  (Lei nº 9.394/1996, art. 24, VI).
- RN70 – Médias e frequência não são armazenadas; são calculadas no momento
  da consulta, para nunca ficarem desatualizadas.

**Critérios de aceite:**

- CA01 – Dadas as notas 6,0; 7,0; 8,0 e 9,0, quando o boletim for gerado,
  então a média exibida deverá ser 7,5.
- CA02 – Dadas 40 aulas e 12 faltas, quando a frequência for calculada, então
  deverá ser 70% e aparecer destacada.
- CA03 – Dadas as notas 5,0; 6,0; 5,5 e 6,5, quando a média for calculada,
  então deverá ser 5,8 e aparecer destacada por estar abaixo de 6,0.
- CA04 – Dadas notas apenas no 1º e no 2º bimestre, quando a média for
  calculada, então deverá ser identificada como "parcial".

**Situação:** Implementado.

---

### RF18 – Emitir boletim em PDF

**Sumário:** Gera o boletim do aluno em PDF, com notas por bimestre, faltas,
médias e frequência de cada disciplina.

**Ator primário:** Aluno, Responsável ou Gestor.

**Atores secundários:** Não se aplica.

**Pré-condições:** O aluno está matriculado e tem notas publicadas.

**Fluxo principal:**

1. O aluno acessa "Boletim".
2. O sistema exibe o boletim do ano letivo atual na tela.
3. O aluno escolhe "Baixar PDF".
4. O sistema gera o PDF e inicia o download.

**Fluxo alternativo (1): Responsável**

a) O responsável acessa "Boletim".
b) Se tiver mais de um aluno vinculado, o sistema pede que escolha o aluno.
c) O caso de uso continua no passo 2.

**Fluxo alternativo (1): Gestor**

a) O gestor busca o aluno (RF06) e escolhe "Boletim".
b) O caso de uso continua no passo 2.

**Fluxo alternativo (2): Ano letivo anterior**

a) O usuário escolhe outro ano letivo em que o aluno teve matrícula.
b) O sistema exibe o boletim daquele ano e o caso de uso continua no passo 3.

**Fluxo de exceção (2): Nenhuma nota publicada**

a) O sistema informa "Ainda não há notas publicadas neste ano letivo." e não
   oferece o download.

**Fluxo de exceção (2): Acesso a aluno não permitido**

a) A API responde com o código 403 e o boletim não é exibido (RN71).

**Pós-condições:** Boletim exibido e, quando solicitado, PDF baixado.

**Regras de negócio:**

- RN71 – O aluno só emite o próprio boletim, e o responsável só o dos alunos
  vinculados (RN55).
- RN72 – O PDF é gerado no momento do pedido e não fica armazenado no
  servidor.
- RN73 – O boletim mostra apenas notas publicadas (RN59).

**Critérios de aceite:**

- CA01 – Dado um aluno com notas publicadas, quando solicitar o boletim, então
  deverá receber um PDF com todas as disciplinas da turma.
- CA02 – Dado o aluno A, quando tentar emitir o boletim do aluno B, então o
  sistema deverá negar o acesso.
- CA03 – Dado um responsável com dois alunos vinculados, quando acessar o
  boletim, então o sistema deverá pedir que escolha o aluno.

**Situação:** Implementado. O PDF é gerado com a biblioteca ReportLab.

---

### RF19 – Publicar tarefa com anexos

**Sumário:** Permite ao professor publicar tarefas para uma disciplina, com
prazo de entrega e arquivos anexos, avisando alunos e responsáveis por
e-mail.

**Ator primário:** Professor.

**Atores secundários:** Serviço de e-mail; Aluno e Responsável (consultam).

**Pré-condições:** O professor é o responsável pela disciplina (RF13).

**Fluxo principal:**

1. O professor acessa "Tarefas" e escolhe "Nova tarefa".
2. O sistema exibe as disciplinas atribuídas ao professor.
3. O professor seleciona a disciplina e informa título, descrição e prazo de
   entrega.
4. O sistema valida os dados, publica a tarefa e registra `tarefa_criada` no
   log.
5. O sistema envia aos alunos da turma e aos responsáveis vinculados um e-mail
   com o título da tarefa, o prazo e o link para o portal.

**Fluxo alternativo (3): Tarefa com anexos**

a) O professor anexa um ou mais arquivos.
b) O sistema valida o tipo e o tamanho de cada arquivo (RN75).
c) O caso de uso continua no passo 4.

**Fluxo alternativo (1): Consulta pelo aluno ou responsável**

a) O aluno ou responsável acessa "Tarefas".
b) O sistema lista as tarefas das disciplinas da turma, com as de prazo mais
   próximo primeiro, e permite baixar os anexos.

**Fluxo de exceção (4): Prazo anterior à data atual**

a) O sistema informa "O prazo de entrega não pode ser anterior a hoje." e não
   publica a tarefa.

**Fluxo de exceção (Tarefa com anexos, b): Arquivo inválido**

a) O sistema informa o nome do arquivo recusado e o motivo (tipo ou tamanho).

**Fluxo de exceção (5): Falha no envio de e-mail**

a) A tarefa permanece publicada.
b) O sistema registra `notificacao_falha_envio` no log, com a causa.

**Pós-condições:** Tarefa visível para a turma e notificação enviada ou falha
registrada.

**Regras de negócio:**

- RN74 – Somente o professor envia anexos; alunos não enviam arquivos.
- RN75 – São aceitos arquivos PDF, DOCX, PNG e JPG de até 10 MB cada.
- RN76 – O prazo de entrega não pode ser anterior à data de publicação.

**Critérios de aceite:**

- CA01 – Dado um anexo de 15 MB, quando o professor tentar enviá-lo, então o
  sistema deverá recusar.
- CA02 – Dada uma tarefa da turma 3º A, quando um aluno do 3º B acessar as
  tarefas, então ela não deverá aparecer.

**Situação:** Previsto.

---

### RF20 – Gerenciar o calendário escolar

**Sumário:** Permite ao gestor cadastrar eventos do calendário escolar
(provas, feriados e reuniões), visíveis a todos os usuários.

**Ator primário:** Gestor (Secretaria ou Direção).

**Atores secundários:** Demais perfis (consultam).

**Pré-condições:** O gestor está autenticado e aceitou o termo vigente.

**Fluxo principal:**

1. O gestor acessa o calendário e escolhe "Novo evento".
2. O gestor informa título, tipo, data de início e data de término.
3. O sistema valida as datas e grava o evento.
4. O evento passa a aparecer no calendário de todos os usuários.

**Fluxo alternativo (2): Evento de uma turma**

a) O gestor seleciona a turma do evento (por exemplo, prova do 3º A).
b) O evento aparece apenas para a turma, os responsáveis vinculados e os
   professores da turma.

**Fluxo alternativo (1): Consulta**

a) Qualquer usuário acessa o calendário.
b) O sistema exibe os eventos do mês, permitindo navegar entre os meses.

**Fluxo de exceção (3): Término anterior ao início**

a) O sistema informa "A data de término não pode ser anterior à data de
   início." e não grava o evento.

**Pós-condições:** Evento visível no calendário.

**Regras de negócio:**

- RN77 – A data de término não pode ser anterior à data de início.
- RN78 – Eventos do calendário não contêm dados pessoais.

**Critérios de aceite:**

- CA01 – Dado um evento com término anterior ao início, quando o gestor
  tentar salvá-lo, então o sistema deverá recusar.
- CA02 – Dado um evento do 3º A, quando um aluno do 3º B acessar o calendário,
  então o evento não deverá aparecer.

**Situação:** Previsto.

---

### RF21 – Exibir painel de indicadores

**Sumário:** Exibe, logo após o login, um painel com os indicadores
acadêmicos permitidos ao perfil de quem consulta.

**Ator primário:** Usuário (Aluno, Responsável, Professor, Secretaria ou
Direção).

**Atores secundários:** Não se aplica.

**Pré-condições:** O usuário está autenticado e aceitou o termo vigente.

**Fluxo principal:**

1. O usuário acessa "Painel".
2. O sistema identifica o perfil do usuário.
3. O sistema calcula (RF17) e exibe os indicadores do perfil, conforme os
   fluxos alternativos.

**Fluxo alternativo (3): Aluno**

a) O sistema exibe, para cada disciplina, a média parcial e a frequência,
   destacando os valores abaixo do mínimo (RN69).
b) O sistema exibe as tarefas com prazo nos próximos 7 dias e os próximos
   eventos do calendário da turma.

**Fluxo alternativo (3): Responsável**

a) Se houver mais de um aluno vinculado, o sistema exibe um seletor de aluno.
b) O sistema exibe para o aluno escolhido os mesmos indicadores do fluxo
   "Aluno".

**Fluxo alternativo (3): Professor**

a) O sistema exibe, para cada disciplina atribuída ao professor: a média da
   turma no bimestre, a quantidade de alunos com média abaixo de 6,0 e a
   quantidade de alunos com frequência abaixo de 75%.
b) Ao selecionar um desses indicadores, o professor vê a lista nominal, em
   ordem alfabética, dos alunos daquela disciplina na situação indicada.
c) O sistema indica as disciplinas com notas do bimestre ainda não
   publicadas.

**Fluxo alternativo (3): Gestor**

a) O sistema exibe, para cada turma: a quantidade de alunos matriculados, a
   média geral, o percentual de alunos com média abaixo de 6,0 e o percentual
   com frequência abaixo de 75%.
b) O sistema indica as disciplinas com notas do bimestre ainda não
   publicadas e o professor responsável por cada uma.
c) O sistema exibe a quantidade de contas que ainda não aceitaram o termo
   vigente.

**Fluxo de exceção (3): Sem dados no período**

a) O sistema exibe "Ainda não há notas ou chamadas registradas neste
   bimestre." no lugar dos indicadores.

**Pós-condições:** Nenhuma alteração de dados.

**Regras de negócio:**

- RN79 – O aluno vê apenas os próprios indicadores; o responsável, apenas os
  dos alunos vinculados; o professor, os das suas disciplinas; o gestor, os
  de todas as turmas.
- RN80 – O painel não exibe rankings nem comparações nominais entre alunos.
  Listas nominais aparecem apenas para o professor da disciplina, em ordem
  alfabética, para acompanhamento pedagógico.
- RN83 – Nos percentuais do gestor, o aluno é contado uma vez se estiver abaixo
  do mínimo em ao menos uma disciplina, porque a média e a frequência mínimas
  valem por disciplina (RN69). O cálculo considera apenas matrículas ativas.
- RN84 – A disciplina fica pendente de publicação enquanto algum aluno ativo da
  turma não tiver nota publicada no bimestre consultado.

**Critérios de aceite:**

- CA01 – Dado um aluno autenticado, quando acessar o painel, então não deverá
  ver nenhum dado de outro aluno.
- CA02 – Dado um professor de "Matemática – 3º A" com 3 alunos abaixo de 6,0,
  quando acessar o painel, então deverá ver o indicador "3" nessa disciplina.
- CA03 – Dado um gestor, quando acessar o painel, então deverá ver os
  indicadores de todas as turmas do ano letivo atual.

**Situação:** Parcial. As tarefas e os eventos do fluxo do aluno entram com o
RF19 e o RF20; os demais indicadores estão implementados.

---

### RF22 – Aplicar a retenção e o descarte de dados

**Sumário:** Executa diariamente a rotina que exclui ou anonimiza os dados
cujo prazo de guarda terminou, conforme o Plano de Retenção e Descarte de
Dados.

**Ator primário:** Sistema.

**Atores secundários:** Não se aplica.

**Pré-condições:** Rotina agendada no servidor.

**Fluxo principal:**

1. Uma vez por dia, o sistema identifica os registros com prazo vencido.
2. O sistema exclui ou anonimiza esses registros.
3. O sistema registra `retencao_executada` no log, com a quantidade de
   registros tratados de cada tipo.

**Fluxo de exceção (2): Erro durante a execução**

a) O sistema desfaz as alterações daquela execução.
b) O sistema registra `retencao_falha` no log, com a causa, e tenta novamente
   na execução seguinte.

**Pós-condições:** Dados vencidos excluídos ou anonimizados.

**Regras de negócio:**

- RN81 – Prazos: logs de auditoria, 6 meses; links de senha, excluídos 7 dias
  após a criação; avisos, 1 ano após a publicação; contas desligadas,
  anonimizadas após 1 ano letivo.
- RN82 – O registro da execução não contém dados pessoais.

**Critérios de aceite:**

- CA01 – Dado um log com mais de 6 meses, quando a rotina for executada,
  então o registro deverá deixar de existir.

**Situação:** Previsto.

## 3. Requisitos não funcionais

Cada requisito não funcional indica como pode ser verificado e qual decisão
técnica o atende. A numeração segue a Ficha de Caracterização do projeto.

| ID | Categoria | Requisito (verificável) | Decisão técnica adotada | Situação |
|---|---|---|---|---|
| RNF01 | Segurança | Toda requisição à API, exceto login, recuperação de senha e documentos públicos, deve ser recusada com o código 401 quando não houver token válido. A sessão expira em 30 minutos sem uso e em no máximo 8 horas | Autenticação JWT (djangorestframework-simplejwt), token de renovação de 8 horas, permissão padrão `IsAuthenticated` e permissões por perfil no Django REST Framework | Implementado |
| RNF02 | Segurança | Nenhuma senha pode ser armazenada em texto puro. Chaves de API e senhas de banco não podem estar no repositório | Hash Argon2; segredos em variáveis de ambiente (`.env` fora do Git). Previstos: limite de tentativas de login e exigência de 8 caracteres na definição de senha | Parcial |
| RNF03 | Privacidade (LGPD) | O sistema deve registrar o aceite do termo vigente de 100% dos usuários antes do uso, não revelar quais e-mails estão cadastrados, permitir a exportação dos dados de qualquer titular e nunca incluir notas ou faltas no texto dos e-mails | Termo versionado com aceite registrado; resposta única na recuperação de senha; exportação JSON restrita à Direção; documentos de privacidade públicos; notificações só com título e link (RN61, RN66). Previstos: anonimização e descarte automático (RF22) | Parcial |
| RNF04 | Disponibilidade | O sistema deve estar acessível pela internet, por navegador, sem instalação de aplicativo | Front-end e back-end independentes; implantação prevista na Vercel (front-end) e no Railway (back-end e PostgreSQL). Hoje executa em ambiente local | Previsto |
| RNF05 | Desempenho | As listagens devem retornar no máximo 20 itens por página, e a consulta do mural não pode fazer uma consulta ao banco por aviso | Paginação padrão do DRF; carregamento do autor na mesma consulta (`select_related`); histórico na tela limitado a 200 registros | Implementado |
| RNF06 | Escalabilidade | O back-end não deve guardar sessão em memória, permitindo executar mais de uma instância | Autenticação JWT sem estado (stateless) e API REST versionada em `/api/v1/` | Implementado |
| RNF07 | Confiabilidade | Dados inválidos devem ser recusados com mensagem de erro, sem gravação parcial | Validação nos serializers do DRF e nos formulários do front-end; banco relacional PostgreSQL | Implementado |
| RNF08 | Consistência | Não podem existir duas contas com o mesmo e-mail, e a remoção de uma conta não pode apagar avisos nem logs | Restrição de unicidade no e-mail; chaves estrangeiras com `SET_NULL` em avisos e logs e `CASCADE` nos links de senha | Implementado |
| RNF09 | Resiliência | Uma falha no serviço de e-mail não pode impedir o cadastro de contas nem a publicação de conteúdo, e a espera pelo serviço não pode passar de 10 segundos | Tempo limite de 10 s na chamada ao Brevo; a conta é criada e o conteúdo é publicado mesmo com falha no envio, que fica registrada no log; erro 503 com mensagem clara na recuperação de senha | Implementado |
| RNF10 | Auditabilidade | 100% das ações listadas na RN43 devem gerar registro com usuário, ação, IP, data e hora, e nenhum perfil pode alterar ou excluir esses registros | Modelo `AuditLog`, função única `registrar_log` e painel administrativo somente leitura | Implementado |
| RNF11 | Observabilidade | Falhas de login, de envio de e-mail e de redefinição de senha devem ficar registradas com a causa | Registro das falhas no log de auditoria com a mensagem de erro. Previstos: monitoramento e alertas no ambiente de produção | Parcial |
| RNF12 | Manutenibilidade | Cada domínio do sistema deve ficar em um módulo próprio, as regras de permissão devem estar centralizadas e as regras de negócio devem ter testes automatizados | Apps Django separados (`accounts`, `communication`, `audit` e `academic`); permissões em um único arquivo; cálculos em funções puras (`calculos.py`, `regras.py`); front-end em TypeScript com a API isolada em `src/api`; 143 testes automatizados (pytest e pytest-django), unitários e de integração | Implementado |
| RNF13 | Usabilidade | A interface deve estar em português, indicar o erro de cada campo do formulário e funcionar em telas de celular. O lançamento de notas de uma turma inteira deve ser feito em uma única tela | Mensagens de erro por campo; atalhos "Primeiro acesso" e "Esqueci minha senha"; painel conforme o perfil; lançamento de notas e chamada da turma inteira em tela única (RF15, RF16). Previsto: revisão do layout das demais telas para celular | Parcial |

## 4. Rastreabilidade com o código

| Requisito | Back-end | Front-end | Testes |
|---|---|---|---|
| RF01 | `apps/accounts/views.py` (`CustomTokenObtainPairView`) | `pages/Login.tsx`, `context/AuthContext.tsx` | `test_fluxo_mural.py` |
| RF02 | `apps/accounts/permissions.py` | `routes/ProtectedRoute.tsx` | `test_permissions.py`, `test_avisos_api.py` |
| RF03 | `apps/accounts/views.py` (`UsuarioViewSet.create`), `serializers.py` (`CriarUsuarioSerializer`) | `pages/PainelSecretaria.tsx` | `test_matricula_api.py` |
| RF04 | `apps/accounts/views.py` (`EsqueciSenhaView`, `RedefinirSenhaView`), `emails.py`, `models.py` (`PasswordResetToken`) | `pages/EsqueciSenha.tsx`, `pages/RedefinirSenha.tsx` | `test_password_reset_token.py`, `test_emails.py`, `test_esqueci_senha_view.py` |
| RF05 | `apps/accounts/views.py` (`AceitarTermosView`), `permissions.py` (`AceitouTermosVigentes`) | `pages/AceiteTermos.tsx` | `test_avisos_api.py`, `test_fluxo_mural.py` |
| RF06, RF07 | `apps/accounts/views.py` (ações `logs` e `exportar`, `IsDirecao`) | `pages/PainelSecretaria.tsx`, `pages/PerfilUsuario.tsx` | `test_historico_direcao_api.py`, `test_matricula_api.py` |
| RF08 a RF10 | `apps/communication/` (`Aviso`, `AvisoViewSet`, `AvisoSerializer`, `notificacoes.py`, comando `enviar_avisos_agendados`) | `pages/MuralAvisos.tsx`, `components/AvisoForm.tsx`, `components/AvisoList.tsx` | `test_aviso_serializer.py`, `test_avisos_api.py`, `test_avisos_turma_periodo_api.py`, `test_aviso_persistencia.py`, `test_fluxo_mural.py` |
| RF11 | `apps/audit/` (`AuditLog`, `registrar_log`, `admin.py`) | — | `test_auditlog_persistencia.py`, `test_fluxo_mural.py` |
| RF12 | — | `pages/TermoDeUso.tsx`, `PoliticaDePrivacidade.tsx`, `PlanoDeRetencao.tsx`, `components/RodapeLegal.tsx` | — |
| RF13 | `apps/academic/` (`AnoLetivo`, `Bimestre`, `Turma`, `Disciplina`, `regras.py`) | `pages/EstruturaAcademica.tsx` | `test_regras_bimestres.py`, `test_estrutura_api.py` |
| RF14 | `apps/academic/views.py` (`AlunoMatriculaViewSet`) | `pages/PerfilUsuario.tsx` | `test_matricula_api.py` |
| RF15, RF16 | `apps/academic/views_diario.py` (`DiarioViewSet`), `models.py` (`Nota`, `Chamada`, `Falta`) | `pages/LancarNotas.tsx`, `pages/Chamada.tsx` | `test_diario_api.py` |
| RF17 | `apps/academic/calculos.py`, `servicos.py` (`boletim_da_matricula`) | `pages/Boletim.tsx` | `test_calculos.py`, `test_diario_api.py` |
| RF18 | `apps/academic/pdf.py` (ReportLab), `views_diario.py` (`BoletimPdfView`) | `pages/Boletim.tsx` | `test_boletim_pdf_api.py` |
| RF21 | `apps/academic/indicadores.py`, `views_painel.py` | `pages/Painel.tsx`, `components/GraficosPainel.tsx` | `test_painel_api.py` |

Os arquivos de teste ficam em `backend/apps/<app>/tests/`.
