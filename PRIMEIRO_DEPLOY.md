# 🚀 Guia do Primeiro Deploy
## Sistema Operacional Bom Jesus

Este guia vai te levar passo a passo através do seu primeiro deploy!

---

## 📋 Escolha seu Tipo de Deploy

### Opção 1: Deploy Local (Teste) ✅ **RECOMENDADO PARA PRIMEIRO DEPLOY**
- Testa tudo localmente primeiro
- Não precisa de VPS
- Perfeito para validar antes de produção

### Opção 2: Deploy em Produção (VPS Real)
- Deploy real em servidor
- Precisa de VPS configurada
- Deploy automatizado via GitHub Actions

---

## 🎯 Opção 1: Deploy Local (Teste)

### Passo 1: Build das Imagens Docker

```bash
# Build da imagem do backend
docker build -f Dockerfile.backend -t bomjesus/backend:latest .

# Build da imagem do frontend
cd frontend
docker build -f Dockerfile.frontend -t bomjesus/frontend:latest .
cd ..
```

### Passo 2: Configurar Variáveis de Produção

```bash
# Copiar exemplo
cp env.prod.example .env.prod

# Editar com valores reais (ou usar os defaults para teste)
nano .env.prod
```

**Valores mínimos para teste local:**
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_DB=bom_jesus_db
SECRET_KEY=dev-secret-key-change-in-production
REDIS_PASSWORD=redis123
NEXT_PUBLIC_API_URL=http://localhost:8000
DOCKER_REGISTRY=bomjesus
IMAGE_TAG=latest
```

### Passo 3: Subir os Serviços

```bash
# Usar docker-compose de produção (com imagens locais)
docker compose -f docker-compose.prod.yml up -d

# Ver status
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

### Passo 4: Verificar Deploy

```bash
# Health check
curl http://localhost:8000/api/v1/health

# DB health check
curl http://localhost:8000/api/v1/db/health

# Frontend (se configurado)
curl http://localhost:3000
```

✅ **Deploy Local Concluído!**

---

## 🌐 Opção 2: Deploy em Produção (VPS)

### Pré-requisitos

- [ ] VPS configurada (Ubuntu 22.04+)
- [ ] Docker e Docker Compose instalados
- [ ] Acesso SSH configurado
- [ ] Domínio apontando para a VPS (opcional, para HTTPS)

### Passo 1: Build e Push das Imagens para Docker Hub

#### 1.1. Criar conta no Docker Hub (se não tiver)

1. Acesse: https://hub.docker.com
2. Crie uma conta
3. Crie um repositório público ou privado:
   - `bomjesus/backend`
   - `bomjesus/frontend`

#### 1.2. Login no Docker Hub

```bash
docker login
# Digite seu username e password
```

#### 1.3. Build e Push das Imagens

Use o script automatizado:

```bash
# Executar script de build e push
./scripts/build-and-push.sh
```

Ou manualmente:

```bash
# Build e push do backend
docker build -f Dockerfile.backend -t bomjesus/backend:latest .
docker push bomjesus/backend:latest

# Build e push do frontend
cd frontend
docker build -f Dockerfile.frontend -t bomjesus/frontend:latest .
docker push bomjesus/frontend:latest
cd ..
```

### Passo 2: Configurar VPS

#### 2.1. Conectar na VPS

```bash
ssh usuario@seu-servidor.com
```

#### 2.2. Instalar Docker (se não tiver)

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
```

#### 2.3. Criar Estrutura de Diretórios

```bash
mkdir -p ~/bom_jesus
cd ~/bom_jesus
```

### Passo 3: Copiar Arquivos para VPS

#### 3.1. Copiar docker-compose.prod.yml

Na sua máquina local:

```bash
scp docker-compose.prod.yml usuario@seu-servidor.com:~/bom_jesus/
```

#### 3.2. Copiar configuração Nginx

```bash
scp -r nginx/ usuario@seu-servidor.com:~/bom_jesus/
```

#### 3.3. Criar .env.prod na VPS

Na VPS:

```bash
cd ~/bom_jesus
nano .env.prod
```

Cole o conteúdo (com valores reais):

```env
POSTGRES_USER=bomjesus
POSTGRES_PASSWORD=<senha-forte>
POSTGRES_DB=bom_jesus_db
SECRET_KEY=<chave-secreta-forte>
REDIS_PASSWORD=<senha-redis-forte>
NEXT_PUBLIC_API_URL=https://seu-dominio.com
DOCKER_REGISTRY=bomjesus
IMAGE_TAG=latest
```

**⚠️ IMPORTANTE**: Use senhas fortes em produção!

### Passo 4: Deploy na VPS

Na VPS:

```bash
cd ~/bom_jesus

# Fazer login no Docker Hub
docker login

# Pull das imagens
docker compose -f docker-compose.prod.yml pull

# Subir serviços
docker compose -f docker-compose.prod.yml up -d

# Ver status
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

### Passo 5: Configurar Nginx (Se tiver domínio)

```bash
# Copiar configuração
sudo cp ~/bom_jesus/nginx/nginx.conf /etc/nginx/sites-available/bom_jesus

# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/bom_jesus /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Instalar Certbot (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx -y

# Configurar SSL
sudo certbot --nginx -d seu-dominio.com

# Reiniciar Nginx
sudo systemctl restart nginx
```

### Passo 6: Verificar Deploy

```bash
# Health check (via IP ou domínio)
curl http://seu-servidor.com/api/v1/health

# Ou via domínio com HTTPS
curl https://seu-dominio.com/api/v1/health
```

✅ **Deploy em Produção Concluído!**

---

## 🤖 Opção 3: Deploy Automatizado (GitHub Actions)

### Passo 1: Configurar Secrets no GitHub

1. Acesse: Repositório → Settings → Secrets and variables → Actions
2. Clique em "New repository secret"
3. Adicione os seguintes secrets:

#### Docker Hub
- `DOCKER_USERNAME` - Seu usuário Docker Hub
- `DOCKER_PASSWORD` - Seu token Docker Hub (não a senha!)

#### VPS
- `VPS_HOST` - IP ou domínio da VPS (ex: `192.168.1.100` ou `servidor.com`)
- `VPS_USER` - Usuário SSH (ex: `root` ou `ubuntu`)
- `SSH_PRIVATE_KEY` - Chave privada SSH completa
- `VPS_DOMAIN` - Domínio do site (ex: `https://app.bomjesus.com`)

#### Aplicação
- `NEXT_PUBLIC_API_URL` - URL da API (ex: `https://api.bomjesus.com`)
- `DOCKER_REGISTRY` - Registry Docker (ex: `bomjesus`)

### Passo 2: Gerar Chave SSH (se não tiver)

Na sua máquina:

```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_actions

# Copiar chave pública para VPS
ssh-copy-id -i ~/.ssh/github_actions.pub usuario@seu-servidor.com

# Copiar chave privada para GitHub Secrets
cat ~/.ssh/github_actions
# Copie TODO o conteúdo e cole no secret SSH_PRIVATE_KEY
```

### Passo 3: Fazer Push para Main

```bash
git add .
git commit -m "Deploy: primeiro deploy automatizado"
git push origin main
```

### Passo 4: Acompanhar Deploy

1. Acesse: GitHub → Actions
2. Veja o workflow "Deploy to Production" executando
3. Aguarde a conclusão

✅ **Deploy Automatizado Ativado!**

Agora, sempre que você fizer push para `main`, o deploy será automático!

---

## 📋 Checklist de Deploy

Use este checklist para garantir que tudo está configurado:

### Antes do Deploy
- [ ] Docker instalado localmente
- [ ] Docker Hub configurado (para produção)
- [ ] Variáveis de ambiente configuradas
- [ ] Imagens Docker buildadas

### Deploy Local
- [ ] Imagens buildadas localmente
- [ ] `.env.prod` configurado
- [ ] Serviços subindo com `docker-compose.prod.yml`
- [ ] Health checks passando
- [ ] Endpoints respondendo

### Deploy em Produção
- [ ] VPS configurada
- [ ] Docker instalado na VPS
- [ ] Imagens no Docker Hub
- [ ] Arquivos copiados para VPS
- [ ] `.env.prod` configurado na VPS
- [ ] Serviços rodando na VPS
- [ ] Nginx configurado (se tiver domínio)
- [ ] SSL configurado (se tiver domínio)

### Deploy Automatizado
- [ ] Secrets configurados no GitHub
- [ ] Chave SSH configurada
- [ ] Workflow funcionando
- [ ] Deploy automático testado

---

## 🆘 Troubleshooting

### Problema: Imagem não sobe no Docker Hub

**Solução**:
```bash
# Verificar login
docker login

# Verificar tags
docker images | grep bomjesus

# Tentar push novamente
docker push bomjesus/backend:latest
```

### Problema: Serviços não iniciam na VPS

**Solução**:
```bash
# Ver logs
docker compose -f docker-compose.prod.yml logs

# Verificar variáveis de ambiente
docker compose -f docker-compose.prod.yml config

# Verificar se imagens foram baixadas
docker images
```

### Problema: Health check falhando

**Solução**:
```bash
# Ver logs do serviço específico
docker compose -f docker-compose.prod.yml logs api-service

# Verificar conectividade
docker compose -f docker-compose.prod.yml exec api-service ping db-service
```

---

## 📚 Próximos Passos

Após o primeiro deploy:

1. ✅ Configurar backup automático do banco
2. ✅ Configurar monitoramento (Uptime Kuma)
3. ✅ Configurar logs centralizados
4. ✅ Configurar alertas
5. ✅ Documentar processos de rollback

---

**Boa sorte com seu primeiro deploy! 🚀**

