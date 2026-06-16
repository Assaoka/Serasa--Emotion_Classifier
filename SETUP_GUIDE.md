# Guia de Configuração — Banco de Dados + Autenticação

Este guia cobre tudo que você precisa fazer para colocar a aplicação no ar com suas próprias contas.

---

## Parte 1 — Banco de Dados (Neon PostgreSQL)

### 1.1 Criar conta no Neon

1. Acesse **[neon.tech](https://neon.tech)**
2. Clique em **"Sign Up"** e crie uma conta com seu email (pode usar o Google Sign In)
3. Confirme o email se necessário

### 1.2 Criar um novo projeto

1. No dashboard do Neon, clique em **"New Project"**
2. Configure assim:
   - **Name**: `emotion-classifier` (ou qualquer nome)
   - **Postgres version**: 16 (padrão)
   - **Region**: `South America (São Paulo)` — menor latência no Brasil
3. Clique em **"Create Project"**

### 1.3 Copiar a Connection String

1. Após criar, você verá uma tela com as credenciais
2. Selecione **"Pooled connection"** (importante para Streamlit!)
3. Copie a string no formato:
   ```
   postgresql://usuario:senha@ep-xxxx-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require
   ```
4. Cole no campo `postgres` do seu `secrets.toml`:
   ```toml
   postgres = "postgresql://SEU_USUARIO:SUA_SENHA@SEU_HOST-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require"
   ```

> **Nota:** As tabelas serão criadas automaticamente na primeira execução do app.

---

## Parte 2 — Google OAuth (Google Cloud Console)

### 2.1 Criar um projeto no Google Cloud Console

1. Acesse **[console.cloud.google.com](https://console.cloud.google.com)**
2. No topo da tela, clique no seletor de projetos → **"New Project"**
3. Configure:
   - **Project name**: `Emotion Classifier`
4. Clique em **"Create"**

### 2.2 Configurar a tela de consentimento OAuth

1. No menu lateral, vá em **APIs & Services → OAuth consent screen**
2. Selecione **"External"** e clique em **"Create"**
3. Preencha os campos obrigatórios:
   - **App name**: `Anotação de Sentimentos`
   - **User support email**: seu email
   - **Developer contact email**: seu email
4. Clique em **"Save and Continue"** em todas as abas (Scopes e Test Users podem ficar vazios por enquanto)
5. No final, clique em **"Back to Dashboard"**

### 2.3 Criar as credenciais OAuth

1. Vá em **APIs & Services → Credentials**
2. Clique em **"+ Create Credentials"** → **"OAuth client ID"**
3. Configure:
   - **Application type**: `Web application`
   - **Name**: `Streamlit App`
4. Em **"Authorized redirect URIs"**, adicione **AMBAS** as URIs:
   - `http://localhost:8501/oauth2callback` (para desenvolvimento local)
   - `https://SEU-APP.streamlit.app/oauth2callback` (para produção — troque pelo URL do seu app)
5. Clique em **"Create"**
6. Copie o **Client ID** e o **Client Secret** que aparecerão

### 2.4 Atualizar o secrets.toml

Abra o arquivo `.streamlit/secrets.toml` e preencha:

```toml
[auth]
redirect_uri = "https://SEU-APP.streamlit.app/oauth2callback"  # URL do Streamlit Cloud
cookie_secret = "db69b758bcf7b9babac2324924be1babae5a9e0f2444f9851b822a1a48fede40"  # já gerado
postgres = "postgresql://..."  # da Parte 1

[auth.google]
client_id = "COLE_O_CLIENT_ID_AQUI.apps.googleusercontent.com"
client_secret = "COLE_O_CLIENT_SECRET_AQUI"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

> **Importante:** O `redirect_uri` deve ser **exatamente igual** ao que você registrou no Google Cloud Console.

---

## Parte 3 — Streamlit Cloud

### 3.1 Configurar os secrets no Streamlit Cloud

Os secrets do `.streamlit/secrets.toml` **não devem ser commitados** no Git (já estão no `.gitignore`).
Você precisa configurá-los diretamente no painel do Streamlit Cloud:

1. Acesse **[share.streamlit.io](https://share.streamlit.io)** e faça login
2. Encontre seu app e clique em **"⋮" (três pontos)** → **"Settings"**
3. Vá na aba **"Secrets"**
4. Cole o conteúdo completo do seu `secrets.toml` (com os valores reais preenchidos)
5. Clique em **"Save"**
6. O app vai reiniciar automaticamente com os novos secrets

### 3.2 Adicionar o URL de produção no Google Cloud Console
****
Quando o Streamlit Cloud gerar o URL do seu app:
1. Volte em **Google Cloud Console → APIs & Services → Credentials**
2. Clique no seu OAuth Client ID para editar
3. Em **"Authorized redirect URIs"**, confirme que está lá:
   `https://SEU-APP.streamlit.app/oauth2callback`
4. Salve

---

## Parte 4 — (Opcional) Migração de dados do banco antigo

Se você ainda tiver acesso ao banco de dados antigo (Neon da outra pessoa):

### Opção A — Via Neon Console (mais simples)
1. No banco **antigo**, vá em **Tables** → exporte cada tabela como CSV
2. No banco **novo**, vá em **Tables** → faça o import de cada CSV

### Opção B — Via pg_dump (linha de comando)
```bash
# Exportar do banco antigo
pg_dump "postgresql://OLD_USER:OLD_PASS@OLD_HOST/neondb?sslmode=require" > backup.sql

# Importar no banco novo
psql "postgresql://NEW_USER:NEW_PASS@NEW_HOST/neondb?sslmode=require" < backup.sql
```

> Se você não tem mais acesso ao banco antigo, as tabelas serão criadas vazias automaticamente.
> As **notícias** ficam no arquivo `resumos.csv` e podem ser reinseridas via `upload_news.py`.

---

## Checklist final

- [ ] Conta criada no Neon
- [ ] Projeto criado (região São Paulo)
- [ ] Connection string copiada para `secrets.toml`
- [ ] Projeto criado no Google Cloud Console
- [ ] OAuth consent screen configurado
- [ ] OAuth Client ID criado
- [ ] Redirect URIs adicionados (local + produção)
- [ ] Client ID e Client Secret copiados para `secrets.toml`
- [ ] Secrets configurados no painel do Streamlit Cloud
- [ ] App testado localmente (`streamlit run app.py`)
- [ ] App testado em produção
