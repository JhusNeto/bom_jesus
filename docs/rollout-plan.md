# Plano de Rollout em 5 Fases

Alinhado ao blueprint da Proposta Final.

## Fase 1: Base, banco, autenticação

**Escopo**
- Postgres + Prisma schema
- Migrations e `db push`
- Auth JWT + refresh token
- Seed admin, cadastros base
- RBAC mínimo

**Critérios de conclusão**
- [ ] Login/refresh/logout funcionando
- [ ] Seed admin cria usuário padrão
- [ ] Health check retorna OK

**Duração estimada**: 1–2 dias

---

## Fase 2: Operação digital (pesagem + câmaras + perdas)

**Escopo**
- Entrada de lote (LOT_ENTRY_REGISTERED)
- Movimentação (LOT_MOVED)
- Registro de perdas (LOSS_REGISTERED)
- Cadastros: produtos, localizações, motivos de perda
- Pipeline RAW → CLEAN

**Critérios de conclusão**
- [ ] Operador registra entrada e movimentação
- [ ] Perdas geram evento RAW e LossRecord
- [ ] Dados aparecem no histórico

**Duração estimada**: 3–5 dias

---

## Fase 3: Devoluções completo

**Escopo**
- RETURN_REGISTERED
- Cadastros: clientes, lojas, motivos de devolução
- Foto opcional (upload)
- Integração com fluxo operacional

**Critérios de conclusão**
- [ ] Devoluções por cliente/loja registradas
- [ ] Foto vinculada quando enviada
- [ ] Histórico e relatórios incluem devoluções

**Duração estimada**: 2–3 dias

---

## Fase 4: Dashboard + relatórios gerenciais

**Escopo**
- KPIs em tempo (quase) real
- Estoque por maturação
- Perdas (dia/mês)
- Devoluções por cliente
- Tendências (série temporal)
- Export CSV

**Critérios de conclusão**
- [ ] Dashboard carrega sem erro
- [ ] Métricas refletem dados do banco
- [ ] Export CSV funciona

**Duração estimada**: 2–3 dias

---

## Fase 5: Estabilização + refinamentos

**Escopo**
- Alertas configuráveis (estoque madura, perdas, backlog RAW)
- Job de maturação diária
- Backup/restore validado
- Correção de fricções UAT
- Documentação operacional

**Critérios de conclusão**
- [ ] Alertas disparando conforme regras
- [ ] Backup e restore testados
- [ ] UAT concluído (10 dias úteis)
- [ ] Go-live checklist assinado

**Duração estimada**: 2 semanas (inclui UAT)

---

## Calendário sugerido

| Semana | Fases |
|--------|-------|
| 1 | Fase 1 + 2 |
| 2 | Fase 3 + início Fase 4 |
| 3 | Fase 4 completa + início Fase 5 |
| 4–5 | Fase 5: UAT e go-live |
