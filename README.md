# EducaPortal

Plataforma web para automação de processos acadêmicos e comunicação escolar em
escolas de ensino médio. Trabalho de conclusão do curso de Bacharelado em
Engenharia de Software da Universidade de Mogi das Cruzes (UMC).

**Autor:** Victor Teixeira Novaes
**Orientação:** Prof.ª Viviane Guimaraes Ribeiro
**Coorientação:** Prof. Alessandro Aparecido da Silva

## Estado do projeto

O projeto é entregue em etapas. A tabela mostra o que já funciona e o que está
previsto para as próximas entregas.

| Módulo | Situação |
|---|---|
| Login com JWT, cinco perfis de acesso (Secretaria, Direção, Professor, Aluno, Responsável) e permissões por perfil | Implementado |
| Primeiro acesso e recuperação de senha por e-mail (Brevo) | Implementado |
| Painel da Secretaria: cadastro de contas, histórico de atividades e exportação de dados em JSON | Implementado |
| Mural de avisos (publicar, fixar e excluir) | Implementado |
| Log de auditoria | Implementado |
| Termo de Uso e Aceite, Política de Privacidade e Plano de Retenção (LGPD) | Implementado |
| Turmas, disciplinas, matrículas e vínculo de responsáveis | Previsto |
| Lançamento de notas e faltas, médias e frequência | Previsto |
| Boletim em PDF | Previsto |
| Tarefas com anexos, calendário escolar, notificações por e-mail e painel de indicadores | Previsto |
| Rotina automática de retenção e descarte de dados | Previsto |

## Tecnologias

- **Back-end:** Python, Django 5, Django REST Framework, djangorestframework-simplejwt, argon2-cffi
- **Banco de dados:** PostgreSQL 16
- **Front-end:** React 19, TypeScript, Vite, React Router, Axios
- **E-mail:** API do Brevo
- **Hospedagem prevista:** Railway (back-end e banco) e Vercel (front-end)

## Estrutura do repositório

```
backend/    API Django (apps accounts, communication e audit)
frontend/   Aplicação React
docs/       Documentação do projeto
```

Principais documentos em [docs/](docs/):

| Arquivo | Conteúdo |
|---|---|
| [requisitos.md](docs/requisitos.md) | Requisitos funcionais e não funcionais |
| [diagramas/](docs/diagramas/) | Diagramas de classes (Mermaid e PNG) e BPMN (PNG) |
| [bpmn-educaportal.bpmn](docs/bpmn-educaportal.bpmn) | Cinco processos de negócio em BPMN 2.0 (abre no [bpmn.io](https://bpmn.io)) |
| [termo-de-uso.md](docs/termo-de-uso.md) | Termo de Uso e Aceite |
| [politica-de-privacidade.md](docs/politica-de-privacidade.md) | Política de Privacidade |
| [lgpd/plano-de-retencao.md](docs/lgpd/plano-de-retencao.md) | Plano de Retenção e Descarte de Dados |
| [integracao-api-externa.md](docs/integracao-api-externa.md) | Integração com a API externa (Brevo) |

## Como executar localmente

### Pré-requisitos

- Python 3.10 ou superior
- Node.js 20.19 ou superior
- Docker (para o PostgreSQL)

### 1. Banco de dados

```bash
docker run -d --name educaportal-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=educaportal \
  -p 127.0.0.1:5432:5432 \
  postgres:16
```

Essa senha é apenas para uso local. Em produção, use uma senha própria.

### 2. Back-end

```bash
cd backend
python -m venv venv
# Windows (Git Bash): source venv/Scripts/activate
# Linux e macOS:      source venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Edite o arquivo `.env` e preencha, no mínimo:

| Variável | Descrição |
|---|---|
| `DJANGO_SECRET_KEY` | Chave secreta longa e aleatória (substitua o valor `change-me`) |
| `BREVO_API_KEY` | Chave da API do Brevo, usada para enviar os e-mails |
| `EMAIL_REMETENTE` | Remetente verificado no Brevo |

O arquivo `.env` contém segredos e **nunca deve ser enviado ao Git** (já está no
`.gitignore`).

Depois, crie as tabelas, uma conta de administrador e inicie o servidor:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

A API fica em `http://localhost:8000/api/v1/` e o painel administrativo do
Django em `http://localhost:8000/admin/`. O login usa o **e-mail** como
identificador.

Para que a conta criada com `createsuperuser` entre no sistema como Direção,
altere o papel dela no painel administrativo do Django.

### 3. Front-end

```bash
cd frontend
npm install
npm run dev
```

A aplicação fica em `http://localhost:5173`.

Outros comandos úteis: `npm run build` (compila para produção) e
`npm run lint`.

## Uso básico

1. Entre com a conta de Direção ou Secretaria.
2. No painel da Secretaria, crie as contas de professores, alunos e responsáveis.
   Cada pessoa recebe um e-mail com o link para definir a senha.
3. No primeiro login, a pessoa lê e aceita o Termo de Uso.
4. O mural de avisos fica disponível para todos os perfis. Secretaria, Direção e
   Professor podem publicar.

## Segurança e privacidade

- As senhas são armazenadas com hash Argon2.
- As chaves e senhas ficam em variáveis de ambiente, fora do repositório.
- Nos testes e demonstrações, use apenas dados fictícios (por exemplo, e-mails
  `@exemplo.com`). Não use dados reais de alunos.
- Dúvidas sobre privacidade: educaportal.tcc@gmail.com.

## Licença

Projeto acadêmico, sem licença de uso definida.
