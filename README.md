# EducaPortal

Plataforma web para automação de processos acadêmicos e comunicação escolar em
escolas de ensino médio. Trabalho de conclusão do curso de Bacharelado em
Engenharia de Software da Universidade de Mogi das Cruzes (UMC).

**Autor:** Victor Teixeira Novaes
**Orientação:** Prof.ª Viviane Guimaraes Ribeiro
**Coorientação:** Prof. Alessandro Aparecido da Silva

**Sistema publicado:** https://educa-portal.vercel.app

## Estado do projeto

Todas as funcionalidades previstas estão implementadas, integradas entre o
front-end e o back-end e publicadas em nuvem.

| Módulo | Situação |
|---|---|
| Login com JWT, cinco perfis de acesso (Secretaria, Direção, Professor, Aluno e Responsável) e permissões por perfil | Implementado |
| Primeiro acesso e recuperação de senha por e-mail (Brevo), com senha de no mínimo 8 caracteres | Implementado |
| Contas: cadastro, filtros, histórico de atividades e exportação de dados em JSON (Direção) | Implementado |
| Ano letivo com quatro bimestres, turmas, disciplinas, matrículas e vínculo de responsáveis | Implementado |
| Lançamento e publicação de notas, chamada da turma, médias e frequência | Implementado |
| Boletim na tela e em PDF | Implementado |
| Painel de indicadores com gráficos para cada perfil | Implementado |
| Mural de avisos geral ou por turma, com período de exibição e aviso por e-mail | Implementado |
| Tarefas com prazo e anexos e calendário escolar | Implementado |
| Log de auditoria | Implementado |
| Termo de Uso e Aceite, Política de Privacidade e Plano de Retenção (LGPD) | Implementado |
| Publicação de novas versões do Termo e da Política pela Direção, com novo aceite de todos | Implementado |
| E-mails mascarados nas telas (cada pessoa vê só o próprio e-mail completo) | Implementado |
| Rotina diária de retenção e descarte de dados e anonimização a pedido do titular | Implementado |
| Layout adaptado para celular | Implementado |

## Tecnologias

- **Back-end:** Python 3.14, Django 5, Django REST Framework, djangorestframework-simplejwt, argon2-cffi, ReportLab
- **Banco de dados:** PostgreSQL 16
- **Front-end:** React 19, TypeScript, Vite, React Router, Axios, Recharts
- **E-mail:** API do Brevo
- **Qualidade:** pytest, pytest-django, Ruff e GitHub Actions
- **Hospedagem:** Railway (API em contêiner Docker, banco e rotina diária) e Vercel (front-end)

## Estrutura do repositório

```
backend/    API Django (apps accounts, academic, communication e audit)
frontend/   Aplicação React
docs/       Documentação do projeto
```

Principais documentos em [docs/](docs/):

| Arquivo | Conteúdo |
|---|---|
| [requisitos.md](docs/requisitos.md) | Requisitos funcionais e não funcionais e regras de negócio |
| [termo-de-uso.md](docs/termo-de-uso.md) | Termo de Uso e Aceite (texto original) |
| [politica-de-privacidade.md](docs/politica-de-privacidade.md) | Política de Privacidade (texto original) |
| [lgpd/plano-de-retencao.md](docs/lgpd/plano-de-retencao.md) | Plano de Retenção e Descarte de Dados |
| [integracao-api-externa.md](docs/integracao-api-externa.md) | Integração com a API externa (Brevo) |
| [implantacao.md](docs/implantacao.md) | Publicação no Railway e na Vercel |

O Termo de Uso e a Política de Privacidade podem ganhar novas versões pela aba
**Documentos** da Direção. Enquanto nenhuma versão for publicada pelo portal,
valem os textos de `docs/`.

## Como executar localmente

### Pré-requisitos

- Python 3.14
- Node.js 20.19 ou superior
- Docker (para o PostgreSQL)

### 1. Banco de dados

Gere senhas fortes com `python -c "import secrets; print(secrets.token_urlsafe(30))"`.
A primeira é a do administrador do banco (`educaportal_app`), usada só para manutenção:

```bash
docker run -d --name educaportal-db \
  -e POSTGRES_USER=educaportal_app \
  -e POSTGRES_PASSWORD=<senha-forte> \
  -e POSTGRES_DB=educaportal \
  -p 127.0.0.1:5432:5432 \
  -v educaportal-pgdata:/var/lib/postgresql/data \
  postgres:16
```

Depois, crie o usuário que a aplicação usa, sem permissões de administrador, e ligue o
registro de conexões. Use uma segunda senha forte e coloque-a em `DB_PASSWORD`, no `.env`:

```bash
docker exec -it educaportal-db psql -U educaportal_app -d educaportal -c "
  CREATE ROLE educaportal_django LOGIN PASSWORD '<segunda-senha-forte>';
  ALTER DATABASE educaportal OWNER TO educaportal_django;
  ALTER SCHEMA public OWNER TO educaportal_django;
  ALTER SYSTEM SET log_connections = on;
  ALTER SYSTEM SET log_disconnections = on;
  ALTER SYSTEM SET log_statement = 'ddl';
  ALTER SYSTEM SET log_line_prefix = '%m [%p] %q%u@%d from %h ';
  SELECT pg_reload_conf();"
```

**Segurança:** mantenha o `127.0.0.1:` na opção `-p`. Sem ele, o Docker publica o
banco para toda a rede.

### 2. Back-end

```bash
cd backend
python -m venv venv
# Windows (Git Bash): source venv/Scripts/activate
# Linux e macOS:      source venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

Edite o arquivo `.env` e preencha, no mínimo:

| Variável | Descrição |
|---|---|
| `DJANGO_SECRET_KEY` | Chave secreta longa e aleatória. Sem ela o servidor não sobe |
| `DJANGO_DEBUG` | `True` só no desenvolvimento local. O padrão é `False` |
| `DB_PASSWORD` | Senha do usuário `educaportal_django` criado no passo 1 |
| `BREVO_API_KEY` | Chave da API do Brevo, usada para enviar os e-mails |
| `EMAIL_REMETENTE` | Remetente verificado no Brevo |

O arquivo `.env` contém segredos e **nunca deve ser enviado ao Git** (já está no
`.gitignore`).

Depois, crie as tabelas e inicie o servidor:

```bash
python manage.py migrate
python manage.py runserver
```

A API fica em `http://localhost:8000/api/v1/`. O login usa o **e-mail** como
identificador.

### 3. Dados de demonstração

Para popular o banco com dados fictícios (contas `@exemplo.com`, turmas, notas,
chamadas, avisos, tarefas e eventos), rode depois das migrações:

```bash
python manage.py criar_dados_demo
```

Todas as contas usam a mesma senha: a da variável `DEMO_SENHA` ou, se ela não
estiver definida, a senha padrão que o comando mostra ao terminar. Em um
servidor público, sempre defina `DEMO_SENHA`. Algumas contas criadas:

| Perfil | E-mail |
|---|---|
| Secretaria | `secretaria@exemplo.com` |
| Direção | `direcao@exemplo.com` |
| Professor | `prof.paulo.mendes@exemplo.com` |
| Aluno | `ana.souza@exemplo.com` |
| Responsável (dois alunos) | `rita.souza@exemplo.com` |

Se a demonstração foi criada antes das tarefas e do calendário, acrescente só
essa parte com `python manage.py criar_dados_demo --agenda`.

Para começar sem dados de demonstração, crie uma conta com
`python manage.py createsuperuser` e mude o papel dela para Direção no painel
administrativo do Django (`http://localhost:8000/admin/`).

### 4. Front-end

```bash
cd frontend
npm install
npm run dev
```

A aplicação fica em `http://localhost:5173`.

Outros comandos úteis: `npm run build` (compila para produção) e
`npm run lint`.

### Rotinas diárias

Duas rotinas devem rodar uma vez por dia:

- `python manage.py enviar_avisos_agendados`: envia o e-mail dos avisos cuja
  exibição começou;
- `python manage.py aplicar_retencao`: exclui ou anonimiza os dados com prazo
  vencido, conforme o Plano de Retenção (RF22).

Em produção, um agendamento do Railway executa `python manage.py disparar_rotinas`,
que aciona as duas pela API (veja [docs/implantacao.md](docs/implantacao.md)).

Os anexos das tarefas ficam em `backend/media/` (fora do Git). Para guardá-los
em outra pasta, defina `DJANGO_MEDIA_ROOT` no `.env`.

## Testes

O back-end tem 333 testes automatizados: 159 unitários, que não acessam o banco
de dados, e 174 de integração, marcados com `integracao`, que usam um banco
SQLite em memória.

```bash
cd backend
python -m pytest                      # todos os testes
python -m pytest -m "not integracao"  # só os unitários
python -m ruff check .                # linter
```

Para medir a cobertura, instale o `pytest-cov` (`python -m pip install pytest-cov`)
e rode `python -m pytest --cov=apps --cov=config`. A suíte completa cobre 96% do
código do back-end, e os testes unitários sozinhos cobrem mais de 50%.

A cada pull request para a `main`, o GitHub Actions roda os testes unitários, os
testes de integração e o Ruff.

## Publicação em nuvem

O passo a passo para publicar a API, o banco e a rotina diária no Railway e o
front-end na Vercel, com todas as variáveis de ambiente, está em
[docs/implantacao.md](docs/implantacao.md).

## Uso básico

1. Entre com a conta da Direção ou da Secretaria.
2. Em **Estrutura acadêmica**, cadastre o ano letivo, as turmas e as disciplinas.
3. Em **Contas**, crie as contas de professores, responsáveis e alunos. Cada
   pessoa recebe um e-mail com o link para definir a senha.
4. No primeiro login, a pessoa lê e aceita o Termo de Uso e a Política de Privacidade.
5. O professor lança as notas, registra a chamada e publica tarefas; o aluno e o
   responsável acompanham o painel, o boletim, as tarefas e o calendário.

O manual completo de cada perfil está no Apêndice E da monografia.

## Segurança e privacidade

- As senhas são armazenadas com hash Argon2.
- As chaves e senhas ficam em variáveis de ambiente, fora do repositório.
- Os e-mails aparecem mascarados nas telas (por exemplo, `an***@exemplo.com`);
  cada pessoa vê só o próprio e-mail completo.
- Toda nova versão do Termo de Uso ou da Política de Privacidade exige um novo
  aceite de todos os usuários, e o histórico de versões fica guardado.
- Nos testes e demonstrações, use apenas dados fictícios (por exemplo, e-mails
  `@exemplo.com`). Não use dados reais de alunos.
- Dúvidas sobre privacidade: educaportal.tcc@gmail.com.

## Licença

Projeto acadêmico, sem licença de uso definida.
