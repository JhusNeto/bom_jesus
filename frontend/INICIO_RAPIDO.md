# 🚀 Início Rápido - Frontend

## Instalação e Execução em 3 Passos

### 1. Instalar Dependências
```bash
cd frontend
npm install
```

### 2. Configurar Ambiente
```bash
cp env.example .env
# Edite .env e configure NEXT_PUBLIC_API_URL se necessário
```

### 3. Executar
```bash
npm run dev
```

A aplicação estará em: **http://localhost:3000**

## 🎯 O que você verá

1. **Tela de Login** (`/login`)
   - Use qualquer email e senha (mockado por enquanto)
   - Após login, será redirecionado para o dashboard

2. **Dashboard** (`/dashboard`)
   - Página principal após autenticação
   - Exemplo de chamada à API
   - Cards de módulos futuros

## 📝 Credenciais de Teste

Por enquanto, qualquer email/senha funciona (autenticação mockada).

Exemplo:
- Email: `teste@exemplo.com`
- Senha: `qualquercoisa`

## 🔧 Comandos Úteis

```bash
# Desenvolvimento
npm run dev

# Build para produção
npm run build

# Executar produção
npm start

# Verificar tipos
npm run type-check

# Formatar código
npm run format

# Linting
npm run lint
```

## 🐛 Problemas Comuns

### Erro ao instalar dependências
```bash
# Limpar cache e reinstalar
rm -rf node_modules package-lock.json
npm install
```

### Porta 3000 já em uso
```bash
# Use outra porta
PORT=3001 npm run dev
```

### Erro de conexão com API
Verifique se o backend está rodando em `http://localhost:8000`

Ajuste em `.env`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📚 Próximos Passos

1. ✅ Teste o login e dashboard
2. ✅ Verifique integração com backend
3. ✅ Explore os componentes em `/components/ui`
4. ✅ Consulte `README.md` para documentação completa

---

**Precisa de ajuda?** Consulte `README.md` para documentação detalhada.

