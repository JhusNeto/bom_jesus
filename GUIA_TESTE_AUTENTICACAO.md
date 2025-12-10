# 🧪 Guia de Teste - Autenticação no Navegador

## 📋 Pré-requisitos

1. **Serviços rodando:**
   ```bash
   docker compose ps
   ```
   Deve mostrar:
   - ✅ `bom_jesus_backend` ou `bom_jesus_backend_dev` (Up)
   - ✅ `bom_jesus_db` (healthy)
   - ✅ `bom_jesus_redis` (healthy)
   - ✅ `bom_jesus_frontend` (se estiver rodando)

2. **Usuário de teste criado:**
   ```bash
   docker exec bom_jesus_db psql -U postgres -d bom_jesus_db -c "SELECT email, name, role FROM users WHERE email = 'admin@bomjesus.com';"
   ```

---

## 🚀 Passo a Passo - Teste no Navegador

### 1. Verificar se os Serviços Estão Rodando

**Backend:**
```bash
curl http://localhost:8000/api/v1/health
```

**Frontend (se estiver rodando):**
```bash
curl http://localhost:3000
```

---

### 2. Criar Usuário de Teste (se não existir)

**Opção A: Via Script Python**
```bash
docker exec bom_jesus_backend_dev python3 scripts/create-test-user.py
```

**Opção B: Direto no Banco**
```bash
docker exec bom_jesus_db psql -U postgres -d bom_jesus_db << 'EOF'
INSERT INTO users (id, name, email, hashed_password, role, is_active, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    'Administrador',
    'admin@bomjesus.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJqJqJqJq',
    'ADMIN'::userrole,
    'Y',
    NOW(),
    NOW()
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'admin@bomjesus.com');
EOF
```

**Credenciais de Teste:**
- **Email:** `admin@bomjesus.com`
- **Senha:** `admin123`

---

### 3. Acessar o Frontend

1. **Abra o navegador** e acesse:
   ```
   http://localhost:3000
   ```

2. **Você será redirecionado para:**
   ```
   http://localhost:3000/login
   ```

---

### 4. Teste de Login

#### ✅ Teste 1: Login Válido

1. Na tela de login, preencha:
   - **Email:** `admin@bomjesus.com`
   - **Senha:** `admin123`

2. Clique em **"Entrar"**

3. **Resultado esperado:**
   - ✅ Redirecionamento para `/dashboard`
   - ✅ Header mostra: "Administrador" (nome do usuário)
   - ✅ Badge com role: "ADMIN"
   - ✅ Botão "Sair" visível

#### ❌ Teste 2: Login Inválido

1. Tente fazer login com:
   - **Email:** `teste@teste.com`
   - **Senha:** `senhaerrada`

2. **Resultado esperado:**
   - ❌ Mensagem de erro: "Email ou senha incorretos"
   - ❌ Permanece na tela de login

---

### 5. Verificar Tokens no LocalStorage

1. **Abra o DevTools** (F12 ou Cmd+Option+I)

2. Vá para a aba **"Application"** (Chrome) ou **"Storage"** (Firefox)

3. No menu lateral, clique em **"Local Storage"** → `http://localhost:3000`

4. **Verifique se existem:**
   - ✅ `access_token` - Token JWT (começa com `eyJ...`)
   - ✅ `refresh_token` - Token de refresh (começa com `eyJ...`)
   - ✅ `auth-storage` - Dados do Zustand (JSON com `user` e `isAuthenticated`)

---

### 6. Teste de Proteção de Rotas

#### ✅ Teste 3: Acessar Dashboard Autenticado

1. Com o usuário logado, acesse:
   ```
   http://localhost:3000/dashboard
   ```

2. **Resultado esperado:**
   - ✅ Dashboard carrega normalmente
   - ✅ Nome do usuário aparece no header

#### ❌ Teste 4: Acessar Dashboard Sem Login

1. **Limpe o localStorage:**
   - No DevTools → Application → Local Storage
   - Clique com botão direito → "Clear"

2. Ou faça logout clicando em **"Sair"**

3. Tente acessar diretamente:
   ```
   http://localhost:3000/dashboard
   ```

4. **Resultado esperado:**
   - ✅ Redirecionamento automático para `/login`
   - ✅ Não consegue acessar o dashboard

---

### 7. Teste de Refresh Automático

#### ✅ Teste 5: Refresh Token Automático

**Preparação:**
1. Faça login normalmente
2. Abra o DevTools → Network
3. Aguarde 10 minutos (ou altere `ACCESS_TOKEN_EXPIRE_MINUTES=1` no `.env` para teste rápido)

**Teste:**
1. Faça uma requisição qualquer (ex: recarregue a página)
2. **Resultado esperado:**
   - ✅ Interceptor detecta 401
   - ✅ Chama `/auth/refresh` automaticamente
   - ✅ Obtém novo `access_token`
   - ✅ Retenta a requisição original
   - ✅ Tudo funciona normalmente (usuário não percebe)

**Verificar no Network:**
- Deve aparecer uma requisição `POST /api/v1/auth/refresh`
- Status: `200 OK`
- Response contém novo `access_token`

---

### 8. Teste de Logout

#### ✅ Teste 6: Logout Completo

1. Com o usuário logado, clique em **"Sair"** no header

2. **Resultado esperado:**
   - ✅ Redirecionamento para `/login`
   - ✅ LocalStorage limpo (sem tokens)
   - ✅ Estado do Zustand resetado

3. **Verificar no DevTools:**
   - LocalStorage não deve ter `access_token`, `refresh_token` ou `auth-storage`

4. **Tentar acessar `/dashboard` novamente:**
   - ✅ Deve redirecionar para `/login`

---

### 9. Verificar no Backend (Swagger)

1. **Acesse a documentação:**
   ```
   http://localhost:8000/docs
   ```

2. **Teste o endpoint de login:**
   - Clique em `POST /api/v1/auth/login`
   - Clique em "Try it out"
   - Preencha:
     ```json
     {
       "email": "admin@bomjesus.com",
       "password": "admin123"
     }
     ```
   - Clique em "Execute"

3. **Resultado esperado:**
   - ✅ Status: `200 OK`
   - ✅ Response contém:
     - `access_token`
     - `refresh_token`
     - `user` (com id, email, name, role)

4. **Teste o endpoint `/auth/me`:**
   - Clique em `GET /api/v1/auth/me`
   - Clique em "Authorize" (canto superior direito)
   - Cole o `access_token` do login anterior
   - Clique em "Try it out" → "Execute"
   - **Resultado esperado:**
     - ✅ Status: `200 OK`
     - ✅ Retorna dados do usuário

---

## 🔍 Verificações no Console do Navegador

### Console do Navegador (F12)

**Durante o Login:**
- Não deve aparecer erros
- Pode aparecer logs de debug (se `DEBUG=True`)

**Após Login:**
- Verificar se há requisições para `/api/v1/auth/login`
- Status: `200 OK`

**Durante Refresh:**
- Pode aparecer requisição para `/api/v1/auth/refresh`
- Status: `200 OK`

**Após Logout:**
- Não deve aparecer erros
- LocalStorage limpo

---

## 🐛 Troubleshooting

### Problema: "Email ou senha incorretos"

**Solução:**
1. Verifique se o usuário existe:
   ```bash
   docker exec bom_jesus_db psql -U postgres -d bom_jesus_db -c "SELECT email, name FROM users;"
   ```

2. Se não existir, crie o usuário (veja passo 2)

3. Verifique se a senha está correta (deve ser `admin123`)

---

### Problema: "Backend não está respondendo"

**Solução:**
1. Verifique se o container está rodando:
   ```bash
   docker ps | grep backend
   ```

2. Verifique os logs:
   ```bash
   docker logs bom_jesus_backend --tail 50
   ```

3. Reinicie o backend:
   ```bash
   docker compose restart api-service
   ```

---

### Problema: "Refresh token não funciona"

**Solução:**
1. Verifique se o Redis está rodando:
   ```bash
   docker exec bom_jesus_redis redis-cli ping
   ```
   Deve retornar: `PONG`

2. Verifique a conexão Redis no backend:
   ```bash
   docker logs bom_jesus_backend | grep -i redis
   ```

---

### Problema: "Redirecionamento não funciona"

**Solução:**
1. Limpe o cache do navegador
2. Limpe o LocalStorage manualmente
3. Recarregue a página (Ctrl+Shift+R ou Cmd+Shift+R)

---

## 📊 Checklist de Testes

- [ ] Login com credenciais válidas funciona
- [ ] Login com credenciais inválidas mostra erro
- [ ] Tokens são salvos no LocalStorage
- [ ] Dashboard é acessível após login
- [ ] Dashboard redireciona para login se não autenticado
- [ ] Nome do usuário aparece no header
- [ ] Role do usuário aparece no header
- [ ] Logout funciona e limpa tokens
- [ ] Refresh automático funciona (teste após 10 min ou com token de 1 min)
- [ ] Endpoint `/auth/me` retorna dados do usuário
- [ ] Swagger UI funciona e endpoints estão documentados

---

## 🎯 Resultado Esperado Final

Após todos os testes, você deve ter:

1. ✅ **Login funcionando** - Redireciona para dashboard
2. ✅ **Proteção de rotas** - Redireciona se não autenticado
3. ✅ **Header com usuário** - Mostra nome e role
4. ✅ **Logout funcionando** - Limpa tokens e redireciona
5. ✅ **Refresh automático** - Funciona sem o usuário perceber
6. ✅ **Tokens no LocalStorage** - `access_token` e `refresh_token` salvos

---

**Última atualização:** 2025-12-03

