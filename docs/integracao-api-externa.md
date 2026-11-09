# Integração com API Externa — Brevo

## Serviço utilizado
[Brevo](https://www.brevo.com) (antigo Sendinblue), provedor de envio de
e-mails transacionais, com sede na França.

## Finalidade
Envio de e-mails transacionais nas seguintes situações:
- **Primeiro acesso:** quando a secretaria cria uma conta, a pessoa recebe um
  link para definir a própria senha;
- **Recuperação de senha:** link enviado pela opção "Esqueci minha senha";
- **Notificações:** aviso do mural com a opção de e-mail marcada (RF08), notas
  publicadas ou corrigidas (RF15) e falta registrada na chamada (RF16).

Nos dois primeiros casos, o link contém um token de uso único que expira em
1 hora. As notificações trazem apenas um texto curto e o link para o portal:
nunca a nota, a falta ou o conteúdo do aviso (RN35, RN61 e RN66).

## Endpoint da API utilizada
`POST https://api.brevo.com/v3/smtp/email`

## Forma de autenticação
API Key enviada no cabeçalho HTTP `api-key`. A chave fica na variável de
ambiente `BREVO_API_KEY`, no arquivo `.env`, que não é versionado no
repositório.

## Dados enviados ao Brevo
Nome e e-mail do destinatário, assunto e conteúdo da mensagem (com o link de
uso único ou o link para o portal). Nenhuma senha é enviada.

As notificações para vários destinatários são enviadas em uma única chamada,
com o campo `messageVersions`: cada pessoa recebe uma mensagem própria, sem
ver os endereços das demais (função `enviar_email_em_lote`).

## Exemplo de uso no código do projeto

```python
import requests
from django.conf import settings

requests.post(
    'https://api.brevo.com/v3/smtp/email',
    headers={'api-key': settings.BREVO_API_KEY, 'accept': 'application/json'},
    json={
        'sender': {'name': 'EducaPortal', 'email': settings.EMAIL_REMETENTE},
        'to': [{'email': usuario.email}],
        'subject': 'Redefinição de senha - EducaPortal',
        'htmlContent': f'<p><a href="{link}">Clique aqui para criar uma nova senha</a></p>',
    },
    timeout=10,
)
```

Implementação completa em `backend/apps/accounts/emails.py`.

## Tratamento de falhas
Se o Brevo recusar o envio, o erro é registrado no log de auditoria
(`esqueci_senha_falha_envio`, `convite_falha_envio`,
`notificacao_falha_envio` ou `aviso_falha_envio`). Uma falha nas notificações
nunca desfaz a publicação do aviso, das notas ou da chamada. No "Esqueci minha
senha", a API responde com status 503. No painel da secretaria, a conta é
criada mesmo assim e a tela avisa que o e-mail não foi enviado; a pessoa pode
usar "Esqueci minha senha" depois.

## Remetente e limitações
- O remetente precisa estar verificado no painel do Brevo.
- O plano gratuito permite 300 e-mails por dia.
- O Brevo pode bloquear chamadas vindas de um endereço IP não autorizado
  (resposta 401). Em produção, é preciso autorizar o IP do servidor ou
  desativar essa restrição no painel do Brevo.
- Remetentes de provedores gratuitos (Gmail, Outlook) podem cair na caixa de
  spam. Em produção, o ideal é usar um domínio próprio autenticado no Brevo
  (registros SPF, DKIM e DMARC).

## Histórico
A primeira versão usava o Resend. Ele foi trocado pelo Brevo porque o plano de
testes do Resend só entrega e-mails para o endereço do dono da conta, a menos
que se configure um domínio próprio.
