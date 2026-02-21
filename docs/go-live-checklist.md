# Checklist Go-Live

Conferir antes de colocar em produção.

## Infraestrutura

- [ ] Banco Postgres em ambiente produtivo
- [ ] Backend deployado e saudável (health check)
- [ ] Frontend deployado (PWA acessível)
- [ ] Variáveis de ambiente produtivas (DATABASE_URL, JWT_SECRET, etc.)
- [ ] Backup diário configurado e testado

## Segurança

- [ ] JWT_SECRET forte e exclusivo
- [ ] Senhas de admin alteradas
- [ ] HTTPS habilitado
- [ ] CORS configurado para origens corretas

## Dados e integridade

- [ ] Migrations aplicadas
- [ ] Seed admin executado (ou usuários criados manualmente)
- [ ] Cadastros base (produtos, locais, clientes, lojas, motivos) populados

## Operacional

- [ ] Jobs agendados rodando (processRawEvents, refreshMaterializedViews, updateMaturation, runAlerts)
- [ ] Alertas configurados (SMTP/VAPID se aplicável)
- [ ] Logs e monitoramento configurados

## UAT

- [ ] UAT concluído com aceite
- [ ] Fricções críticas resolvidas
- [ ] Treinamento de usuários realizado

## Pós go-live

- [ ] Comunicar equipe sobre disponibilidade
- [ ] Suporte de primeira linha definido
- [ ] Runbook de incidentes acessível
