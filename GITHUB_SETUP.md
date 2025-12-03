# 🔧 Configuração do GitHub
## Sistema Operacional Bom Jesus

**Status**: ✅ **Código enviado para o GitHub**

---

## 📦 O Que Foi Enviado

### ✅ Estrutura Completa
- ✅ Backend FastAPI completo
- ✅ Frontend Next.js completo
- ✅ Configuração Docker (dev e prod)
- ✅ Nginx reverse proxy
- ✅ GitHub Actions workflow
- ✅ Documentação completa
- ✅ Scripts automatizados

### ✅ Arquivos de Configuração
- ✅ `docker-compose.yml` - Desenvolvimento
- ✅ `docker-compose.prod.yml` - Produção
- ✅ `Dockerfile.backend` - Backend otimizado
- ✅ `Dockerfile.frontend` - Frontend otimizado
- ✅ `.github/workflows/deploy.yml` - CI/CD

### ✅ Documentação
- ✅ `PRIMEIRO_DEPLOY.md` - Guia de deploy
- ✅ `DEPLOY.md` - Documentação geral
- ✅ `DOCKER_GUIDE.md` - Guia Docker
- ✅ `DATABASE.md` - Documentação do banco
- ✅ `README.md` - Documentação principal

---

## 🔐 Próximos Passos: Configurar Secrets

Para ativar o deploy automatizado, configure os secrets no GitHub:

### 1. Acesse as Configurações

1. Vá para: https://github.com/JhusNeto/bom_jesus
2. Clique em: **Settings**
3. No menu lateral: **Secrets and variables** → **Actions**
4. Clique em: **New repository secret**

### 2. Adicione os Secrets

#### Docker Hub
```
Nome: DOCKER_USERNAME
Valor: seu-usuario-docker-hub
```

```
Nome: DOCKER_PASSWORD
Valor: seu-token-docker-hub (não a senha!)
```

**Como obter token Docker Hub:**
1. Acesse: https://hub.docker.com/settings/security
2. Clique em "New Access Token"
3. Copie o token gerado

#### VPS (Quando tiver servidor)
```
Nome: VPS_HOST
Valor: IP ou domínio da VPS (ex: 192.168.1.100 ou servidor.com)
```

```
Nome: VPS_USER
Valor: usuário SSH (ex: root ou ubuntu)
```

```
Nome: SSH_PRIVATE_KEY
Valor: chave privada SSH completa (gerar com: ssh-keygen -t ed25519)
```

```
Nome: VPS_DOMAIN
Valor: domínio do site (ex: https://app.bomjesus.com)
```

#### Aplicação
```
Nome: NEXT_PUBLIC_API_URL
Valor: URL da API em produção (ex: https://api.bomjesus.com)
```

```
Nome: DOCKER_REGISTRY
Valor: bomjesus (ou seu registry)
```

---

## 🚀 Como Funciona o Deploy Automatizado

### Trigger
O deploy é acionado automaticamente quando você faz push para a branch `main`.

### Processo
1. ✅ **Build** - GitHub Actions builda as imagens Docker
2. ✅ **Push** - Imagens são enviadas para Docker Hub
3. ✅ **Deploy** - SSH na VPS e atualiza os serviços
4. ✅ **Health Check** - Verifica se tudo está funcionando

### Acompanhar Deploy
1. Vá para: https://github.com/JhusNeto/bom_jesus/actions
2. Veja o workflow "Deploy to Production"
3. Clique para ver detalhes

---

## 📋 Checklist de Configuração

### Antes do Primeiro Deploy Automatizado

- [ ] Docker Hub configurado
- [ ] Secrets do Docker Hub adicionados
- [ ] VPS configurada (quando tiver)
- [ ] Secrets da VPS adicionados
- [ ] Chave SSH configurada
- [ ] Domínio configurado (opcional)

---

## 🔍 Verificar Configuração

### Verificar Secrets
1. GitHub → Settings → Secrets and variables → Actions
2. Verifique se todos os secrets estão configurados

### Testar Workflow
1. Faça uma pequena alteração
2. Commit e push
3. Veja o workflow executar em: Actions

---

## 📚 Links Úteis

- **Repositório**: https://github.com/JhusNeto/bom_jesus
- **Actions**: https://github.com/JhusNeto/bom_jesus/actions
- **Settings**: https://github.com/JhusNeto/bom_jesus/settings
- **Secrets**: https://github.com/JhusNeto/bom_jesus/settings/secrets/actions

---

## ✅ Status Atual

- ✅ Código enviado para GitHub
- ✅ GitHub Actions workflow configurado
- ⏳ Secrets precisam ser configurados (quando tiver VPS)
- ⏳ Deploy automatizado ativado (após configurar secrets)

---

**Próximo passo**: Configure os secrets quando tiver uma VPS para fazer deploy em produção!

