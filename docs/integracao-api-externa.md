# Integração com API Externa — Resend

## Serviço utilizado
[Resend](https://resend.com) — provedor de envio de e-mails transacionais.

## Finalidade
Envio do e-mail de recuperação de senha, contendo um link com token único
para o usuário redefinir sua senha no EducaPortal.

## Endpoint da API utilizada
`POST https://api.resend.com/emails`, chamado internamente pelo SDK oficial
`resend` para Python, através do método `resend.Emails.send(...)`.

## Forma de autenticação
API Key (Bearer Token), configurada em `resend.api_key` a partir da variável
de ambiente `RESEND_API_KEY` — nunca versionada no repositório, mantida
apenas no arquivo `.env` local de cada ambiente.

## Exemplo de uso no código do projeto

```python
import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY

resend.Emails.send({
    "from": "EducaPortal <onboarding@resend.dev>",
    "to": [usuario.email],
    "subject": "Redefinição de senha - EducaPortal",
    "html": f'<p><a href="{link}">Clique aqui para redefinir sua senha</a></p>',
})

## Limitação do ambiente de testes

No ambiente de desenvolvimento, o envio usa o remetente de testes do Resend
(`onboarding@resend.dev`), que só entrega e-mails para o endereço do dono da
conta Resend. Para produção, é necessário verificar um domínio próprio no
painel do Resend (registros DNS SPF/DKIM) e trocar o remetente para um
endereço desse domínio (ex.: `nao-responda@educaportal.com.br`). Nenhuma outra
alteração de código é necessária.

Falhas no envio são tratadas pela view: o erro retornado pelo Resend é
registrado no log de auditoria com a ação `esqueci_senha_falha_envio`, e a API
responde com status 503.
