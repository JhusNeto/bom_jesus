# 🐛 Problemas Mapeados - Sistema Operacional Bom Jesus

**Data do Teste:** 2025-12-06 17:25:44  
**Total de Testes:** 61  
**Taxa de Sucesso:** 78.7% (48 passaram, 10 falharam, 3 pulados)

---

## 📊 Resumo Executivo

### ✅ O Que Está Funcionando

- **Infraestrutura**: 10/10 testes passaram ✅
  - Docker rodando
  - Todos os containers healthy
  - Portas abertas

- **API Básica**: 7/7 testes passaram ✅
  - Endpoints básicos funcionando
  - Health checks OK
  - Swagger/ReDoc acessíveis

- **Redis**: 8/8 testes passaram ✅
  - Conexão OK
  - Operações de refresh tokens funcionando

- **Banco de Dados (Parcial)**: 19/28 testes passaram
  - Conexão OK
  - Tabela `users` existe e está correta
  - Migrations aplicadas

---

## ❌ Problemas Críticos Encontrados

### 1. 🔴 CRÍTICO: Tabela `auth_tokens` Não Existe

**Problema:**
- Tabela `auth_tokens` não foi criada no banco de dados
- 9 testes falharam por causa disso

**Evidência:**
```
❌ Tabela 'auth_tokens' existe: Tabela 'auth_tokens' não encontrada
```

**Causa Provável:**
- A migration `432576a07748` não cria a tabela `auth_tokens`
- A migration anterior `701ea1d79e33` deveria ter criado, mas não foi aplicada ou foi substituída

**Impacto:**
- Sistema de autenticação não funciona completamente
- Refresh tokens não podem ser salvos no banco (apenas no Redis)
- Logout não funciona corretamente

**Solução:**
1. Verificar se a migration `701ea1d79e33` foi aplicada
2. Se não, aplicar: `alembic upgrade 701ea1d79e33`
3. Ou criar nova migration para criar a tabela `auth_tokens`

---

### 2. 🔴 CRÍTICO: Login Retorna 500 (Internal Server Error)

**Problema:**
- Endpoint `POST /api/v1/auth/login` retorna erro 500
- Erro: `LookupError: 'admin' is not among the defined enum values`

**Evidência:**
```
❌ POST /auth/login (credenciais válidas): Status esperado 200, recebido 500
```

**Causa:**
- Usuário no banco tem `role = 'admin'` (minúsculo)
- Enum espera `'ADMIN'` (maiúsculo)
- SQLAlchemy não consegue converter o valor

**Impacto:**
- Login não funciona
- Autenticação completamente quebrada
- Usuários não conseguem acessar o sistema

**Solução:**
1. Atualizar role do usuário no banco:
   ```sql
   UPDATE users SET role = 'ADMIN'::userrole WHERE email = 'admin@bomjesus.com';
   ```
2. Ou recriar usuário com role correto

---

### 3. 🟡 MÉDIO: Frontend Não Está Rodando

**Problema:**
- Container do frontend não está rodando
- Porta 3000 não responde
- 3 testes falharam

**Evidência:**
```
❌ Frontend está acessível: Não respondeu com HTTP 200/301/302
❌ Redirecionamento para login: Página não contém elementos de login
❌ Página /login acessível: Não respondeu com HTTP 200
```

**Causa:**
- Frontend não foi iniciado ou container parou

**Impacto:**
- Interface web não acessível
- Usuários não conseguem usar o sistema via navegador

**Solução:**
1. Iniciar frontend:
   ```bash
   docker compose up -d frontend-service
   ```
2. Ou iniciar manualmente:
   ```bash
   cd frontend && npm run dev
   ```

---

## 📋 Lista Completa de Problemas

### CRÍTICO (Prioridade 1)

1. ✅ **Tabela `auth_tokens` não existe** - 9 testes falharam
2. ✅ **Login retorna 500** - Erro de enum no role do usuário

### ALTO (Prioridade 2)

3. ✅ **Frontend não está rodando** - 3 testes falharam

### MÉDIO (Prioridade 3)

- Nenhum problema médio encontrado

### BAIXO (Prioridade 4)

- Nenhum problema baixo encontrado

---

## 🔧 Plano de Correção

### Passo 1: Corrigir Role do Usuário (URGENTE)

```sql
-- Conectar ao banco
docker exec -it bom_jesus_db psql -U postgres -d bom_jesus_db

-- Atualizar role
UPDATE users SET role = 'ADMIN'::userrole WHERE email = 'admin@bomjesus.com';

-- Verificar
SELECT email, role::text, is_active FROM users WHERE email = 'admin@bomjesus.com';
```

### Passo 2: Criar Tabela auth_tokens

**Opção A: Aplicar migration anterior**
```bash
docker compose exec api-service alembic upgrade 701ea1d79e33
```

**Opção B: Criar nova migration**
```bash
docker compose exec api-service alembic revision --autogenerate -m "Add auth_tokens table"
docker compose exec api-service alembic upgrade head
```

### Passo 3: Iniciar Frontend

```bash
docker compose up -d frontend-service
# ou
cd frontend && npm run dev
```

### Passo 4: Re-executar Testes

```bash
./scripts/test-suite.sh
```

---

## 📊 Estatísticas por Categoria

| Categoria | Total | Passaram | Falharam | Taxa |
|-----------|-------|----------|----------|------|
| Infraestrutura | 10 | 10 | 0 | 100% |
| API Básica | 7 | 7 | 0 | 100% |
| Autenticação | 8 | 4 | 1 | 50% |
| Banco de Dados | 28 | 19 | 9 | 68% |
| Redis | 8 | 8 | 0 | 100% |
| Frontend | 3 | 0 | 3 | 0% |
| **TOTAL** | **61** | **48** | **10** | **78.7%** |

---

## ✅ Próximos Passos

1. **Imediato**: Corrigir role do usuário no banco
2. **Imediato**: Criar/aplicar migration para tabela `auth_tokens`
3. **Imediato**: Iniciar frontend
4. **Após correções**: Re-executar testes
5. **Validação**: Verificar se todos os testes passam

---

**Relatório gerado automaticamente pela suite de testes**

