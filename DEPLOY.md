# 🚀 Guia de Deploy - Sistema Operacional Bom Jesus

## Visão Geral

Este guia explica como fazer deploy do Sistema Operacional Bom Jesus em diferentes ambientes.

---

## 📋 Índice

- [Ambiente de Desenvolvimento](#ambiente-de-desenvolvimento)
- [Ambiente de Produção](#ambiente-de-produção)
- [Deploy Automatizado](#deploy-automatizado)
- [Configuração da VPS](#configuração-da-vps)
- [Troubleshooting](#troubleshooting)

---

## 🛠️ Ambiente de Desenvolvimento

### Pré-requisitos

- Docker e Docker Compose instalados
- Git

### Setup Rápido

```bash
# 1. Clone o repositório
git clone <repo-url>
cd bom_jesus

# 2. Configure as variáveis de ambiente
cp env.example .env
# Edite o .env conforme necessário

# 3. Inicie os serviços
docker compose up -d

# 4. Verifique os serviços
docker compose ps
```

### Serviços Disponíveis

Após iniciar, você terá:

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5433
- **Redis**: localhost:6379
- **PGAdmin** (opcional): http://localhost:5050

Para iniciar com PGAdmin:

```bash
docker compose --profile tools up -d
```

### Hot Reload

**Backend**:
- Volumes mapeados: `./app:/app/app`
- Comando: `--reload` ativo
- Alterações no código são refletidas automaticamente

**Frontend**:
- Volumes mapeados: `./frontend:/app`
- Comando: `npm run dev`
- Alterações são refletidas automaticamente

### Comandos Úteis

```bash
# Ver logs
docker compose logs -f api-service
docker compose logs -f frontend-service

# Parar serviços
docker compose down

# Parar e limpar volumes
docker compose down -v

# Rebuild
docker compose build --no-cache
docker compose up -d
```

---

## 🌐 Ambiente de Produção

### Pré-requisitos na VPS

- Ubuntu 22.04 LTS (ou similar)
- Docker e Docker Compose instalados
- Nginx instalado
- Certbot (Let's Encrypt)
- Firewall configurado

### Setup Inicial da VPS

#### 1. Instalar Docker

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

#### 2. Instalar Nginx e Certbot

```bash
sudo apt install nginx certbot python3-certbot-nginx -y
```

#### 3. Configurar Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

#### 4. Preparar Estrutura

```bash
mkdir -p ~/bom_jesus
cd ~/bom_jesus
```

### Deploy Manual

#### 1. Copiar Arquivos

```bash
# Na sua máquina local
scp docker-compose.prod.yml user@vps:~/bom_jesus/
scp -r nginx/ user@vps:~/bom_jesus/
```

#### 2. Configurar Variáveis de Ambiente

Na VPS, crie `~/bom_jesus/.env.prod`:

```env
# Database
POSTGRES_USER=bomjesus
POSTGRES_PASSWORD=<senha-forte>
POSTGRES_DB=bom_jesus_db

# Redis
REDIS_PASSWORD=<senha-forte>

# App
SECRET_KEY=<chave-secreta-forte>
NEXT_PUBLIC_API_URL=https://seu-dominio.com

# Docker
DOCKER_REGISTRY=bomjesus
IMAGE_TAG=latest
```

#### 3. Configurar Nginx

```bash
# Copiar configuração
sudo cp ~/bom_jesus/nginx/nginx.conf /etc/nginx/sites-available/bom_jesus
sudo ln -s /etc/nginx/sites-available/bom_jesus /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Configurar SSL (Let's Encrypt)
sudo certbot --nginx -d seu-dominio.com

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

#### 4. Iniciar Serviços

```bash
cd ~/bom_jesus
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

#### 5. Verificar

```bash
# Status dos containers
docker compose -f docker-compose.prod.yml ps

# Logs
docker compose -f docker-compose.prod.yml logs -f

# Health check
curl https://seu-dominio.com/api/v1/health
```

---

## 🤖 Deploy Automatizado

### GitHub Actions

O deploy automatizado é configurado via GitHub Actions. Quando você faz push para `main`, o workflow:

1. ✅ Build das imagens Docker
2. ✅ Push para Docker Hub
3. ✅ SSH na VPS
4. ✅ Pull das imagens
5. ✅ Restart dos serviços
6. ✅ Health check

### Configurar Secrets no GitHub

No repositório GitHub, adicione os seguintes secrets:

#### Docker Hub
- `DOCKER_USERNAME` - Seu usuário Docker Hub
- `DOCKER_PASSWORD` - Seu token Docker Hub

#### VPS
- `VPS_HOST` - IP ou domínio da VPS
- `VPS_USER` - Usuário SSH
- `SSH_PRIVATE_KEY` - Chave privada SSH
- `VPS_DOMAIN` - Domínio do site

#### Aplicação
- `NEXT_PUBLIC_API_URL` - URL da API em produção
- `DOCKER_REGISTRY` - Registry Docker (opcional)

### Como Adicionar Secrets

1. Vá em: Repositório → Settings → Secrets and variables → Actions
2. Clique em "New repository secret"
3. Adicione cada secret acima

### Deploy

Após configurar os secrets, o deploy é automático:

```bash
git add .
git commit -m "Deploy: descrição"
git push origin main
```

O workflow será executado automaticamente. Você pode acompanhar em:
- GitHub → Actions → Deploy to Production

---

## 🔧 Configuração da VPS

### Estrutura de Diretórios

```
~/bom_jesus/
├── docker-compose.prod.yml
├── .env.prod
├── nginx/
│   └── nginx.conf
└── logs/
    ├── backend/
    └── nginx/
```

### Firewall da VPS

O banco de dados deve estar protegido:

```bash
# Bloquear acesso externo ao PostgreSQL
sudo ufw deny 5432

# Permitir apenas acesso interno
# O PostgreSQL só é acessível pela rede Docker
```

### Backup do Banco

Configure backup automático:

```bash
# Criar script de backup
cat > ~/bom_jesus/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker compose -f docker-compose.prod.yml exec -T db-service \
  pg_dump -U bomjesus bom_jesus_db | gzip > $BACKUP_DIR/backup_$DATE.sql.gz
# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
EOF

chmod +x ~/bom_jesus/backup-db.sh

# Adicionar ao crontab (backup diário às 2h)
(crontab -l 2>/dev/null; echo "0 2 * * * ~/bom_jesus/backup-db.sh") | crontab -
```

---

## 📊 Monitoramento

### Uptime Kuma (Recomendado)

Para monitorar o sistema:

```yaml
# Adicionar ao docker-compose.prod.yml
uptime-kuma:
  image: louislam/uptime-kuma:latest
  container_name: bom_jesus_uptime
  volumes:
    - uptime_kuma_data:/app/data
  ports:
    - "3001:3001"
  networks:
    - bomjesus-net
  restart: always
```

### Logs Estruturados

Os logs estão configurados em JSON:

```bash
# Ver logs do backend
docker compose -f docker-compose.prod.yml logs backend | jq

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔒 Segurança

### Checklist de Produção

- [ ] ✅ Credenciais fortes em `.env.prod`
- [ ] ✅ SSL/HTTPS configurado (Let's Encrypt)
- [ ] ✅ Firewall ativo (apenas portas necessárias)
- [ ] ✅ Banco de dados não acessível externamente
- [ ] ✅ Secrets no GitHub Actions configurados
- [ ] ✅ Backup automático configurado
- [ ] ✅ Logs estruturados ativos
- [ ] ✅ Health checks configurados
- [ ] ✅ Restart policies configuradas

---

## 🆘 Troubleshooting

### Problema: Containers não iniciam

```bash
# Ver logs
docker compose -f docker-compose.prod.yml logs

# Verificar dependências
docker compose -f docker-compose.prod.yml ps

# Verificar health checks
docker compose -f docker-compose.prod.yml ps | grep unhealthy
```

### Problema: Backend não conecta ao banco

```bash
# Verificar se banco está saudável
docker compose -f docker-compose.prod.yml exec db-service pg_isready -U postgres

# Testar conexão do backend
docker compose -f docker-compose.prod.yml exec api-service python -c "from app.db.session import engine; engine.connect()"
```

### Problema: Nginx não funciona

```bash
# Testar configuração
sudo nginx -t

# Ver logs
sudo tail -f /var/log/nginx/error.log

# Verificar se containers estão acessíveis
docker compose -f docker-compose.prod.yml exec nginx ping api-service
```

### Problema: SSL não funciona

```bash
# Renovar certificado
sudo certbot renew

# Testar renovação
sudo certbot renew --dry-run

# Verificar certificado
sudo certbot certificates
```

---

## 📚 Referências

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Versão**: 1.0.0  
**Última atualização**: 2024

