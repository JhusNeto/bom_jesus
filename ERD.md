# 📊 Diagrama Entidade-Relacionamento (ERD)
## Sistema Operacional Bom Jesus - MVP

## 🎯 Visão Geral

Este documento apresenta o diagrama entidade-relacionamento textual das 15 entidades essenciais do MVP.

---

## 📐 Diagrama Textual

```
┌─────────────────────────────────────────────────────────────────┐
│                    NÚCLEO OPERACIONAL                           │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐         ┌──────────────────────┐
│  CARGA   │         │      CAMARA          │
├──────────┤         ├──────────────────────┤
│ id       │         │ id                   │
│ data     │         │ nome (unique)        │
│ fornecedor│        │ capacidade           │
│ fazenda  │         │ status               │
│ tipo     │         └──────────────────────┘
│ qualidade│                  │
│ qtd_cx   │                  │
│ preco    │                  │
│ status   │                  │
└──────────┘                  │
     │                        │
     │ 1:N                    │ 1:N
     │                        │
     ▼                        ▼
┌──────────────┐    ┌─────────────────────────┐
│ MOVIMENTACAO │    │      PESAGEM            │
│   CAMARA     │    ├─────────────────────────┤
├──────────────┤    │ id                      │
│ id           │    │ data                    │
│ camara_id FK │    │ cliente_id FK           │
│ carga_id FK  │    │ carga_id FK             │
│ tipo_mov     │    │ qtd_caixas              │
│ qtd_caixas   │    │ peso_total              │
│ observacao   │    │ operador_id FK          │
└──────────────┘    │ status                  │
                    └─────────────────────────┘
     │                        │
     │                        │
     │ 1:N                    │ 1:N
     │                        │
     ▼                        ▼
┌──────────┐         ┌──────────────────────┐
│  PERDA   │         │      CLIENTE          │
├──────────┤         ├──────────────────────┤
│ id       │         │ id                   │
│ carga_id │        │ nome                 │
│ data     │         │ tipo                 │
│ qtd_cx   │         │ cidade/bairro        │
│ motivo   │         │ endereco             │
│ valor    │         │ telefone             │
└──────────┘         │ ativo                │
                    └──────────────────────┘
                             │
                             │ 1:N
                             │
                             ▼
                    ┌──────────────────────┐
                    │      PEDIDO           │
                    ├──────────────────────┤
                    │ id                   │
                    │ data                 │
                    │ cliente_id FK        │
                    │ origem_pedido        │
                    │ status               │
                    │ observacoes          │
                    └──────────────────────┘
                             │
                             │ 1:N
                             │
                             ▼
                    ┌──────────────────────┐
                    │    ITEM_PEDIDO       │
                    ├──────────────────────┤
                    │ id                   │
                    │ pedido_id FK         │
                    │ tipo_banana          │
                    │ qtd_caixas           │
                    │ preco_unitario       │
                    │ preco_total          │
                    └──────────────────────┘
                             │
                             │ 1:N
                             │
                             ▼
                    ┌──────────────────────┐
                    │    DEVOLUCAO         │
                    ├──────────────────────┤
                    │ id                   │
                    │ cliente_id FK        │
                    │ pedido_id FK         │
                    │ data                 │
                    │ qtd_caixas           │
                    │ motivo               │
                    │ valor_estornado      │
                    └──────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    NÚCLEO FINANCEIRO                             │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   GASTO_INTERNO      │
├──────────────────────┤
│ id                   │
│ data                 │
│ tipo                 │
│ valor                │
│ descricao            │
└──────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    NÚCLEO TÉCNICO                                │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐         ┌──────────────────────┐
│  USER   │         │  LOG_OPERACIONAL     │
├──────────┤         ├──────────────────────┤
│ id       │         │ id                   │
│ name     │         │ tipo                 │
│ email    │         │ usuario_id FK        │
│ password │         │ referencia_id        │
│ role     │         │ data                 │
│ active   │         │ detalhes             │
└──────────┘         └──────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    NÚCLEO IA / FUTURO                            │
└─────────────────────────────────────────────────────────────────┘

┌──────────┐         ┌──────────────────────┐
│ OCR_INPUT│         │       ROTA           │
├──────────┤         ├──────────────────────┤
│ id       │         │ id                   │
│ imagem   │         │ motorista            │
│ texto    │         │ veiculo              │
│ confianca│         │ data                 │
│ cliente  │         │ status               │
│ data     │         │ observacoes          │
└──────────┘         └──────────────────────┘
                             │
                             │ 1:N
                             │
                             ▼
                    ┌──────────────────────┐
                    │  ENTREGA_CLIENTE    │
                    ├──────────────────────┤
                    │ id                   │
                    │ rota_id FK           │
                    │ cliente_id FK        │
                    │ pedido_id FK         │
                    │ qtd_caixas           │
                    │ devolucao            │
                    │ horario              │
                    └──────────────────────┘
```

---

## 🔗 Relacionamentos Detalhados

### Núcleo Operacional
- **Carga** → **MovimentacaoCamara** (1:N)
- **Carga** → **Pesagem** (1:N)
- **Carga** → **Perda** (1:N)
- **Camara** → **MovimentacaoCamara** (1:N)

### Núcleo Comercial
- **Cliente** → **Pedido** (1:N)
- **Cliente** → **Pesagem** (1:N)
- **Cliente** → **Devolucao** (1:N)
- **Cliente** → **EntregaCliente** (1:N)
- **Pedido** → **ItemPedido** (1:N)
- **Pedido** → **Devolucao** (1:N)
- **Pedido** → **EntregaCliente** (1:N)

### Núcleo Técnico
- **User** → **LogOperacional** (1:N, opcional)
- **User** → **Pesagem** (1:N, como operador)

### Núcleo IA/Futuro
- **Cliente** → **OCRInput** (1:N, opcional)
- **Rota** → **EntregaCliente** (1:N)
- **EntregaCliente** → **Cliente** (N:1)
- **EntregaCliente** → **Pedido** (N:1, opcional)

---

## 📊 Estatísticas

- **Total de Tabelas**: 15
- **Total de Relacionamentos**: 20+
- **Foreign Keys**: 15+
- **Índices**: 30+

---

**Versão**: 1.0.0  
**Data**: 2024
