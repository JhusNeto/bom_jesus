# Runbook: Backup e Restore Postgres

## Backup

### Via Docker (recomendado em produção)

```bash
# Do diretório raiz do projeto
./scripts/backup-postgres.sh --docker ./backups
```

### Sem Docker (Postgres local)

```bash
./scripts/backup-postgres.sh /caminho/backups
```

O arquivo gerado é `bom_jesus_YYYYMMDD_HHMMSS.dump` (formato custom `-Fc`, compacto).

### Agendamento (cron diário)

```cron
# Todo dia às 2h
0 2 * * * cd /caminho/projeto && ./scripts/backup-postgres.sh --docker ./backups
```

Considere:
- Rotacionar backups (ex.: manter 7 diários, 4 semanais, 12 mensais)
- Copiar para storage externo (S3, NFS)

## Restore

### Atenção

- Restore em **produção** substitui o banco. Fazer apenas em cenário de recuperação.
- Em **staging/teste**: usar um DB diferente, ex. `bom_jesus_staging`.

### Via Docker

```bash
# Restore em banco de staging (seguro)
./scripts/restore-postgres.sh --docker ./backups/bom_jesus_20260220_120000.dump bom_jesus_staging

# Restore no banco principal (cuidado!)
./scripts/backup-postgres.sh --docker ./backups  # backup antes!
./scripts/restore-postgres.sh --docker ./backups/bom_jesus_20260220_120000.dump bom_jesus
```

### Sem Docker

```bash
./scripts/restore-postgres.sh ./backups/bom_jesus_20260220_120000.dump bom_jesus_staging
```

### Pós-restore

1. Rodar `npx prisma generate` no backend (se schema mudou).
2. Reiniciar backend: `docker compose restart backend`.
3. Validar: login, dashboard, eventos RAW.
