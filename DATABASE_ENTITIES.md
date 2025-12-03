# 📊 Entidades do Banco de Dados - MVP
## Sistema Operacional Bom Jesus

Este documento descreve todas as entidades essenciais do MVP, organizadas por núcleos funcionais.

---

## 🧱 A. Núcleo Operacional

### 1. Carga (`cargas`)

**Descrição**: Representa uma entrada de frutas vinda de um fornecedor.

**Campos principais**:
- `id` (UUID) - Identificador único
- `data_chegada` (DateTime) - Data de chegada da carga
- `fornecedor` (String) - Nome do fornecedor
- `fazenda` (String, opcional) - Nome da fazenda
- `tipo_banana` (Enum) - Tipo: nanica, prata, maca, outra
- `qualidade_inicial` (String) - Qualidade: A, B, C, etc.
- `quantidade_caixas` (Integer) - Quantidade de caixas
- `preco_compra` (Numeric) - Preço de compra
- `status` (Enum) - em_estoque, encerrada
- `created_at`, `updated_at` (DateTime)

**Relacionamentos**:
- `movimentacoes` → MovimentacaoCamara (1:N)
- `pesagens` → Pesagem (1:N)
- `perdas` → Perda (1:N)

---

### 2. Camara (`camaras`)

**Descrição**: Representa cada câmara fria física.

**Campos principais**:
- `id` (UUID)
- `nome` (String, único) - Nome da câmara
- `capacidade` (Integer) - Capacidade em caixas
- `status` (Enum) - disponivel, ocupada, manutencao
- `created_at`, `updated_at` (DateTime)

**Relacionamentos**:
- `movimentacoes` → MovimentacaoCamara (1:N)

---

### 3. MovimentacaoCamara (`movimentacoes_camara`)

**Descrição**: Tudo que entra e sai da câmara.

**Campos principais**:
- `id` (UUID)
- `camara_id` (UUID, FK) - Referência à câmara
- `carga_id` (UUID, FK opcional) - Referência à carga
- `data` (DateTime)
- `tipo_movimento` (Enum) - entrada, saida
- `quantidade_caixas` (Integer)
- `observacao` (Text, opcional)
- `created_at`, `updated_at` (DateTime)

**Relacionamentos**:
- `camara` → Camara (N:1)
- `carga` → Carga (N:1, opcional)

---

### 4. Pesagem (`pesagens`)

**Descrição**: Cada operação de pesagem para separar caixas por cliente.

**Campos principais**:
- `id` (UUID)
- `data` (DateTime)
- `cliente_id` (UUID, FK)
- `carga_id` (UUID, FK)
- `quantidade_caixas` (Integer)
- `peso_total` (Numeric) - Em kg
- `operador_id` (UUID, FK opcional) - Usuário que fez a pesagem
- `status` (Enum) - pendente, carregado, enviado
- `created_at`, `updated_at` (DateTime)

**Relacionamentos**:
- `cliente` → Cliente (N:1)
- `carga` → Carga (N:1)
- `operador` → User (N:1, opcional)

---

### 5. Perda (`perdas`)

**Descrição**: Quando a fruta estraga, amolece, ou é separada.

**Campos principais**:
- `id` (UUID)
- `carga_id` (UUID, FK)
- `data` (DateTime)
- `quantidade_caixas` (Integer)
- `motivo` (String) - passou, madura, machucada, etc.
- `valor_estimado` (Numeric)
- `created_at`, `updated_at` (DateTime)

**Relacionamentos**:
- `carga` → Carga (N:1)

---

## 🛒 B. Núcleo Comercial

### 6. Cliente (`clientes`)

**Descrição**: Mercados, CEASA, Veneza, Açaí, etc.

**Campos principais**:
- `id` (UUID)
- `nome` (String)
- `tipo` (Enum) - ceasa, mercado, atacado, sacolao, outro
- `cidade` (String, opcional)
- `bairro` (String, opcional)
- `endereco` (String, opcional)
- `telefone` (String, opcional)
- `ativo` (Boolean) - Se o cliente está ativo
- `created_at`, `updated_at` (DateTime)

**Relacionamentos**:
- `pedidos` → Pedido (1:N)
- `pesagens` → Pesagem (1:N)
- `devolucoes` → Devolucao (1:N)
- `entregas` → EntregaCliente (1:N)
- `ocr_inputs` → OCRInput (1:N)

---

### 7. Pedido (`pedidos`)

**Descrição**: O pedido feito pelo cliente (WhatsApp, telefone, manual, OCR).

**Campos principais**:
- `id` (UUID)
- `data` (DateTime)
- `cliente_id` (UUID, FK)
- `origem_pedido` (Enum) - manual, ocr, whatsapp, telefone, outro
- `status` (Enum) - aberto, separado, enviado, devolucao, encerrado
- `observacoes` (String, opcional)
- `created_at`, `updated_at` (DateTime)

**Relacionamentos**:
- `cliente` → Cliente (N:1)
- `itens` → ItemPedido (1:N)
- `devolucoes` → Devolucao (1:N)
- `entregas` → EntregaCliente (1:N)

---

### 8. ItemPedido (`itens_pedido`)

**Descrição**: Itens do pedido (cada tipo de banana/tipo de fruta).

**Campos principais**:
- `id` (UUID)
- `pedido_id` (UUID, FK)
- `tipo_banana` (Enum) - nanica, prata, maca, outra
- `quantidade_caixas` (Integer)
- `preco_unitario` (Numeric)
- `preco_total` (Numeric)
- `created_at`, `updated_at` (DateTime)

**Relacionamentos**:
- `pedido` → Pedido (N:1)

---

### 9. Devolucao (`devolucoes`)

**Descrição**: Quando o cliente devolve caixas.

**Campos principais**:
- `id` (UUID)
- `cliente_id` (UUID, FK)
- `pedido_id` (UUID, FK opcional)
- `data` (DateTime)
- `quantidade_caixas` (Integer)
- `motivo` (Text)
- `valor_estornado` (Numeric)
- `created_at`, `updated_at` (DateTime)

**Relacionamentos**:
- `cliente` → Cliente (N:1)
- `pedido` → Pedido (N:1, opcional)

---

## 🧾 C. Núcleo Financeiro Básico

### 10. GastoInterno (`gastos_internos`)

**Descrição**: Para vale-transporte, gasolina, custo interno da operação.

**Campos principais**:
- `id` (UUID)
- `data` (DateTime)
- `tipo` (Enum) - vale_transporte, gasolina, administrativo, manutencao, outro
- `valor` (Numeric)
- `descricao` (Text, opcional)
- `created_at`, `updated_at` (DateTime)

**Nota**: Sem querer competir com Conta Azul — apenas controle interno simples.

---

## 👥 D. Núcleo Técnico

### 11. Usuario (`users`)

**Descrição**: Usuários do sistema (já modelado anteriormente).

**Campos principais**:
- `id` (UUID)
- `name` (String)
- `email` (String, único)
- `hashed_password` (String)
- `role` (Enum) - admin, manager, operator, viewer
- `is_active` (String) - Y/N
- `created_at`, `updated_at` (DateTime)

---

### 12. LogOperacional (`logs_operacionais`)

**Descrição**: Registro mínimo de auditoria e ações.

**Campos principais**:
- `id` (UUID)
- `tipo` (Enum) - login, pesagem, carregamento, atualizacao, devolucao, movimentacao, outro
- `usuario_id` (UUID, FK opcional)
- `referencia_id` (UUID, opcional) - ID genérico da entidade relacionada
- `data` (DateTime)
- `detalhes` (Text, opcional)
- `created_at` (DateTime)

**Relacionamentos**:
- `usuario` → User (N:1, opcional)

---

## 🔮 E. Núcleo IA / Futuro

### 13. OCR_Input (`ocr_inputs`)

**Descrição**: Para armazenar imagens e extração OCR dos pedidos manuscritos.

**Campos principais**:
- `id` (UUID)
- `imagem_url` (String)
- `texto_extraido` (Text, opcional)
- `confianca` (Numeric, opcional) - 0.00 a 100.00
- `cliente_id` (UUID, FK opcional)
- `data` (DateTime)
- `created_at`, `updated_at` (DateTime)

**Relacionamentos**:
- `cliente` → Cliente (N:1, opcional)

---

### 14. Rota (`rotas`)

**Descrição**: Prepara estrutura para o módulo de rota do Derson.

**Campos principais**:
- `id` (UUID)
- `motorista` (String, opcional)
- `veiculo` (String, opcional)
- `data` (DateTime)
- `status` (Enum) - planejada, em_andamento, concluida, cancelada
- `observacoes` (String, opcional)
- `created_at`, `updated_at` (DateTime)

**Relacionamentos**:
- `entregas` → EntregaCliente (1:N)

---

### 15. EntregaCliente (`entregas_cliente`)

**Descrição**: Relacionamento rota → cliente.

**Campos principais**:
- `id` (UUID)
- `rota_id` (UUID, FK)
- `cliente_id` (UUID, FK)
- `pedido_id` (UUID, FK opcional)
- `quantidade_caixas` (Integer)
- `devolucao` (Boolean) - Se houve devolução
- `horario` (DateTime, opcional)
- `created_at`, `updated_at` (DateTime)

**Relacionamentos**:
- `rota` → Rota (N:1)
- `cliente` → Cliente (N:1)
- `pedido` → Pedido (N:1, opcional)

---

## 📊 Resumo

**Total de Entidades**: 15

- **Núcleo Operacional**: 5 entidades
- **Núcleo Comercial**: 4 entidades
- **Núcleo Financeiro**: 1 entidade
- **Núcleo Técnico**: 2 entidades
- **Núcleo IA/Futuro**: 3 entidades

---

## 🔗 Relacionamentos Principais

```
Cliente (1) ──< (N) Pedido ──< (N) ItemPedido
Cliente (1) ──< (N) Pesagem
Cliente (1) ──< (N) Devolucao
Cliente (1) ──< (N) EntregaCliente

Carga (1) ──< (N) MovimentacaoCamara
Carga (1) ──< (N) Pesagem
Carga (1) ──< (N) Perda

Camara (1) ──< (N) MovimentacaoCamara

Rota (1) ──< (N) EntregaCliente ──> (N) Cliente
```

---

**Versão**: 1.0.0  
**Data**: 2024

