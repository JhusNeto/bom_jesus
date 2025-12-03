# Sistema Operacional Bom Jesus - Frontend

Frontend do Sistema Operacional Bom Jesus construído com **Next.js 15**, **React 19** e **TailwindCSS**.

## 📋 Índice

- [Stack Tecnológica](#stack-tecnológica)
- [Arquitetura](#arquitetura)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação e Execução](#instalação-e-execução)
- [Componentes Principais](#componentes-principais)
- [Desenvolvimento](#desenvolvimento)
- [Próximos Passos](#próximos-passos)

## 🚀 Stack Tecnológica

### Framework e Biblioteca
- **Next.js 15**: Framework React com App Router
- **React 19**: Biblioteca JavaScript para interfaces
- **TypeScript**: Tipagem estática

### Estilização
- **TailwindCSS**: Framework CSS utility-first
- **shadcn/ui**: Componentes UI baseados em Radix UI
- **Lucide React**: Ícones modernos

### Estado e Dados
- **Zustand**: Gerenciamento de estado global leve
- **TanStack Query**: Cache e sincronização de dados do servidor

### Ferramentas de Desenvolvimento
- **ESLint**: Linter para JavaScript/TypeScript
- **Prettier**: Formatador de código
- **TypeScript**: Tipagem estática

### Preparado para Futuro
- **Recharts**: Biblioteca de gráficos (pronto para uso)
- **PWA**: Estrutura preparada para Progressive Web App

## 🏗️ Arquitetura

### App Router (Next.js 15)

A aplicação utiliza o App Router do Next.js 15, organizando rotas através da estrutura de pastas:

```
app/
├── (public)/          # Rotas públicas
│   ├── layout.tsx    # Layout público
│   └── login/        # Página de login
├── (auth)/           # Rotas protegidas (requerem autenticação)
│   ├── layout.tsx    # Layout autenticado
│   └── dashboard/    # Dashboard principal
└── layout.tsx        # Layout root
```

### Camadas da Aplicação

```
┌─────────────────────────────────────┐
│      Pages/App Router               │  ← Rotas e páginas
├─────────────────────────────────────┤
│      Components (UI)                │  ← Componentes reutilizáveis
├─────────────────────────────────────┤
│      Features (Módulos)             │  ← Lógica de negócio por módulo
├─────────────────────────────────────┤
│      Services (API)                 │  ← Integração com backend
├─────────────────────────────────────┤
│      Store (Zustand)                │  ← Estado global
├─────────────────────────────────────┤
│      Hooks (Custom)                 │  ← Hooks reutilizáveis
└─────────────────────────────────────┘
```

## 📁 Estrutura do Projeto

```
frontend/
├── app/                          # App Router (Next.js 15)
│   ├── (auth)/                   # Rotas protegidas
│   │   ├── layout.tsx           # Layout autenticado
│   │   └── dashboard/           # Dashboard
│   ├── (public)/                 # Rotas públicas
│   │   ├── layout.tsx           # Layout público
│   │   └── login/               # Login
│   ├── globals.css              # Estilos globais
│   ├── layout.tsx               # Layout root
│   ├── page.tsx                 # Página inicial (redirect)
│   └── providers.tsx            # Providers (TanStack Query, etc)
├── components/                   # Componentes reutilizáveis
│   └── ui/                      # Componentes shadcn/ui
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       └── label.tsx
├── features/                     # Módulos por funcionalidade
│   └── .gitkeep                 # Estrutura preparada
├── hooks/                        # Custom hooks
│   └── use-api.ts               # Hook para chamadas API
├── lib/                          # Utilitários
│   └── utils.ts                 # Funções utilitárias
├── services/                     # Serviços de API
│   ├── api.ts                   # Cliente Axios configurado
│   └── auth.service.ts          # Serviço de autenticação
├── store/                        # Estado global (Zustand)
│   └── auth.store.ts            # Store de autenticação
├── types/                        # Tipos TypeScript
│   └── index.ts                 # Tipos principais
├── middleware.ts                 # Middleware de proteção de rotas
├── components.json               # Configuração shadcn/ui
├── next.config.ts               # Configuração Next.js
├── tailwind.config.ts           # Configuração TailwindCSS
├── tsconfig.json                # Configuração TypeScript
├── package.json                 # Dependências
└── README.md                    # Esta documentação
```

## 🚀 Instalação e Execução

### Pré-requisitos

- Node.js 20+
- npm ou yarn
- Backend rodando (ver [README do backend](../README.md))

### Instalação

1. **Navegue para a pasta do frontend**:
```bash
cd frontend
```

2. **Instale as dependências**:
```bash
npm install
```

3. **Configure as variáveis de ambiente**:
```bash
cp env.example .env
# Edite o .env com suas configurações
```

4. **Execute em modo desenvolvimento**:
```bash
npm run dev
```

A aplicação estará disponível em: `http://localhost:3000`

### Build para Produção

```bash
npm run build
npm start
```

## 🎨 Componentes Principais

### UI Components (shadcn/ui)

Componentes base instalados e prontos para uso:

- **Button**: Botão com variantes
- **Input**: Campo de entrada
- **Label**: Label para formulários
- **Card**: Card container

Para adicionar mais componentes do shadcn/ui:

```bash
npx shadcn-ui@latest add [component-name]
```

### Custom Components

Componentes específicos da aplicação serão organizados por feature em `/features`.

## 🔐 Autenticação

### Login

A tela de login está implementada com:
- ✅ Validação de formulário
- ✅ Integração com Zustand store
- ✅ Redirecionamento automático após login
- ✅ Proteção de rotas via middleware

**Nota**: Atualmente usando login mockado. Substituir por chamada real à API quando disponível.

### Proteção de Rotas

O middleware protege automaticamente rotas que não estão na lista de rotas públicas:

- Rotas públicas: `/login`, `/`
- Rotas protegidas: Todas as outras (ex: `/dashboard`)

## 📊 TanStack Query

Exemplo de uso para chamadas à API:

```typescript
import { useQuery } from "@tanstack/react-query"
import api from "@/services/api"

const { data, isLoading, error } = useQuery({
  queryKey: ["health"],
  queryFn: async () => {
    const response = await api.get("/health")
    return response.data
  },
})
```

## 🗄️ Estado Global (Zustand)

Exemplo de uso do store de autenticação:

```typescript
import { useAuthStore } from "@/store/auth.store"

const { user, isAuthenticated, login, logout } = useAuthStore()
```

## 🎯 Features (Módulos)

A estrutura de features está preparada para organizar módulos futuros:

```
features/
├── pesagem/          # Módulo de pesagem
│   ├── components/
│   ├── hooks/
│   └── services/
├── estoque/          # Módulo de estoque
└── rotas/            # Módulo de rotas
```

## 🛠️ Desenvolvimento

### Scripts Disponíveis

```bash
# Desenvolvimento
npm run dev

# Build
npm run build

# Produção
npm start

# Linting
npm run lint

# Formatação
npm run format
npm run format:check

# Type checking
npm run type-check
```

### Adicionar Componentes shadcn/ui

```bash
npx shadcn-ui@latest add [component-name]
```

Componentes disponíveis: https://ui.shadcn.com/docs/components

### Estrutura de um Feature

Ao criar um novo módulo (ex: pesagem):

1. Criar pasta em `/features/pesagem/`
2. Organizar em subpastas:
   - `components/`: Componentes específicos
   - `hooks/`: Hooks customizados
   - `services/`: Serviços de API
   - `types/`: Tipos TypeScript
3. Exportar em `index.ts`

## 🎨 Design System

### Cores

O tema utiliza variáveis CSS customizadas definidas em `globals.css`:

- Primary: Azul principal
- Secondary: Cinza secundário
- Destructive: Vermelho para ações destrutivas
- Muted: Textos e backgrounds desbotados

### Tema Escuro

Suporte a tema escuro preparado através das variáveis CSS. Pode ser implementado com toggle no futuro.

## 📝 Convenções

### Nomenclatura

- **Componentes**: PascalCase (ex: `UserCard.tsx`)
- **Hooks**: camelCase com prefixo `use` (ex: `useApi.ts`)
- **Services**: camelCase com sufixo `.service.ts` (ex: `auth.service.ts`)
- **Types**: PascalCase em arquivos (ex: `User.ts`)
- **Arquivos**: kebab-case ou camelCase conforme contexto

### Estrutura de Componentes

```typescript
"use client" // Se usar hooks/estado

import { ... } from "@/..."

interface ComponentProps {
  // Props tipadas
}

export default function Component({ ...props }: ComponentProps) {
  // Component logic
  return <div>...</div>
}
```

## 🚧 Próximos Passos

### Funcionalidades Pendentes

1. **Autenticação Real**
   - Substituir login mockado por chamada real à API
   - Implementar refresh token
   - Gerenciamento de sessão

2. **Módulos do MVP**
   - Módulo de Pesagem
   - Módulo de Estoque
   - Módulo de Rotas

3. **Gráficos e Visualizações**
   - Integrar Recharts ou Tremor
   - Dashboards com métricas
   - Relatórios visuais

4. **PWA**
   - Configurar next-pwa
   - Service Worker
   - Offline support

5. **Testes**
   - Unit tests (Jest/Vitest)
   - Integration tests
   - E2E tests (Playwright/Cypress)

### Melhorias Futuras

- [ ] Tema escuro com toggle
- [ ] Internacionalização (i18n)
- [ ] Acessibilidade (a11y) aprimorada
- [ ] Performance optimization
- [ ] SEO optimization
- [ ] Error boundary
- [ ] Loading states aprimorados

## 🔗 Integração com Backend

### URL da API

Configurar em `.env`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### CORS

Certifique-se de que o backend está configurado para aceitar requisições do frontend:

```python
CORS_ORIGINS=["http://localhost:3000"]
```

## 📚 Recursos

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [TanStack Query Documentation](https://tanstack.com/query/latest)
- [Zustand Documentation](https://zustand-demo.pmnd.rs)

## 📄 Licença

[Adicionar licença conforme necessário]

---

**Versão**: 1.0.0  
**Última atualização**: 2024

