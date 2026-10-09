# Requisitos Funcionais e Não Funcionais — EducaPortal

**Versão:** 2.0 — 05 de outubro de 2026

## 1. Convenções

Os requisitos seguem o modelo do "Guia de apoio: como descrever requisitos
funcionais" do PFC. Cada requisito funcional (RF) apresenta descrição, atores,
pré-condições, fluxo principal, regras de negócio (RN), pós-condições e
critérios de aceite (CA) no formato "Dado..., quando..., então...".

As regras de negócio têm numeração única no documento (RN01, RN02...), para
que possam ser citadas nos diagramas e nos testes. Os critérios de aceite são
numerados dentro de cada requisito.

O campo **Situação** indica:

- **Implementado:** funciona na versão atual do sistema.
- **Parcial:** parte do requisito funciona e o restante está previsto.
- **Previsto:** definido nesta especificação e será implementado nas próximas
  etapas do projeto.

### 1.1 Atores

| Ator | Descrição |
|---|---|
| Secretaria | Cadastra contas, atende pedidos dos titulares de dados e publica avisos |
| Direção | Possui as mesmas permissões da Secretaria |
| Gestor | Termo usado neste documento para "Secretaria ou Direção" |
| Professor | Publica avisos e, nas próximas etapas, lança notas, faltas e tarefas das suas turmas |
| Aluno | Consulta o mural e, nas próximas etapas, as próprias notas, faltas, tarefas e boletim |
| Responsável | Consulta o mural e, nas próximas etapas, os dados do aluno vinculado |
| Visitante | Pessoa não autenticada |
| Sistema | Ações executadas automaticamente pelo EducaPortal |

### 1.2 Resumo dos requisitos funcionais

| ID | Nome | Atores principais | Situação |
|---|---|---|---|
| RF01 | Autenticar usuário | Todos os perfis | Implementado |
| RF02 | Controlar o acesso por perfil | Sistema | Implementado |
| RF03 | Cadastrar usuário | Gestor | Implementado |
| RF04 | Definir ou redefinir senha por e-mail | Todos os perfis | Implementado |
| RF05 | Aceitar o Termo de Uso e Aceite | Todos os perfis | Implementado |
| RF06 | Consultar usuários e histórico de atividades | Gestor | Implementado |
| RF07 | Exportar os dados de um titular | Gestor | Implementado |
| RF08 | Publicar aviso no mural | Gestor, Professor | Implementado |
| RF09 | Gerenciar aviso publicado | Gestor, Professor | Parcial |
| RF10 | Consultar o mural de avisos | Todos os perfis | Implementado |
| RF11 | Registrar log de auditoria | Sistema | Implementado |
| RF12 | Consultar os documentos de privacidade | Todos, inclusive Visitante | Implementado |
| RF13 | Gerenciar turmas e disciplinas | Gestor | Previsto |
| RF14 | Matricular alunos e vincular responsáveis | Gestor | Previsto |
| RF15 | Lançar notas e faltas | Professor | Previsto |
| RF16 | Calcular médias e frequência | Sistema | Previsto |
| RF17 | Emitir boletim em PDF | Aluno, Responsável, Gestor | Previsto |
| RF18 | Publicar tarefa com anexos | Professor | Previsto |
| RF19 | Gerenciar o calendário escolar | Gestor | Previsto |
| RF20 | Notificar por e-mail novos conteúdos | Sistema | Previsto |
| RF21 | Exibir painel de indicadores | Aluno, Responsável, Professor, Gestor | Previsto |
| RF22 | Aplicar a retenção e o descarte de dados | Sistema | Previsto |

## 2. Requisitos funcionais implementados

### RF01 – Autenticar usuário

**Descrição:** O sistema deverá permitir que usuários cadastrados e ativos se
autentiquem com e-mail e senha, liberando apenas as funcionalidades do seu
perfil, e deverá permitir o encerramento da sessão.

**Atores:** Secretaria, Direção, Professor, Aluno, Responsável.

**Pré-condições:** O usuário possui conta ativa e senha definida (RF04).

**Fluxo principal:**

1. O usuário informa e-mail e senha na tela de login.
2. O sistema valida o formato dos campos antes do envio.
3. O sistema verifica as credenciais.
4. Se forem válidas, o sistema inicia a sessão, registra o login no log de
   auditoria e direciona o usuário ao mural de avisos.
5. Se forem inválidas, o sistema exibe "E-mail ou senha inválidos." e
   registra a tentativa no log de auditoria.
6. Ao escolher "Sair", o sistema encerra a sessão e retorna à tela de login.

**Regras de negócio:**

- RN01 – A senha não é armazenada em texto puro, apenas o seu hash.
- RN02 – A mensagem de falha é a mesma para e-mail inexistente, senha
  incorreta e conta inativa, sem revelar qual dado está errado.
- RN03 – A sessão expira após 30 minutos sem renovação. Enquanto o usuário
  estiver usando o sistema, ela é renovada automaticamente por até 7 dias;
  depois disso, é necessário um novo login.
- RN04 – Contas inativas não podem se autenticar.

**Pós-condições:** Sessão iniciada e login registrado no log, ou acesso
recusado e tentativa registrada no log.

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

**Situação:** Implementado.

---

### RF02 – Controlar o acesso por perfil

**Descrição:** O sistema deverá restringir cada funcionalidade aos perfis
autorizados, tanto nas telas quanto na API.

**Atores:** Sistema.

**Pré-condições:** O usuário está autenticado (RF01).

**Fluxo principal:**

1. O usuário acessa uma página ou faz uma requisição à API.
2. O sistema identifica o perfil do usuário.
3. O sistema verifica se o perfil tem permissão para a operação.
4. Se tiver, a operação é executada. Se não tiver, a API responde com acesso
   negado e a interface redireciona o usuário ao mural.

**Regras de negócio:**

- RN05 – Os perfis são Secretaria, Direção, Professor, Aluno e Responsável.
  Cada conta possui exatamente um perfil.
- RN06 – A verificação de permissão ocorre no back-end. A interface apenas
  oculta o que o perfil não pode usar.
- RN07 – Usuário não autenticado só acessa a página inicial, o login, o
  primeiro acesso, a recuperação de senha e os documentos de privacidade.

**Pós-condições:** Operação executada somente quando o perfil tem permissão.

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

**Descrição:** O sistema deverá permitir que o gestor cadastre contas de
aluno, responsável e professor, enviando automaticamente um convite por
e-mail para que a pessoa defina a própria senha.

**Atores:** Secretaria, Direção.

**Pré-condições:** O gestor está autenticado e aceitou a versão vigente do
termo (RF05).

**Fluxo principal:**

1. O gestor acessa o painel da secretaria.
2. Informa nome, sobrenome, e-mail e perfil da nova conta.
3. O sistema valida os dados.
4. O sistema cria a conta sem senha utilizável e registra a operação no log.
5. O sistema envia o e-mail de primeiro acesso com o link de definição de
   senha (RF04).
6. O sistema informa se o convite foi enviado.

**Regras de negócio:**

- RN08 – Pelo painel, só podem ser criadas contas de Aluno, Responsável e
  Professor. Contas de Secretaria e Direção são criadas pela equipe técnica.
- RN09 – O e-mail é único no sistema, sem diferenciar letras maiúsculas e
  minúsculas.
- RN10 – Nome e sobrenome são obrigatórios.
- RN11 – O gestor nunca define a senha de outra pessoa.
- RN12 – Se o e-mail de convite falhar, a conta continua criada. A falha é
  registrada no log e a pessoa pode usar "Primeiro acesso" na tela de login.

**Pós-condições:** Conta criada, operação registrada no log e convite enviado
ou falha de envio informada ao gestor.

**Critérios de aceite:**

- CA01 – Dado um e-mail ainda não cadastrado, quando o gestor criar a conta,
  então ela deverá aparecer na lista de usuários e a pessoa deverá receber o
  convite.
- CA02 – Dado um e-mail já cadastrado, quando o gestor tentar criar outra
  conta com ele, então o sistema deverá exibir "Já existe uma conta com este
  e-mail."
- CA03 – Dado que o serviço de e-mail está indisponível, quando o gestor criar
  a conta, então a conta deverá ser criada e o sistema deverá avisar que o
  e-mail não pôde ser enviado.
- CA04 – Dado um professor autenticado, quando tentar acessar o cadastro de
  usuários, então o sistema deverá negar o acesso.

**Situação:** Implementado.

---

### RF04 – Definir ou redefinir senha por e-mail

**Descrição:** O sistema deverá permitir que o usuário defina a senha no
primeiro acesso ou crie uma nova senha quando a esquecer, por meio de um link
de uso único enviado ao e-mail cadastrado.

**Atores:** Secretaria, Direção, Professor, Aluno, Responsável.

**Pré-condições:** O usuário possui conta cadastrada (RF03).

**Fluxo principal:**

1. O usuário escolhe "Primeiro acesso" ou "Esqueci minha senha" e informa o
   e-mail.
2. O sistema exibe a mesma confirmação, exista ou não uma conta com aquele
   e-mail.
3. Se a conta existir, o sistema gera um link e o envia por e-mail. Para quem
   ainda não tem senha, o texto do e-mail é o de primeiro acesso.
4. O usuário abre o link, informa a nova senha e a confirma.
5. O sistema valida o link e grava a nova senha.

**Regras de negócio:**

- RN13 – O link vale por 1 hora e pode ser usado uma única vez.
- RN14 – Ao gerar um novo link, os links anteriores do mesmo usuário deixam de
  valer.
- RN15 – A resposta ao pedido é sempre a mesma, para não revelar quais e-mails
  estão cadastrados.
- RN16 – A senha deve ter no mínimo 6 caracteres e ser digitada duas vezes de
  forma idêntica.
- RN17 – O código do link nunca é gravado no log de auditoria.

**Pós-condições:** Senha definida e link marcado como usado, com registro no
log.

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

**Descrição:** O sistema deverá exigir que o usuário aceite a versão vigente
do Termo de Uso e Aceite antes de usar as funcionalidades internas,
registrando a versão aceita e a data do aceite.

**Atores:** Secretaria, Direção, Professor, Aluno, Responsável.

**Pré-condições:** O usuário está autenticado (RF01).

**Fluxo principal:**

1. Após o login, o sistema verifica se o usuário aceitou a versão vigente do
   termo.
2. Se não aceitou, o sistema exibe a página de aceite, com links para o termo
   e para a Política de Privacidade.
3. O usuário marca "Li e aceito" e confirma.
4. O sistema registra a versão, a data e a hora do aceite e grava o evento no
   log.
5. O sistema libera o acesso ao mural.

**Regras de negócio:**

- RN18 – Enquanto não houver aceite da versão vigente, a API recusa as
  operações internas (mural e gestão de usuários).
- RN19 – Quando a versão do termo muda, todos os usuários precisam aceitar a
  nova versão no próximo acesso.
- RN20 – O usuário pode recusar e sair do sistema pelo botão "Sair".

**Pós-condições:** Aceite registrado na conta e no log de auditoria.

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

**Descrição:** O sistema deverá permitir que o gestor liste as contas
cadastradas e consulte, no perfil de cada pessoa, os dados da conta e o
histórico de atividades registrado no log de auditoria.

**Atores:** Secretaria, Direção.

**Pré-condições:** O gestor está autenticado e aceitou o termo vigente.

**Fluxo principal:**

1. O gestor acessa o painel da secretaria.
2. O sistema lista as contas em ordem alfabética, com nome, e-mail, perfil e
   situação.
3. O gestor seleciona uma conta.
4. O sistema exibe os dados da conta e o histórico de atividades, do mais
   recente para o mais antigo.

**Regras de negócio:**

- RN21 – A tela exibe no máximo os 200 registros mais recentes do histórico.
  O histórico completo está disponível na exportação (RF07).
- RN22 – O histórico é somente leitura.

**Pós-condições:** Nenhuma alteração de dados.

**Critérios de aceite:**

- CA01 – Dado um usuário que fez login, quando o gestor abrir o perfil dele,
  então o login deverá aparecer no histórico com data, hora e endereço IP.
- CA02 – Dado um aluno autenticado, quando tentar acessar o perfil de outro
  usuário, então o sistema deverá negar o acesso.

**Situação:** Implementado.

---

### RF07 – Exportar os dados de um titular

**Descrição:** O sistema deverá permitir que o gestor exporte, em arquivo
JSON, os dados da conta e o histórico completo de atividades de um usuário,
para atender aos pedidos de acesso e portabilidade previstos na LGPD.

**Atores:** Secretaria, Direção.

**Pré-condições:** O gestor está no perfil do usuário (RF06).

**Fluxo principal:**

1. O gestor clica em "Exportar dados (JSON)".
2. O sistema reúne os dados da conta e todo o histórico de atividades.
3. O sistema registra a exportação no log.
4. O navegador baixa o arquivo JSON.

**Regras de negócio:**

- RN23 – O arquivo informa a data da geração e o e-mail de quem a gerou.
- RN24 – O arquivo não é guardado no servidor. Após a entrega ao titular, deve
  ser apagado do computador do gestor em até 7 dias (Plano de Retenção).
- RN25 – O arquivo não inclui o hash da senha.

**Pós-condições:** Arquivo baixado e exportação registrada no log.

**Critérios de aceite:**

- CA01 – Dado um usuário com histórico, quando o gestor exportar os dados,
  então o arquivo deverá conter os dados da conta e todos os registros do
  histórico.
- CA02 – Dada uma exportação concluída, quando o gestor consultar o próprio
  histórico, então deverá constar o evento `dados_exportados`.

**Situação:** Implementado.

---

### RF08 – Publicar aviso no mural

**Descrição:** O sistema deverá permitir que gestores e professores publiquem
avisos no mural, com título e conteúdo, registrando o autor e a data de
publicação.

**Atores:** Secretaria, Direção, Professor.

**Pré-condições:** O usuário está autenticado e aceitou o termo vigente.

**Fluxo principal:**

1. O usuário preenche título e conteúdo no formulário do mural.
2. O sistema valida os campos.
3. O sistema grava o aviso, define o usuário como autor e registra a operação
   no log.
4. O aviso passa a aparecer no mural.

**Regras de negócio:**

- RN26 – Título e conteúdo são obrigatórios e não podem conter apenas espaços.
- RN27 – O título tem no máximo 200 caracteres.
- RN28 – O autor é sempre o usuário autenticado, sem possibilidade de ser
  informado manualmente.
- RN29 – Avisos não devem conter dados pessoais de alunos além do necessário
  (orientação da Política de Privacidade).

**Pós-condições:** Aviso publicado e registrado no log.

**Critérios de aceite:**

- CA01 – Dado um professor autenticado, quando publicar um aviso com título e
  conteúdo, então o aviso deverá aparecer no mural com o nome dele e a data.
- CA02 – Dado um título vazio, quando o usuário tentar publicar, então o
  sistema deverá recusar o aviso e exibir uma mensagem de erro.
- CA03 – Dado um aluno autenticado, quando acessar o mural, então o
  formulário de publicação não deverá ser exibido.

**Situação:** Implementado.

---

### RF09 – Gerenciar aviso publicado

**Descrição:** O sistema deverá permitir fixar, desafixar, editar e excluir
avisos, respeitando a autoria.

**Atores:** Secretaria, Direção, Professor.

**Pré-condições:** O aviso existe e o usuário tem permissão sobre ele.

**Fluxo principal:**

1. O usuário localiza o aviso no mural.
2. Escolhe fixar, desafixar ou excluir o aviso.
3. O sistema verifica a permissão do usuário sobre aquele aviso.
4. O sistema aplica a alteração e registra a operação no log.

**Regras de negócio:**

- RN30 – Gestores podem gerenciar qualquer aviso. O professor só pode
  gerenciar os avisos que ele próprio publicou.
- RN31 – Avisos fixados aparecem antes dos demais no mural.
- RN32 – A exclusão remove o aviso definitivamente. O registro da exclusão
  permanece no log, com o título e o identificador do aviso.

**Pós-condições:** Aviso alterado ou excluído e operação registrada no log.

**Critérios de aceite:**

- CA01 – Dado um aviso publicado pelo professor A, quando o professor B
  acessar o mural, então os botões de fixar e excluir não deverão aparecer
  para esse aviso, e a API deverá recusar a operação se for chamada
  diretamente.
- CA02 – Dado um aviso fixado, quando o mural for carregado, então ele deverá
  aparecer antes dos avisos não fixados.
- CA03 – Dado um aviso excluído, quando o gestor consultar o histórico do
  autor da exclusão, então deverá constar o evento `aviso_excluido`.

**Situação:** Parcial. Fixar, desafixar e excluir funcionam na interface. A
edição de título e conteúdo já é aceita pela API, mas a tela de edição está
prevista.

---

### RF10 – Consultar o mural de avisos

**Descrição:** O sistema deverá exibir a todos os usuários autenticados os
avisos publicados, com os fixados primeiro e os demais do mais recente para o
mais antigo.

**Atores:** Secretaria, Direção, Professor, Aluno, Responsável.

**Pré-condições:** O usuário está autenticado e aceitou o termo vigente.

**Fluxo principal:**

1. O usuário acessa o mural.
2. O sistema lista os avisos com título, conteúdo, autor e data.
3. Se não houver avisos, o sistema informa "Nenhum aviso publicado ainda."

**Regras de negócio:**

- RN33 – A listagem é paginada em 20 avisos por página.
- RN34 – Se o autor de um aviso for removido, o aviso continua no mural, sem
  o nome do autor.

**Pós-condições:** Nenhuma alteração de dados.

**Critérios de aceite:**

- CA01 – Dado um aluno autenticado, quando acessar o mural, então deverá ver
  todos os avisos publicados, com os fixados no topo.
- CA02 – Dado que não há avisos, quando o usuário acessar o mural, então
  deverá ver "Nenhum aviso publicado ainda."

**Situação:** Implementado.

---

### RF11 – Registrar log de auditoria

**Descrição:** O sistema deverá registrar automaticamente as ações relevantes
de segurança e de alteração de dados, com usuário, ação, detalhes, endereço IP,
data e hora.

**Atores:** Sistema.

**Pré-condições:** Ocorrência de uma das ações listadas na RN35.

**Fluxo principal:**

1. Uma ação monitorada é executada.
2. O sistema grava um registro com o usuário (quando identificado), o código
   da ação, os detalhes, o endereço IP e a data e hora.

**Regras de negócio:**

- RN35 – São registradas as ações: `login_sucesso`, `login_falha`,
  `termos_aceitos`, `usuario_criado`, `convite_falha_envio`,
  `esqueci_senha_solicitado`, `esqueci_senha_falha_envio`,
  `redefinir_senha_falha`, `senha_redefinida`, `aviso_criado`,
  `aviso_editado`, `aviso_excluido` e `dados_exportados`.
- RN36 – Os registros não podem ser alterados nem excluídos por nenhum perfil,
  inclusive no painel administrativo.
- RN37 – Senhas e códigos de redefinição de senha nunca são gravados no log.
- RN38 – Se a conta do usuário for removida, os registros permanecem, sem a
  ligação com a conta.
- RN39 – Os registros são mantidos por 6 meses (Plano de Retenção, RF22).

**Pós-condições:** Registro gravado e disponível para consulta (RF06, RF07).

**Critérios de aceite:**

- CA01 – Dada uma tentativa de login com senha errada, quando a tentativa for
  recusada, então deverá existir um registro `login_falha` com o e-mail
  informado e o endereço IP.
- CA02 – Dado um superusuário no painel administrativo, quando abrir um
  registro de log, então não deverão existir as opções de alterar ou excluir.

**Situação:** Implementado. A exclusão após 6 meses está prevista no RF22.

---

### RF12 – Consultar os documentos de privacidade

**Descrição:** O sistema deverá disponibilizar o Termo de Uso e Aceite, a
Política de Privacidade e o Plano de Retenção e Descarte de Dados em páginas
acessíveis a qualquer momento, inclusive sem login.

**Atores:** Todos os perfis e Visitante.

**Pré-condições:** Nenhuma.

**Fluxo principal:**

1. O usuário clica em um dos links do rodapé ou da tela de login.
2. O sistema exibe o documento escolhido.

**Regras de negócio:**

- RN40 – Os links aparecem no rodapé de todas as páginas.
- RN41 – Cada documento informa a sua versão e a data de vigência.

**Pós-condições:** Nenhuma alteração de dados.

**Critérios de aceite:**

- CA01 – Dado um visitante, quando clicar em "Política de privacidade" na
  tela de login, então o documento deverá ser exibido sem pedir login.
- CA02 – Dado um usuário em qualquer página interna, quando olhar o rodapé,
  então deverá encontrar os links para os três documentos.

**Situação:** Implementado.

## 3. Requisitos funcionais previstos

Os requisitos abaixo completam o escopo definido na Introdução e nos
Objetivos da monografia. Eles já estão especificados para orientar o
diagrama de classes e as próximas etapas de desenvolvimento.

### RF13 – Gerenciar turmas e disciplinas

**Descrição:** O sistema deverá permitir que o gestor cadastre turmas e
disciplinas do ano letivo e atribua professores às disciplinas de cada turma.

**Atores:** Secretaria, Direção.

**Pré-condições:** Gestor autenticado; professores cadastrados (RF03).

**Fluxo principal:**

1. O gestor cadastra a turma (nome, série, turno e ano letivo).
2. Cadastra as disciplinas.
3. Atribui um professor a cada disciplina da turma.

**Regras de negócio:**

- RN42 – Não podem existir duas turmas com o mesmo nome no mesmo ano letivo.
- RN43 – Cada disciplina de uma turma tem exatamente um professor
  responsável.

**Pós-condições:** Turma pronta para receber matrículas.

**Critérios de aceite:**

- CA01 – Dada uma turma "3º A" em 2026, quando o gestor tentar cadastrar outra
  "3º A" em 2026, então o sistema deverá recusar.
- CA02 – Dado um professor atribuído à disciplina de uma turma, quando ele
  acessar o sistema, então deverá ver essa turma entre as suas.

**Situação:** Previsto.

---

### RF14 – Matricular alunos e vincular responsáveis

**Descrição:** O sistema deverá permitir que o gestor matricule alunos em
turmas e vincule cada responsável aos alunos pelos quais responde.

**Atores:** Secretaria, Direção.

**Pré-condições:** Turma (RF13), aluno e responsável cadastrados (RF03).

**Fluxo principal:**

1. O gestor seleciona a turma e adiciona os alunos.
2. No perfil do responsável, seleciona os alunos vinculados.

**Regras de negócio:**

- RN44 – O aluno tem uma única matrícula ativa por ano letivo.
- RN45 – O responsável só acessa dados acadêmicos dos alunos vinculados a
  ele.

**Pós-condições:** Aluno matriculado e responsável vinculado.

**Critérios de aceite:**

- CA01 – Dado um aluno já matriculado em 2026, quando o gestor tentar
  matriculá-lo em outra turma de 2026, então o sistema deverá recusar.
- CA02 – Dado um responsável vinculado ao aluno A, quando tentar consultar as
  notas do aluno B, então o sistema deverá negar o acesso.

**Situação:** Previsto.

---

### RF15 – Lançar notas e faltas

**Descrição:** O sistema deverá permitir que o professor lance as notas
bimestrais e as faltas dos alunos das turmas e disciplinas atribuídas a ele.

**Atores:** Professor.

**Pré-condições:** Professor atribuído à disciplina da turma (RF13); alunos
matriculados (RF14).

**Fluxo principal:**

1. O professor seleciona turma, disciplina e bimestre (1º a 4º).
2. O sistema lista os alunos da turma.
3. O professor informa a nota e o número de faltas de cada aluno.
4. O sistema valida, grava e registra a operação no log.

**Regras de negócio:**

- RN46 – A nota varia de 0 a 10, com uma casa decimal.
- RN47 – O número de faltas não pode ser negativo nem maior que o número de
  aulas dadas no bimestre.
- RN48 – O professor só lança dados das disciplinas e turmas atribuídas a ele.
- RN49 – Toda alteração de nota ou falta é registrada no log, com o valor
  anterior e o novo.

**Pós-condições:** Notas e faltas gravadas; médias e frequência recalculadas
(RF16).

**Critérios de aceite:**

- CA01 – Dada uma nota 11, quando o professor tentar gravá-la, então o
  sistema deverá recusar.
- CA02 – Dado um professor de Matemática, quando tentar lançar notas de
  História, então o sistema deverá negar a operação.

**Situação:** Previsto.

---

### RF16 – Calcular médias e frequência

**Descrição:** O sistema deverá calcular automaticamente a média e o
percentual de frequência de cada aluno por disciplina.

**Atores:** Sistema.

**Pré-condições:** Existem notas e faltas lançadas (RF15).

**Fluxo principal:**

1. Após cada lançamento, o sistema recalcula a média da disciplina e a
   frequência do aluno.
2. Os valores ficam disponíveis no boletim (RF17) e no painel (RF21).

**Regras de negócio:**

- RN50 – O ano letivo é dividido em 4 bimestres. A média da disciplina é a
  média aritmética das notas bimestrais lançadas.
- RN51 – Frequência (%) = (aulas dadas − faltas) ÷ aulas dadas × 100.
- RN52 – A média mínima da escola é 6,0. O sistema destaca as médias abaixo
  de 6,0 e a frequência abaixo de 75%, mínimo exigido pela LDB
  (Lei nº 9.394/1996, art. 24, VI).
- RN53 – Médias e frequência não são armazenadas; são calculadas no momento
  da consulta.

**Pós-condições:** Valores calculados disponíveis para consulta.

**Critérios de aceite:**

- CA01 – Dadas as notas 6,0; 7,0; 8,0 e 9,0, quando o boletim for gerado,
  então a média exibida deverá ser 7,5.
- CA02 – Dadas 40 aulas e 12 faltas, quando a frequência for calculada, então
  deverá ser 70% e aparecer destacada.
- CA03 – Dadas as notas 5,0; 6,0; 5,5 e 6,5, quando a média for calculada,
  então deverá ser 5,75 e aparecer destacada por estar abaixo de 6,0.

**Situação:** Previsto.

---

### RF17 – Emitir boletim em PDF

**Descrição:** O sistema deverá gerar o boletim do aluno em PDF, com notas,
faltas, médias e frequência por disciplina.

**Atores:** Aluno, Responsável, Secretaria, Direção.

**Pré-condições:** Aluno matriculado com notas lançadas.

**Fluxo principal:**

1. O usuário solicita o boletim.
2. O sistema verifica a permissão, gera o PDF e inicia o download.

**Regras de negócio:**

- RN54 – O aluno só emite o próprio boletim, e o responsável só o dos alunos
  vinculados (RN45).
- RN55 – O PDF é gerado no momento do pedido e não fica armazenado no
  servidor.

**Pós-condições:** Arquivo PDF baixado.

**Critérios de aceite:**

- CA01 – Dado um aluno com notas lançadas, quando solicitar o boletim, então
  deverá receber um PDF com todas as disciplinas da turma.
- CA02 – Dado o aluno A, quando tentar emitir o boletim do aluno B, então o
  sistema deverá negar o acesso.

**Situação:** Previsto.

---

### RF18 – Publicar tarefa com anexos

**Descrição:** O sistema deverá permitir que o professor publique tarefas
para uma turma, com prazo de entrega e arquivos anexos.

**Atores:** Professor (publica); Aluno e Responsável (consultam).

**Pré-condições:** Professor atribuído à turma (RF13).

**Fluxo principal:**

1. O professor informa turma, título, descrição, prazo e anexos.
2. O sistema valida e publica a tarefa.
3. Os alunos da turma e seus responsáveis passam a vê-la.

**Regras de negócio:**

- RN56 – Somente o professor envia anexos; alunos não enviam arquivos.
- RN57 – São aceitos arquivos PDF, DOCX, PNG e JPG de até 10 MB cada.
- RN58 – O prazo de entrega não pode ser anterior à data de publicação.

**Pós-condições:** Tarefa visível para a turma.

**Critérios de aceite:**

- CA01 – Dado um anexo de 15 MB, quando o professor tentar enviá-lo, então o
  sistema deverá recusar.
- CA02 – Dada uma tarefa da turma 3º A, quando um aluno do 3º B acessar as
  tarefas, então ela não deverá aparecer.

**Situação:** Previsto.

---

### RF19 – Gerenciar o calendário escolar

**Descrição:** O sistema deverá permitir que o gestor cadastre eventos do
calendário escolar (provas, feriados e reuniões), visíveis a todos os
usuários.

**Atores:** Secretaria, Direção (cadastram); todos os perfis (consultam).

**Pré-condições:** Gestor autenticado.

**Fluxo principal:**

1. O gestor informa título, tipo, data de início e data de término.
2. O evento passa a aparecer no calendário.

**Regras de negócio:**

- RN59 – A data de término não pode ser anterior à data de início.
- RN60 – Eventos do calendário não contêm dados pessoais.

**Pós-condições:** Evento visível no calendário.

**Critérios de aceite:**

- CA01 – Dado um evento com término anterior ao início, quando o gestor
  tentar salvá-lo, então o sistema deverá recusar.

**Situação:** Previsto.

---

### RF20 – Notificar por e-mail novos conteúdos

**Descrição:** O sistema deverá avisar por e-mail os usuários interessados
quando houver um novo aviso, uma nova tarefa ou uma nova nota.

**Atores:** Sistema.

**Pré-condições:** Publicação de aviso (RF08), tarefa (RF18) ou nota (RF15).

**Fluxo principal:**

1. O conteúdo é publicado.
2. O sistema identifica os destinatários.
3. O sistema envia o e-mail com um link para o portal.

**Regras de negócio:**

- RN61 – O e-mail não contém a nota, a falta nem outro dado acadêmico; apenas
  informa que há algo novo no portal.
- RN62 – A falha no envio não impede a publicação do conteúdo e é registrada
  no log.

**Pós-condições:** Notificações enviadas ou falhas registradas.

**Critérios de aceite:**

- CA01 – Dada uma nota lançada, quando o aluno receber a notificação, então o
  e-mail não deverá conter o valor da nota.

**Situação:** Previsto.

---

### RF21 – Exibir painel de indicadores

**Descrição:** O sistema deverá exibir um painel com médias e frequência,
respeitando o perfil de quem consulta.

**Atores:** Aluno, Responsável, Professor, Secretaria, Direção.

**Pré-condições:** Notas e faltas lançadas (RF15).

**Fluxo principal:**

1. O usuário acessa o painel.
2. O sistema calcula e exibe os indicadores permitidos ao perfil.

**Regras de negócio:**

- RN63 – O aluno vê apenas os próprios indicadores; o responsável, apenas os
  dos alunos vinculados; o professor, os das suas turmas; o gestor, os de todas
  as turmas.
- RN64 – O painel não exibe rankings nem comparações nominais entre alunos.

**Pós-condições:** Nenhuma alteração de dados.

**Critérios de aceite:**

- CA01 – Dado um aluno autenticado, quando acessar o painel, então não deverá
  ver nenhum dado de outro aluno.

**Situação:** Previsto.

---

### RF22 – Aplicar a retenção e o descarte de dados

**Descrição:** O sistema deverá executar diariamente a rotina que exclui ou
anonimiza os dados cujo prazo de guarda terminou, conforme o Plano de
Retenção e Descarte de Dados.

**Atores:** Sistema.

**Pré-condições:** Rotina agendada no servidor.

**Fluxo principal:**

1. Uma vez por dia, o sistema identifica os registros com prazo vencido.
2. Exclui ou anonimiza esses registros.
3. Grava no log a quantidade de registros tratados de cada tipo.

**Regras de negócio:**

- RN65 – Prazos: logs de auditoria, 6 meses; links de senha, excluídos 7 dias
  após a criação; avisos, 1 ano após a publicação; contas desligadas,
  anonimizadas após 1 ano letivo.
- RN66 – O registro da execução não contém dados pessoais.

**Pós-condições:** Dados vencidos excluídos ou anonimizados.

**Critérios de aceite:**

- CA01 – Dado um log com mais de 6 meses, quando a rotina for executada,
  então o registro deverá deixar de existir.

**Situação:** Previsto.

## 4. Requisitos não funcionais

Cada requisito não funcional indica como pode ser verificado e qual decisão
técnica o atende. A numeração segue a Ficha de Caracterização do projeto.

| ID | Categoria | Requisito (verificável) | Decisão técnica adotada | Situação |
|---|---|---|---|---|
| RNF01 | Segurança | Toda requisição à API, exceto login, recuperação de senha e documentos públicos, deve ser recusada com o código 401 quando não houver token válido. A sessão expira em 30 minutos sem renovação e em no máximo 7 dias | Autenticação JWT (djangorestframework-simplejwt), permissão padrão `IsAuthenticated` e permissões por perfil no Django REST Framework | Implementado |
| RNF02 | Segurança | Nenhuma senha pode ser armazenada em texto puro. Chaves de API e senhas de banco não podem estar no repositório | Hash Argon2; segredos em variáveis de ambiente (`.env` fora do Git). Previstos: limite de tentativas de login e exigência de 8 caracteres na definição de senha | Parcial |
| RNF03 | Privacidade (LGPD) | O sistema deve registrar o aceite do termo vigente de 100% dos usuários antes do uso, não revelar quais e-mails estão cadastrados e permitir a exportação dos dados de qualquer titular | Termo versionado com aceite registrado; resposta única na recuperação de senha; exportação JSON; documentos de privacidade públicos. Previstos: anonimização e descarte automático (RF22) | Parcial |
| RNF04 | Disponibilidade | O sistema deve estar acessível pela internet, por navegador, sem instalação de aplicativo | Front-end e back-end independentes; implantação prevista na Vercel (front-end) e no Railway (back-end e PostgreSQL). Hoje executa em ambiente local | Previsto |
| RNF05 | Desempenho | As listagens devem retornar no máximo 20 itens por página, e a consulta do mural não pode fazer uma consulta ao banco por aviso | Paginação padrão do DRF; carregamento do autor na mesma consulta (`select_related`); histórico na tela limitado a 200 registros | Implementado |
| RNF06 | Escalabilidade | O back-end não deve guardar sessão em memória, permitindo executar mais de uma instância | Autenticação JWT sem estado (stateless) e API REST versionada em `/api/v1/` | Implementado |
| RNF07 | Confiabilidade | Dados inválidos devem ser recusados com mensagem de erro, sem gravação parcial | Validação nos serializers do DRF e nos formulários do front-end; banco relacional PostgreSQL | Implementado |
| RNF08 | Consistência | Não podem existir duas contas com o mesmo e-mail, e a remoção de uma conta não pode apagar avisos nem logs | Restrição de unicidade no e-mail; chaves estrangeiras com `SET_NULL` em avisos e logs e `CASCADE` nos links de senha | Implementado |
| RNF09 | Resiliência | Uma falha no serviço de e-mail não pode impedir o cadastro de contas, e a espera pelo serviço não pode passar de 10 segundos | Tempo limite de 10 s na chamada ao Brevo; a conta é criada mesmo com falha no convite; erro 503 com mensagem clara na recuperação de senha | Implementado |
| RNF10 | Auditabilidade | 100% das ações listadas na RN35 devem gerar registro com usuário, ação, IP, data e hora, e nenhum perfil pode alterar ou excluir esses registros | Modelo `AuditLog`, função única `registrar_log` e painel administrativo somente leitura | Implementado |
| RNF11 | Observabilidade | Falhas de login, de envio de e-mail e de redefinição de senha devem ficar registradas com a causa | Registro das falhas no log de auditoria com a mensagem de erro. Previstos: monitoramento e alertas no ambiente de produção | Parcial |
| RNF12 | Manutenibilidade | Cada domínio do sistema deve ficar em um módulo próprio, e as regras de permissão devem estar centralizadas | Apps Django separados (`accounts`, `communication`, `audit` e, previsto, `academic`); permissões em um único arquivo; front-end em TypeScript com a API isolada em `src/api`. Previstos: testes automatizados | Parcial |
| RNF13 | Usabilidade | A interface deve estar em português, indicar o erro de cada campo do formulário e funcionar em telas de celular | Mensagens de erro por campo; atalhos "Primeiro acesso" e "Esqueci minha senha"; redirecionamento conforme o perfil. Previsto: revisão do layout para telas pequenas | Parcial |

## 5. Rastreabilidade com o código

| Requisito | Back-end | Front-end |
|---|---|---|
| RF01 | `apps/accounts/views.py` (`CustomTokenObtainPairView`) | `pages/Login.tsx`, `context/AuthContext.tsx` |
| RF02 | `apps/accounts/permissions.py` | `routes/ProtectedRoute.tsx` |
| RF03 | `apps/accounts/views.py` (`UsuarioViewSet.create`), `serializers.py` (`CriarUsuarioSerializer`) | `pages/PainelSecretaria.tsx` |
| RF04 | `apps/accounts/views.py` (`EsqueciSenhaView`, `RedefinirSenhaView`), `emails.py`, `models.py` (`PasswordResetToken`) | `pages/EsqueciSenha.tsx`, `pages/RedefinirSenha.tsx` |
| RF05 | `apps/accounts/views.py` (`AceitarTermosView`), `permissions.py` (`AceitouTermosVigentes`) | `pages/AceiteTermos.tsx` |
| RF06, RF07 | `apps/accounts/views.py` (ações `logs` e `exportar`) | `pages/PainelSecretaria.tsx`, `pages/PerfilUsuario.tsx` |
| RF08 a RF10 | `apps/communication/` (`Aviso`, `AvisoViewSet`, `AvisoSerializer`) | `pages/MuralAvisos.tsx`, `components/AvisoForm.tsx`, `components/AvisoList.tsx` |
| RF11 | `apps/audit/` (`AuditLog`, `registrar_log`, `admin.py`) | — |
| RF12 | — | `pages/TermoDeUso.tsx`, `PoliticaDePrivacidade.tsx`, `PlanoDeRetencao.tsx`, `components/RodapeLegal.tsx` |
