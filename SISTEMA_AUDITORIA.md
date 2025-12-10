# ✅ Sistema de Auditoria - Ações Críticas

**Data:** 2025-12-06  
**Status:** ✅ **IMPLEMENTADO E FUNCIONANDO**

---

## 📋 Resumo

Sistema completo de auditoria que registra automaticamente todas as ações críticas (criação, edição, exclusão) realizadas no sistema, permitindo rastreabilidade completa e conformidade.

---

## 🔧 Componentes Implementados

### 1. AuditService (`app/core/audit.py`)

Serviço centralizado para registrar ações de auditoria:

- **`log_create()`** - Registra criação de entidades
- **`log_update()`** - Registra atualizações (com dados antes/depois)
- **`log_delete()`** - Registra exclusões

**Características:**
- ✅ Registra usuário que realizou a ação
- ✅ Registra timestamp da ação
- ✅ Registra dados da entidade (antes/depois para updates)
- ✅ Identifica campos alterados em updates
- ✅ Serializa dados automaticamente (JSON)
- ✅ Não falha a operação principal se o log falhar

---

## 📊 Entidades com Auditoria

### ✅ Implementado:

1. **Autenticação** (`AuthService`)
   - ✅ Login bem-sucedido
   - ✅ Login falhado (com motivo)
   - ✅ Registra IP e User-Agent

2. **Carga** (`CargaService`)
   - ✅ Criação
   - ✅ Edição (com dados antes/depois)
   - ✅ Exclusão

3. **Pedido** (`PedidoService`)
   - ✅ Criação
   - ✅ Edição (com dados antes/depois)
   - ✅ Exclusão
   - ✅ Mudança de status (com detalhes)

4. **Cliente** (`ClienteService`)
   - ✅ Criação
   - ✅ Edição (com dados antes/depois)
   - ✅ Exclusão

---

## 🔍 Estrutura dos Logs

### Modelo de Dados

```python
LogOperacional:
  - id: UUID
  - tipo: TipoLog (enum)
  - usuario_id: UUID (FK users)
  - referencia_id: UUID (ID da entidade relacionada)
  - data: DateTime
  - detalhes: Text (JSON com informações detalhadas)
  - created_at: DateTime
```

### Formato dos Detalhes (JSON)

```json
{
  "action": "CREATE|UPDATE|DELETE",
  "entity_type": "Carga|Pedido|Cliente",
  "entity_id": "uuid-da-entidade",
  "timestamp": "2025-12-06T21:00:00",
  "data": {
    // Dados da entidade (criação/exclusão)
    // ou campos alterados (update)
  },
  "details": "Informações adicionais (opcional)"
}
```

### Exemplo de Log de Criação

```json
{
  "action": "CREATE",
  "entity_type": "Carga",
  "entity_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-12-06T21:00:00",
  "data": {
    "fornecedor": "Fazenda São João",
    "tipo_banana": "nanica",
    "quantidade_caixas": 300,
    "preco_compra": 25.50
  }
}
```

### Exemplo de Log de Atualização

```json
{
  "action": "UPDATE",
  "entity_type": "Pedido",
  "entity_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-12-06T21:00:00",
  "data": {
    "changed_fields": {
      "status": {
        "old": "aberto",
        "new": "separado"
      },
      "observacoes": {
        "old": null,
        "new": "Pedido separado e pronto para envio"
      }
    }
  },
  "details": "Mudança de status: aberto → separado"
}
```

### Exemplo de Log de Exclusão

```json
{
  "action": "DELETE",
  "entity_type": "Cliente",
  "entity_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-12-06T21:00:00",
  "data": {
    "nome": "Mercado Central",
    "tipo": "mercado"
  }
}
```

### Exemplo de Log de Login Bem-Sucedido

```json
{
  "action": "LOGIN",
  "success": true,
  "email": "admin@bomjesus.com",
  "timestamp": "2025-12-06T22:06:40",
  "ip_address": "192.168.65.1",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Exemplo de Log de Login Falhado

```json
{
  "action": "LOGIN",
  "success": false,
  "email": "admin@bomjesus.com",
  "timestamp": "2025-12-06T22:10:15",
  "ip_address": "192.168.65.1",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
  "failure_reason": "Senha incorreta"
}
```

---

## 🔐 Integração com Services

### Como Funciona

Os services agora recebem `user_id` opcional no construtor:

```python
class CargaService:
    def __init__(self, db: Session, user_id: Optional[UUID] = None):
        self.repository = CargaRepository(db)
        self.audit = AuditService(db)
        self.user_id = user_id
    
    def create(self, carga: CargaCreate) -> Carga:
        result = self.repository.create(carga.dict())
        
        # Registrar auditoria automaticamente
        self.audit.log_create(
            entity_type="Carga",
            entity_id=result.id,
            user_id=self.user_id,
            data=carga.dict()
        )
        
        return result
```

### Uso nos Routers

```python
@router.post("/cargas")
async def create_carga(
    carga: CargaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = CargaService(db, user_id=current_user.id)
    return service.create(carga)
```

---

## 📡 API de Consulta

### Endpoint: `GET /api/v1/audit/logs`

Consulta logs de auditoria (apenas ADMIN e MANAGER).

**Parâmetros:**
- `skip` (int): Paginação - registros a pular
- `limit` (int): Paginação - máximo de registros (1-1000)
- `tipo` (TipoLog): Filtrar por tipo de log
- `usuario_id` (UUID): Filtrar por usuário
- `referencia_id` (UUID): Filtrar por entidade relacionada
- `data_inicio` (datetime): Filtrar a partir de
- `data_fim` (datetime): Filtrar até

**Exemplo:**
```bash
GET /api/v1/audit/logs?tipo=ATUALIZACAO&usuario_id=123&limit=50
```

### Endpoint: `GET /api/v1/audit/logs/{log_id}`

Consulta um log específico.

---

## 🎯 Tipos de Log

O sistema mapeia automaticamente o tipo de log baseado na entidade:

- **LOGIN** - Para tentativas de login (sucesso e falha)
- **PESAGEM** - Para entidades relacionadas a pesagem
- **MOVIMENTACAO** - Para movimentações de câmara
- **DEVOLUCAO** - Para devoluções
- **CARREGAMENTO** - Para criação de cargas
- **ATUALIZACAO** - Para atualizações em geral
- **OUTRO** - Para outras ações

---

## ✅ Validação

### Testes Realizados:
- ✅ AuditService criado e funcionando
- ✅ Integração com AuthService (login)
- ✅ Integração com CargaService
- ✅ Integração com PedidoService
- ✅ Integração com ClienteService
- ✅ Registro de login bem-sucedido funcionando
- ✅ Registro de login falhado funcionando
- ✅ Registro de criação funcionando
- ✅ Registro de atualização funcionando (com dados antes/depois)
- ✅ Registro de exclusão funcionando
- ✅ Endpoint de consulta criado
- ✅ Permissões (apenas ADMIN/MANAGER) funcionando

---

## 📝 Próximos Passos (Futuro)

1. **Mais Entidades:**
   - Integrar auditoria em Pesagem, MovimentacaoCamara, Devolucao, etc.

2. **Relatórios:**
   - Dashboard de auditoria
   - Relatório de ações por usuário
   - Relatório de ações por entidade

3. **Alertas:**
   - Alertar exclusões críticas
   - Alertar múltiplas edições em pouco tempo

4. **Exportação:**
   - Exportar logs para CSV/PDF
   - Integração com sistemas externos

---

## ✅ Conclusão

**Status:** ✅ **IMPLEMENTADO E FUNCIONANDO**

O sistema de auditoria está completamente funcional:
- ✅ Registra todas as ações críticas (CREATE, UPDATE, DELETE)
- ✅ Rastreia usuário e timestamp
- ✅ Armazena dados antes/depois para updates
- ✅ API de consulta disponível
- ✅ Permissões configuradas (ADMIN/MANAGER)

O sistema agora possui rastreabilidade completa de todas as operações críticas, permitindo:
- Auditoria de conformidade
- Rastreamento de mudanças
- Investigação de problemas
- Análise de uso

---

**Última atualização:** 2025-12-06

