# Plano de Retenção e Descarte de Dados — EducaPortal

**Versão:** 1.0 — 25 de setembro de 2026

## 1. Objetivo

Este plano define por quanto tempo cada categoria de dado pessoal fica
armazenada no EducaPortal, qual critério define esse prazo e o que acontece
com o dado ao final dele. Ele atende aos artigos 15 e 16 da Lei Geral de
Proteção de Dados (LGPD), que tratam do término do tratamento e da
eliminação dos dados.

A coluna "Situação" das tabelas indica o estado de cada item:

- **Implementado:** o controle já funciona na versão atual do sistema.
- **Previsto:** o controle será implementado até a entrega final do projeto.

## 2. Princípios

- **Guardar só o necessário:** cada dado é mantido apenas enquanto serve à
  finalidade para a qual foi coletado.
- **Prazos verificáveis:** todo prazo é contado a partir de um evento
  concreto (criação do registro, fim do prazo de uma tarefa, desligamento do
  aluno), e não "pelo tempo necessário".
- **Descarte automático sempre que possível:** o sistema executa o descarte
  por uma rotina diária. Quando o descarte depende de uma pessoa, ele segue
  um procedimento definido e fica registrado no log de auditoria.
- **Excluir ou anonimizar:** ao final do prazo, o dado é excluído. Quando o
  registro precisa continuar existindo, os dados que identificam a pessoa são
  removidos (anonimização).
- **Não gerar cópias desnecessárias:** boletins em PDF, indicadores do
  painel e exportações são gerados no momento do pedido e não ficam
  armazenados no servidor.

## 3. Tabela de retenção

### 3.1 Dados de conta e acesso

| Categoria | Dados | Finalidade | Prazo ou critério | Destino ao final | Situação |
|---|---|---|---|---|---|
| Conta de usuário | Nome, e-mail, papel, hash da senha | Autenticar e identificar o usuário | Enquanto a pessoa tiver vínculo com a escola. No desligamento, a conta é desativada no mesmo dia e anonimizada após 1 ano letivo | Anonimizar | Conta: implementado. Anonimização: previsto |
| Vínculo responsável e aluno | Quem é responsável por qual aluno | Permitir que o responsável acompanhe apenas o aluno vinculado | Enquanto o aluno tiver vínculo com a escola | Excluir junto com a conta do aluno | Previsto |
| Token de primeiro acesso ou redefinição de senha | Código do token, data de criação | Permitir que o usuário crie ou troque a senha | Vale por 1 hora e só pode ser usado uma vez. É excluído 7 dias após a criação | Excluir | Validade e uso único: implementado. Exclusão após 7 dias: previsto |
| Log de auditoria | Ação, data e hora, endereço IP, usuário, e-mail informado no login | Segurança e rastreabilidade | 6 meses a partir do registro | Excluir | Registro: implementado. Descarte: previsto |

### 3.2 Dados acadêmicos

| Categoria | Dados | Finalidade | Prazo ou critério | Destino ao final | Situação |
|---|---|---|---|---|---|
| Turmas, disciplinas e matrículas | Turma do aluno, disciplinas, professores atribuídos | Organizar o acesso por turma | Durante o ano letivo e por 1 ano letivo após o seu término | Excluir | Previsto |
| Notas e faltas | Notas, faltas, médias e percentual de frequência calculados | Acompanhamento escolar e emissão do boletim | Durante o vínculo do aluno e por 1 ano letivo após o desligamento | Excluir do EducaPortal | Previsto |
| Boletim em PDF | Notas, faltas, médias e frequência do aluno | Entrega ao aluno e aos responsáveis | Não é armazenado: o PDF é gerado no servidor no momento do download | Não se aplica | Previsto |
| Indicadores do painel (dashboard) | Médias e frequência do próprio aluno | Acompanhamento pelo aluno e pelo responsável | Não são armazenados: são calculados a partir das notas e faltas no momento da consulta | Não se aplica | Previsto |

**Sobre notas e faltas:** o EducaPortal não substitui o arquivo oficial da
escola. A guarda permanente do histórico escolar é responsabilidade da
secretaria, no sistema oficial da instituição, conforme a legislação
educacional. Por isso, esses dados podem ser excluídos do EducaPortal após o
prazo acima.

### 3.3 Comunicação

| Categoria | Dados | Finalidade | Prazo ou critério | Destino ao final | Situação |
|---|---|---|---|---|---|
| Avisos do mural (gerais ou por turma) | Título, conteúdo, autor, turma | Comunicação escolar | 1 ano após a publicação | Excluir | Mural geral: implementado. Avisos por turma e descarte: previsto |
| Tarefas | Título, descrição, prazo de entrega, professor, turma | Organizar as atividades da turma | 1 ano após o prazo de entrega da tarefa | Excluir | Previsto |
| Anexos das tarefas | Arquivos enviados pelo professor | Material de apoio da tarefa | Excluídos junto com a tarefa (1 ano após o prazo de entrega) | Excluir o arquivo do armazenamento | Previsto |
| Calendário escolar | Eventos (provas, feriados, reuniões), sem dados pessoais | Organização do ano letivo | Até 1 ano após o fim do ano letivo | Excluir | Previsto |
| E-mails transacionais e notificações | Nome, e-mail, conteúdo da mensagem | Primeiro acesso, recuperação de senha e avisos de novos conteúdos | O EducaPortal não guarda cópia dos e-mails. As notificações não incluem notas nem faltas, só avisam que há algo novo no portal. O Brevo mantém registros de envio conforme a política de privacidade dele | Não se aplica | Primeiro acesso e recuperação de senha: implementado. Notificações: previsto |

### 3.4 Atendimento ao titular, infraestrutura e testes

| Categoria | Dados | Finalidade | Prazo ou critério | Destino ao final | Situação |
|---|---|---|---|---|---|
| Exportação de dados (JSON) | Dados da conta e histórico de atividades | Atender pedidos de acesso e portabilidade do titular | Não fica armazenada no servidor. O arquivo baixado pela secretaria deve ser entregue ao titular e apagado do computador em até 7 dias | Excluir (procedimento manual) | Implementado |
| Cópias de segurança (backups) do banco | Cópia completa do banco de dados, hospedado no Railway | Recuperação em caso de falha | 30 dias. Um dado excluído do sistema desaparece dos backups em até 30 dias | Sobrescrever | Previsto (ambiente de produção) |
| Registros de acesso da hospedagem | Endereço IP e data e hora das requisições, registrados pelo Railway e pela Vercel | Funcionamento e segurança da infraestrutura | Conforme a política de privacidade de cada provedor | Excluídos pelos provedores | Previsto (ambiente de produção) |
| Dados de demonstração | Contas e conteúdos fictícios | Testes acadêmicos | Somente durante o projeto | Excluir ao final do projeto | Implementado |

**Sobre o log de auditoria:** o prazo de 6 meses segue como referência o
artigo 15 do Marco Civil da Internet (Lei nº 12.965/2014), que define esse
período para a guarda de registros de acesso a aplicações.

## 4. Como o descarte é executado

Os três mecanismos abaixo estão previstos para a entrega final do projeto.

- **Rotina automática:** um comando do sistema
  (`python manage.py aplicar_retencao`) é executado uma vez por dia. Ele
  exclui os logs, tokens, avisos, tarefas (com seus anexos), turmas, notas,
  faltas e eventos que passaram do prazo, e anonimiza as contas desligadas há
  mais de 1 ano letivo.
- **Registro do descarte:** cada execução grava no log de auditoria quantos
  registros de cada tipo foram excluídos ou anonimizados, sem incluir dados
  pessoais.
- **Anonimização de conta:** o nome passa a ser "Usuário removido", o e-mail
  é substituído por um endereço inválido e único, a senha deixa de funcionar
  e a conta fica inativa. O e-mail também é apagado dos detalhes dos logs
  antigos dessa pessoa. Os avisos e as tarefas que ela publicou continuam
  disponíveis até o fim do próprio prazo, sem a identificação do autor.

## 5. Pedido de exclusão feito pelo titular

O titular (ou o responsável legal, no caso de alunos menores de idade) pode
pedir a exclusão dos seus dados antes do fim do prazo:

1. O pedido é feito pelo canal de privacidade: **educaportal.tcc@gmail.com**.
2. A secretaria confirma a identidade de quem fez o pedido.
3. A secretaria verifica se algum dado precisa ser mantido por obrigação
   legal (por exemplo, notas do ano letivo em andamento). Se precisar, informa
   ao titular quais dados serão mantidos, o motivo e o prazo.
4. Os demais dados são anonimizados pela secretaria, na página de perfil do
   usuário no painel da secretaria (funcionalidade prevista).
5. O atendimento fica registrado no log de auditoria, e o titular recebe uma
   resposta em até 15 dias.

## 6. Responsáveis

| Quem | Responsabilidade |
|---|---|
| Secretaria | Desativar as contas de pessoas desligadas, atender pedidos dos titulares e apagar os arquivos de exportação após a entrega |
| Professores | Não incluir dados pessoais de alunos em avisos, tarefas ou anexos além do necessário |
| Equipe técnica (operadora do sistema) | Manter a rotina automática de descarte e a política de backups funcionando |
| Direção | Revisar este plano uma vez por ano letivo |

## 7. Revisão

Este plano é revisado a cada ano letivo ou sempre que uma nova
funcionalidade passar a tratar dados pessoais.

| Versão | Data | Alteração |
|---|---|---|
| 1.0 | 25/09/2026 | Primeira versão |
