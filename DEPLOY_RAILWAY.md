# Deploy para Railway - Guia Completo

## Por que Railway?
✅ Grátis (até $5/mês com free tier)  
✅ Conecta direto com GitHub  
✅ Deployment automático em cada push  
✅ Suporta Flask + PostgreSQL  
✅ OAuth redirect URIs funcionam perfeitamente  

---

## Step 1: Preparar Repositório GitHub

```bash
cd C:\AppsProjects\MyApps\album-builder

# Inicializar git (se não tiver)
git init

# Adicionar files
git add .
git commit -m "Initial commit: Family Album Builder"

# Criar repo no GitHub (https://github.com/new)
# Então:
git remote add origin https://github.com/SEU_USER/album-builder.git
git branch -M main
git push -u origin main
```

---

## Step 2: Criar `Procfile` (Railway precisa disso)

Cria arquivo `Procfile` na raiz do projeto:

```
web: python main.py
```

---

## Step 3: Atualizar `main.py` para Production

Railway passa a porta via variável de ambiente. Atualiza o main.py:

```python
#!/usr/bin/env python3
import sys
import os
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5050))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("=" * 60)
    print("Family Album Builder")
    print("=" * 60)
    print(f"\nServer running at port {port}")
    print(f"Debug mode: {debug}\n")
    
    # Só abre browser em local development
    if port == 5050:
        webbrowser.open("http://localhost:5050")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=False
    )
```

---

## Step 4: Criar `.env.example` (Railway usará isso)

Arquivo `.env.example`:

```
FLASK_ENV=production
PORT=5000
GOOGLE_REDIRECT_URI=https://album-builder-prod.up.railway.app/callback
```

---

## Step 5: Cadastro no Railway

1. Vai para **https://railway.app**
2. Click "Start a New Project"
3. Click "Deploy from GitHub repo"
4. Conecta com GitHub
5. Seleciona o repo `album-builder`
6. Railway detecta Python automaticamente

---

## Step 6: Configurar Variáveis de Ambiente

No painel do Railway:

1. Click no projeto
2. Vai para **Variables**
3. Adiciona:

```
PORT=5000
FLASK_ENV=production
GOOGLE_REDIRECT_URI=https://seu-projeto.up.railway.app/callback
```

(Railway vai gerar um domínio tipo `album-builder-prod.up.railway.app`)

---

## Step 7: Atualizar Google OAuth

**⚠️ IMPORTANTE:** Voltar ao Google Cloud Console:

1. Vai para **https://console.cloud.google.com/apis/credentials**
2. Click no seu OAuth 2.0 Client ID
3. Adiciona Authorized redirect URIs:
   ```
   http://localhost:5050/callback
   https://seu-projeto.up.railway.app/callback
   ```
4. Save

---

## Step 8: Upload do `client_secret_*.json` 

Railway NÃO tem acesso a arquivos locais. Precisa fazer upload:

**Opção A (Recomendado):** Como variável de ambiente

```bash
# Na pasta do projeto, encode o client_secret:
$content = Get-Content "client_secret_2_415896127616-euoecu375g31a6ibs5pnherqc43bfron.apps.googleusercontent.com.json"
$base64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($content))
Write-Host $base64
```

Copia o output e adiciona no Railway Variables:
```
GOOGLE_CLIENT_SECRET_B64=<paste aqui>
```

Depois atualiza `auth.py`:

```python
import os
import base64
import json

CLIENT_SECRET_FILE = r"C:\AppsProjects\MyApps\album-builder\client_secret_2_415896127616-euoecu375g31a6ibs5pnherqc43bfron.apps.googleusercontent.com.json"

# Em produção, ler da variável
if 'GOOGLE_CLIENT_SECRET_B64' in os.environ:
    secret_data = base64.b64decode(os.environ['GOOGLE_CLIENT_SECRET_B64']).decode()
    CLIENT_SECRET_DATA = json.loads(secret_data)
```

**Opção B:** Criar via Railway's MySQL/Postgres (mais complexo)

---

## Step 9: Persistência de Dados (SQLite → PostgreSQL)

Railway não mantém arquivos locais. Precisa de database persistente.

**Adicionar PostgreSQL:**

1. No painel Railway: "Add" → "Provision PostgreSQL"
2. Railway cria automaticamente `DATABASE_URL` em Variables

Depois atualiza `photos_api.py` para usar PostgreSQL:

```python
import os
from sqlalchemy import create_engine

# Usar PostgreSQL se em produção
db_url = os.environ.get('DATABASE_URL', 'sqlite:///cache/media_items.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

engine = create_engine(db_url)
```

---

## Step 10: Deploy

Railway monitora seu GitHub. Cada push faz deploy automático:

```bash
git add .
git commit -m "Setup Railway deployment"
git push origin main
```

Acompanha no painel do Railway → Deployments

---

## Troubleshooting

### Erro: `ModuleNotFoundError`
- Railway instalou requirements.txt? Checa em "Build Logs"

### Erro: `PORT não definida`
- Adiciona `PORT=5000` em Variables

### Erro: Google OAuth redirect
- Checa se `GOOGLE_REDIRECT_URI` tá correto
- Adiciona no Google Cloud Console

### SQLite vazio em produção
- Sempre usar PostgreSQL em produção
- SQLite é só para local

---

## URLs importantes

- **App URL**: https://seu-projeto.up.railway.app
- **Admin Painel**: https://railway.app/dashboard
- **Logs**: Railway Painel → Deployments → View Logs

---

## Custo

- **Grátis**: $5/mês em credits
- **PostgreSQL**: $12/mês (extra)
- **Total**: ~$17/mês OU mais se usar os credits

💡 **Dica**: Fazer sync uma vez por semana via cron job (Railway suporta)

