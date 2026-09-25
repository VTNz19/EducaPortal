# Política de Privacidade — EducaPortal

**Versão:** 2.0 — 25 de setembro de 2026

Esta política explica quais dados pessoais o EducaPortal trata, para que
eles são usados, com quem são compartilhados, por quanto tempo ficam
guardados e como você pode exercer os seus direitos, conforme a Lei Geral de
Proteção de Dados Pessoais (LGPD — Lei nº 13.709/2018).

O EducaPortal é um projeto acadêmico, desenvolvido como Projeto Final de
Curso de Engenharia de Software da Universidade de Mogi das Cruzes. Esta
política descreve o sistema completo, como ele será na versão final. As
funcionalidades que ainda estão em desenvolvimento aparecem marcadas como
"(previsto)".

## 1. Quem é responsável pelos seus dados

- **Controladora:** a instituição de ensino (escola de ensino médio) que
  utiliza o EducaPortal. É ela quem decide quais dados são tratados e para
  quê, por exemplo, quem é matriculado e quais notas são lançadas. Como este
  é um protótipo acadêmico, não há uma escola real vinculada; em uma
  implantação, a escola que adotar o sistema assume esse papel.
- **Operadora:** a equipe do EducaPortal, que desenvolve e mantém o sistema
  e trata os dados em nome da escola, seguindo as instruções dela.
- **Suboperadores:** os serviços externos listados na seção 6.
- **Canal de privacidade:** **educaportal.tcc@gmail.com**. Os pedidos são
  respondidos em até 15 dias. Em uma implantação, a escola indica o seu
  encarregado de proteção de dados (art. 41 da LGPD), que passa a responder
  por esse canal.

## 2. Quais dados tratamos

| Categoria | Dados | De quem | Como são obtidos | Situação |
|---|---|---|---|---|
| Identificação e contato | Nome, sobrenome e e-mail | Todos os usuários | Cadastro feito pela secretaria | Implementado |
| Perfil de acesso | Papel no sistema (secretaria, direção, professor, aluno ou responsável) | Todos os usuários | Cadastro feito pela secretaria | Implementado |
| Credencial | Senha, guardada apenas na forma de hash (ninguém consegue lê-la, nem a escola) | Todos os usuários | Criada pelo próprio usuário no primeiro acesso | Implementado |
| Registros de auditoria | Ação realizada, data e hora, endereço IP e e-mail informado na tela de login | Todos os usuários | Gerados automaticamente pelo sistema | Implementado |
| Aceite do termo | Data e versão do Termo de Uso e Aceite aceito | Todos os usuários | Registrado no primeiro acesso e a cada nova versão | Implementado |
| Vínculo responsável e aluno | Quais alunos cada responsável acompanha | Alunos e responsáveis | Cadastro feito pela secretaria | Previsto |
| Dados acadêmicos | Turma, disciplinas, notas, faltas, médias e percentual de frequência | Alunos | Lançados pelos professores; médias e frequência são calculadas pelo sistema | Previsto |
| Conteúdo publicado | Avisos, tarefas e anexos, com o nome do autor | Professores, secretaria e direção | Publicados pelo próprio autor | Avisos: implementado. Tarefas e anexos: previsto |
| Preferências de notificação | Se o usuário quer receber avisos por e-mail | Todos os usuários | Escolha do próprio usuário | Previsto |

**O que não coletamos:** CPF, RG, endereço, telefone, data de nascimento,
fotografia, localização, dados de saúde ou qualquer outro dado pessoal
sensível (art. 5º, II, da LGPD). Nenhum dado é usado para publicidade.

**Decisões automatizadas:** o sistema não toma decisões automatizadas sobre
as pessoas. As médias e o percentual de frequência são apenas cálculos a
partir das notas e faltas lançadas pelo professor, que pode corrigi-las.

## 3. Para que usamos os dados e com qual base legal

| Finalidade | Dados usados | Base legal (LGPD) |
|---|---|---|
| Criar e manter a conta e autenticar o usuário | Identificação, perfil e credencial | Execução de contrato (art. 7º, V): o contrato de prestação de serviços educacionais (matrícula) ou o vínculo de trabalho com a escola |
| Enviar e-mails de primeiro acesso e de recuperação de senha | Nome e e-mail | Execução de contrato (art. 7º, V) |
| Registrar o aceite do Termo de Uso e Aceite | Data e versão aceita | Execução de contrato (art. 7º, V) |
| Comunicação escolar: mural de avisos, tarefas e calendário | Conteúdo publicado e nome do autor | Execução de contrato (art. 7º, V) |
| Lançar notas e faltas, calcular médias e frequência e gerar o boletim (previsto) | Dados acadêmicos | Cumprimento de obrigação legal (art. 7º, II): a Lei de Diretrizes e Bases da Educação (Lei nº 9.394/1996) exige a verificação do rendimento e o controle de frequência (art. 24) |
| Permitir que o responsável acompanhe o aluno vinculado (previsto) | Vínculo e dados acadêmicos | Cumprimento de obrigação legal (art. 7º, II): a escola deve informar os responsáveis sobre a frequência e o rendimento dos alunos (art. 12, VII, da Lei nº 9.394/1996) |
| Avisar por e-mail que há conteúdo novo no portal (previsto) | Nome e e-mail | Legítimo interesse (art. 7º, IX), com opção de desligar as notificações |
| Segurança e rastreabilidade das ações | Registros de auditoria | Legítimo interesse (art. 7º, IX) e exercício regular de direitos (art. 7º, VI) |
| Atender os pedidos dos titulares | Dados da conta e registros de auditoria | Cumprimento de obrigação legal (art. 7º, II, e art. 18) |

O EducaPortal **não usa o consentimento** como base para o funcionamento do
sistema. Os dados são necessários para a prestação do serviço educacional e
para obrigações legais da escola.

### Avaliação do legítimo interesse nos registros de auditoria

- **Finalidade:** detectar acessos indevidos, investigar incidentes de
  segurança e comprovar quem fez cada alteração no sistema.
- **Necessidade:** são registrados apenas a ação, a data e hora, o endereço
  IP e o usuário. Senhas e códigos de acesso nunca são registrados.
- **Expectativa do titular:** o registro é informado nesta política e no
  Termo de Uso e Aceite.
- **Salvaguardas:** só a secretaria, a direção e a equipe técnica consultam
  os registros, sem poder alterá-los, e eles são excluídos após 6 meses.
- **Oposição:** não se aplica enquanto a conta existir, porque os registros
  protegem a segurança de todos os usuários.

## 4. Dados de adolescentes

A maior parte dos alunos do ensino médio é adolescente. O tratamento dos
dados deles segue o melhor interesse do adolescente (art. 14 da LGPD) e usa
as bases legais do art. 7º, como admite o Enunciado CD/ANPD nº 1/2023.
Medidas adotadas:

- Coletamos apenas o mínimo necessário e nenhum dado sensível.
- As notas e faltas de um aluno são vistas só por ele, pelos seus
  responsáveis, pelos seus professores e pela secretaria e direção. Nenhum
  aluno vê os dados de outro, e o sistema não exibe rankings nem
  comparações entre alunos.
- As notificações por e-mail não trazem notas nem faltas, só avisam que há
  algo novo no portal.
- Não há publicidade, criação de perfil comportamental nem venda de dados.
- As contas são criadas pela escola, e o responsável acompanha a vida
  escolar do aluno vinculado (previsto).

## 5. Quem tem acesso a cada dado

| Perfil | O que pode ver |
|---|---|
| Aluno | Os próprios dados; as próprias notas, faltas e boletim (previsto); os avisos; as tarefas da sua turma e o calendário (previsto) |
| Responsável | Os próprios dados; as notas, faltas e boletim somente dos alunos vinculados a ele (previsto); os avisos e o calendário |
| Professor | Os próprios dados; as notas e faltas das turmas em que leciona (previsto); os avisos, podendo editar e excluir apenas os que publicou |
| Secretaria e direção | O cadastro de todos os usuários; os dados acadêmicos de todos os alunos, para emissão de documentos (previsto); os registros de auditoria de cada usuário e a exportação desses dados |
| Equipe técnica | Acesso administrativo para manutenção do sistema, com os registros de auditoria disponíveis apenas para leitura |

Essas regras são verificadas pelo servidor a cada operação, e não apenas
escondidas na tela.

## 6. Compartilhamento e transferência internacional

O EducaPortal **não vende** dados pessoais e **não os compartilha** para
publicidade. Os únicos serviços externos que recebem dados são:

| Serviço | País | Finalidade | Dados enviados | Situação |
|---|---|---|---|---|
| Brevo | França | Envio de e-mails de primeiro acesso, recuperação de senha e notificações | Nome, e-mail e conteúdo da mensagem | Implementado |
| Railway | Estados Unidos | Hospedagem do servidor e do banco de dados | Todos os dados armazenados no sistema | Previsto (produção) |
| Vercel | Estados Unidos | Hospedagem das telas do sistema | Endereço IP e dados técnicos de acesso | Previsto (produção) |

Como esses serviços ficam fora do Brasil, há transferência internacional de
dados. Ela é feita com base nas garantias contratuais oferecidas pelos
provedores, conforme o art. 33 da LGPD e a regulamentação da ANPD sobre
transferência internacional (Resolução CD/ANPD nº 19/2024).

Os dados também podem ser informados a autoridades públicas quando houver
ordem judicial ou obrigação legal.

## 7. Por quanto tempo guardamos os dados

Os prazos completos estão no [Plano de Retenção e Descarte](lgpd/plano-de-retencao.md).
Em resumo:

- **Registros de auditoria:** 6 meses.
- **Links de primeiro acesso e de redefinição de senha:** valem por 1 hora,
  podem ser usados uma vez e são excluídos após 7 dias.
- **Conta:** desativada no dia do desligamento da escola e anonimizada após
  1 ano letivo.
- **Notas e faltas:** durante o vínculo do aluno e por 1 ano letivo depois
  do desligamento (previsto).
- **Avisos:** 1 ano após a publicação. **Tarefas e anexos:** 1 ano após o
  prazo de entrega (previsto).
- **Boletins em PDF e exportações de dados:** não ficam armazenados no
  servidor; são gerados no momento do pedido.
- **Cópias de segurança:** 30 dias (previsto, em produção).

Ao fim de cada prazo, os dados são excluídos ou anonimizados por uma rotina
automática diária (previsto).

## 8. Armazenamento no seu navegador (cookies)

- O EducaPortal **não usa cookies** de publicidade, rastreamento ou análise
  de navegação. Por isso, não há aviso de cookies.
- Para manter você conectado, o sistema guarda no armazenamento local do
  navegador (`localStorage`) um código de renovação da sessão, válido por até
  7 dias. Ele é apagado quando você clica em **Sair**. Esse armazenamento é
  estritamente necessário para o login funcionar.
- O código de acesso usado em cada operação fica só na memória da página e
  expira em 30 minutos.
- Em computadores compartilhados, clique sempre em **Sair** ao terminar.

## 9. Segurança

- Senhas guardadas apenas como hash, com o algoritmo Argon2. Nem a escola
  nem a equipe técnica conseguem ver a sua senha.
- Acesso por códigos de curta duração, renovados automaticamente.
- Permissões de cada perfil verificadas pelo servidor em toda operação.
- Links de primeiro acesso e de redefinição de senha com uso único e
  validade de 1 hora.
- Registro de auditoria das ações relevantes, incluindo tentativas de login
  que falharam.
- Chaves de acesso a serviços externos guardadas fora do código-fonte.
- Comunicação criptografada (HTTPS) em todo o tráfego (previsto, em produção).
- Limite de tentativas de login seguidas (previsto).

Nenhum sistema é totalmente imune a falhas. Se você perceber algo estranho
na sua conta, troque a senha e avise pelo canal de privacidade.

## 10. Seus direitos como titular

A LGPD (art. 18) garante os direitos abaixo. Todos os pedidos são feitos
pelo canal **educaportal.tcc@gmail.com**. No caso de alunos menores de
idade, o responsável legal também pode fazer o pedido.

| Direito | Como é atendido | Situação |
|---|---|---|
| Confirmação e acesso aos dados | A secretaria exporta, pelo sistema, um arquivo com os dados da conta e o histórico de atividades | Implementado |
| Correção de dados incompletos ou errados | A secretaria corrige o cadastro pelo painel administrativo | Implementado |
| Portabilidade | O mesmo arquivo exportado, em formato JSON | Implementado |
| Informação sobre compartilhamento | Descrita na seção 6 desta política | Implementado |
| Anonimização, bloqueio ou eliminação de dados desnecessários | A secretaria anonimiza a conta pelo painel da secretaria | Previsto |
| Oposição | Desligar as notificações por e-mail no próprio perfil (previsto); outros casos pelo canal de privacidade | Parcialmente previsto |
| Revogação do consentimento | Não se aplica, porque o sistema não usa o consentimento como base legal | Não se aplica |
| Revisão de decisões automatizadas | Não se aplica, porque o sistema não toma decisões automatizadas | Não se aplica |

**Como o pedido é atendido:**

1. Você envia o pedido para o canal de privacidade.
2. A secretaria confirma a sua identidade antes de entregar ou alterar
   qualquer dado.
3. Você recebe a resposta em até 15 dias. Se algum dado precisar ser
   mantido por obrigação legal, informamos qual, por quê e até quando.
4. O atendimento fica registrado no log de auditoria.

Você também pode apresentar reclamação à Autoridade Nacional de Proteção de
Dados (ANPD), pelo site gov.br/anpd.

## 11. Incidentes de segurança

Se houver um incidente (por exemplo, um acesso não autorizado aos dados), a
escola e a equipe do EducaPortal:

1. confirmam o incidente;
2. contêm o problema e preservam as evidências;
3. identificam quais dados e quais pessoas foram afetados;
4. avaliam se há risco ou dano relevante aos titulares;
5. se houver, comunicam a ANPD e os titulares afetados em até 3 dias úteis
   (Resolução CD/ANPD nº 15/2024), por e-mail e por aviso no portal;
6. corrigem a causa e registram as medidas tomadas.

## 12. Alterações nesta política

Esta política é revisada a cada nova versão do sistema. Quando houver uma
mudança relevante, ela é comunicada por aviso no mural, e o Termo de Uso e
Aceite é apresentado novamente para aceite no próximo acesso.

| Versão | Data | Alteração |
|---|---|---|
| 1.0 | 22/09/2026 | Primeira versão |
| 2.0 | 25/09/2026 | Revisão completa: novos perfis de acesso, bases legais, dados de adolescentes, serviços externos (Brevo, Railway e Vercel), prazos de retenção, armazenamento no navegador e incidentes |

Consulte também o [Termo de Uso e Aceite](termo-de-uso.md).
