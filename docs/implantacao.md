# Implantação do EducaPortal (RNF04)

**Versão:** 1.0 — 16 de novembro de 2026

O EducaPortal é publicado em dois serviços de nuvem gerenciada:

| Parte | Onde | Como |
|---|---|---|
| Front-end (React) | Vercel | Build do Vite a partir da pasta `frontend` |
| API (Django) | Railway | Imagem Docker a partir da pasta `backend` (`backend/Dockerfile`) |
| Banco de dados | Railway | PostgreSQL gerenciado, com backups da plataforma |
| Anexos das tarefas | Railway | Volume persistente montado em `/app/media` |
| Rotinas diárias | Railway | Serviço agendado (cron) que chama a API pela rede interna |
| E-mails | Brevo | API de e-mail transacional |

## 1. Antes de começar

- O código a publicar precisa estar no GitHub, na branch que será implantada.
- Gere três valores secretos, um para cada variável abaixo, com
  `python -c "import secrets; print(secrets.token_urlsafe(50))"`:
  `DJANGO_SECRET_KEY`, `ROTINAS_TOKEN` e `DEMO_SENHA`.
- Nenhum desses valores vai para o repositório nem para documentos. Eles ficam
  apenas nas variáveis dos serviços.

## 2. API e banco no Railway

1. Crie um projeto em railway.com com **Deploy from GitHub repo**, escolhendo o
   repositório e a branch.
2. No serviço criado, em **Settings → Source**, defina **Root Directory** como
   `/backend`. O Railway usa o `Dockerfile` dessa pasta.
3. Renomeie o serviço para `api` (os exemplos abaixo usam esse nome).
4. Adicione o banco: **New → Database → PostgreSQL**. Em **Settings →
   Networking** do banco, remova o **TCP Proxy** público, se houver.
5. No serviço `api`, em **Variables**, cadastre:

| Variável | Valor |
|---|---|
| `DJANGO_SECRET_KEY` | valor secreto gerado no passo 1 |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `${{RAILWAY_PUBLIC_DOMAIN}},${{RAILWAY_PRIVATE_DOMAIN}}` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://${{RAILWAY_PUBLIC_DOMAIN}}` |
| `DJANGO_NUM_PROXIES` | `1` |
| `DJANGO_MEDIA_ROOT` | `/app/media` |
| `PORT` | `8000` |
| `DB_NAME` | `${{Postgres.PGDATABASE}}` |
| `DB_USER` | `${{Postgres.PGUSER}}` |
| `DB_PASSWORD` | `${{Postgres.PGPASSWORD}}` |
| `DB_HOST` | `${{Postgres.PGHOST}}` |
| `DB_PORT` | `${{Postgres.PGPORT}}` |
| `ROTINAS_TOKEN` | valor secreto gerado no passo 1 |
| `DEMO_SENHA` | valor secreto gerado no passo 1 |
| `BREVO_API_KEY` | chave da API do Brevo |
| `EMAIL_REMETENTE` | remetente verificado no Brevo |
| `EMAIL_REMETENTE_NOME` | `EducaPortal` |
| `CORS_ALLOWED_ORIGINS` | endereço da Vercel (seção 4) |
| `FRONTEND_URL` | endereço da Vercel (seção 4) |

6. Crie o volume dos anexos: clique com o botão direito no canvas do projeto,
   **New → Volume**, ligue ao serviço `api` e use o caminho de montagem
   `/app/media`.
7. Em **Settings → Networking**, clique em **Generate Domain** para ter o
   endereço público da API (algo como `https://api-xxxx.up.railway.app`).
8. A cada publicação, o contêiner aplica as migrações antes de iniciar o
   servidor. Confira em **Deployments → Logs** se aparece `Listening at`.

## 3. Rotinas diárias (cron) no Railway

O agendador roda em um contêiner separado, sem acesso ao volume dos anexos.
Por isso ele só chama a API pela rede interna, e a retenção de dados (RF22) e o
envio dos avisos agendados (RF08) acontecem no serviço `api`.

1. **New → GitHub Repo**, com o mesmo repositório e a mesma branch. Renomeie
   para `rotinas` e defina **Root Directory** como `/backend`.
2. Em **Settings → Deploy**:
   - **Custom Start Command:** `python manage.py disparar_rotinas`
   - **Cron Schedule:** `0 6 * * *` (todo dia às 6h UTC, 3h no horário de
     Brasília)
3. Em **Variables**:

| Variável | Valor |
|---|---|
| `DJANGO_SECRET_KEY` | `${{api.DJANGO_SECRET_KEY}}` |
| `DJANGO_DEBUG` | `False` |
| `ROTINAS_TOKEN` | `${{api.ROTINAS_TOKEN}}` |
| `ROTINAS_URL` | `http://${{api.RAILWAY_PRIVATE_DOMAIN}}:8000/api/v1/rotinas/diarias/` |

4. Esse serviço não precisa de domínio público. Cada execução aparece nos logs
   com a quantidade de registros tratados, e a API grava `retencao_executada`
   no log de auditoria.

## 4. Front-end na Vercel

1. Em vercel.com, **Add New → Project** e importe o repositório.
2. Em **Root Directory**, escolha `frontend`. O framework Vite é detectado
   sozinho.
3. Em **Environment Variables**, cadastre
   `VITE_API_URL` = `https://<endereço-da-api>/api/v1`.
4. Mantenha ligada a opção **Include files outside the root directory in the
   Build Step** (em **Settings → Build and Deployment**). O front-end lê os
   documentos de privacidade da pasta `docs`, que fica fora de `frontend`.
5. Em **Settings → Git**, defina a branch de produção.
6. Depois do primeiro deploy, copie o endereço (`https://<projeto>.vercel.app`)
   e coloque-o em `CORS_ALLOWED_ORIGINS` e `FRONTEND_URL` no serviço `api` do
   Railway. O serviço é publicado de novo sozinho.

O arquivo `frontend/vercel.json` faz com que endereços como `/boletim` abram o
sistema mesmo quando acessados diretamente, e acrescenta cabeçalhos de
segurança.

## 5. Dados de demonstração

Com a API no ar, crie os dados fictícios uma única vez pelo terminal do
serviço (Railway CLI, comando `railway ssh` no serviço `api`):

```
python manage.py criar_dados_demo
```

Como `DEMO_SENHA` está definida, as contas de demonstração usam essa senha, e
não a do repositório, que é pública. O comando não mostra a senha no log.

## 6. Conferência depois da publicação

- [ ] A página inicial abre no endereço da Vercel, com cadeado (HTTPS).
- [ ] O login funciona com uma conta de demonstração.
- [ ] Um link direto, como `/termo-de-uso`, abre sem erro 404.
- [ ] O boletim em PDF é baixado.
- [ ] Uma tarefa com anexo é publicada, e o anexo continua disponível depois de
      um novo deploy da API (prova de que o volume está ligado).
- [ ] O registro de atividades mostra o endereço IP real de quem fez login, e
      não o do proxy.
- [ ] Os e-mails chegam (primeiro acesso, recuperação de senha, avisos).
- [ ] A execução do serviço `rotinas` aparece nos logs sem erro.

## 7. Segurança em produção

- `DJANGO_DEBUG=False` liga cookies seguros, o cabeçalho de proxy HTTPS,
  `nosniff` e `X-Frame-Options: DENY`.
- O endereço das rotinas responde 404 a quem não envia `ROTINAS_TOKEN`, e fica
  desligado se a variável estiver vazia.
- O limite de tentativas de login e o log de auditoria usam o IP do cliente
  informado pelo proxy da plataforma (`DJANGO_NUM_PROXIES=1`).
- O banco não deve ter porta pública. No serviço Postgres, em **Settings →
  Networking**, remova o **TCP Proxy** se ele existir: a API acessa o banco
  pela rede interna do Railway e não precisa dele.
