# Checklist UAT (10 dias úteis)

Uso no ambiente real com usuários-chave (operador, gestor, admin).

## Pré-UAT

- [ ] Backend e frontend publicados em ambiente de homologação
- [ ] Banco com dados de teste/seed
- [ ] Credenciais distribuídas (operador, gestor, admin)
- [ ] Acesso móvel (PWA) testado

## Dia 1–2: Operação básica

- [ ] **Login** – operador faz login e vê home
- [ ] **Entrada de lote** – registra pesagem (produto, local, caixas)
- [ ] **Movimentação** – move lote entre câmaras
- [ ] **Perda** – registra perda com motivo
- [ ] **Offline** – desconecta, registra evento, reconecta e sync funciona

## Dia 3–4: Devoluções e fotos

- [ ] **Devolução** – registra devolução por cliente/loja
- [ ] **Foto** – anexa foto à devolução (quando aplicável)
- [ ] **Histórico** – consulta eventos e movimentações

## Dia 5–6: Dashboard e backoffice

- [ ] **Dashboard** – KPIs carregam; gráficos coerentes
- [ ] **Export CSV** – download de KPIs e tendências
- [ ] **Admin** – cadastros (produtos, locais, clientes, lojas, motivos)
- [ ] **Pipeline** – revisão de needs_review e reprocessamento

## Dia 7–8: Alertas e refinamentos

- [ ] **Alertas** – regras ativas; notificações (e-mail/push) quando configurado
- [ ] **Maturação** – job diário atualiza estados
- [ ] **Correções** – fricções reportadas são tratadas

## Dia 9–10: Validação final

- [ ] Todos os fluxos principais passam sem erro
- [ ] Performance aceitável em dispositivo real
- [ ] Sem bloqueios críticos para go-live
- [ ] Checklist go-live pré-preenchido

## Registro de fricções

| # | Descrição | Severidade | Status |
|---|-----------|------------|--------|
| 1 | _exemplo_ | Alta/Média/Baixa | Resolvido/Pendente |
|   |           |            |        |
