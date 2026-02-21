#!/usr/bin/env bash
# Teste automatizado: backup + restore em staging
# Uso: ./scripts/test-backup-restore.sh [--docker]
# Requer: stack rodando (docker compose up)
# Saída: 0 se OK, 1 se falhou

set -e

USE_DOCKER=""
[[ "$1" == "--docker" ]] && USE_DOCKER="--docker"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_DIR="$PROJ_DIR/backups"
STAGING_DB="bom_jesus_staging_test"

cd "$PROJ_DIR"

echo "=== Teste backup/restore ==="

# 1. Backup
echo "1. Executando backup..."
"$SCRIPT_DIR/backup-postgres.sh" $USE_DOCKER "$BACKUP_DIR"
LAST=$(ls -t "$BACKUP_DIR"/bom_jesus_*.dump 2>/dev/null | head -1)
if [[ -z "$LAST" || ! -f "$LAST" ]]; then
  echo "FALHA: Backup não gerado"
  exit 1
fi
echo "   Backup: $LAST ($(du -h "$LAST" | cut -f1))"

# 2. Restore em staging
echo "2. Restaurando em $STAGING_DB..."
"$SCRIPT_DIR/restore-postgres.sh" $USE_DOCKER "$LAST" "$STAGING_DB"

# 3. Validar (contar tabelas)
echo "3. Validando restore..."
if [[ -n "$USE_DOCKER" ]]; then
  COUNT=$(docker compose exec -T postgres psql -U postgres -d "$STAGING_DB" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
else
  COUNT=$(psql -U postgres -d "$STAGING_DB" -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';")
fi
if [[ "${COUNT:-0}" -lt 10 ]]; then
  echo "FALHA: Restore incompleto (apenas $COUNT tabelas)"
  exit 1
fi
echo "   Tabelas em public: $COUNT"

# 4. Limpar staging de teste
if [[ -n "$USE_DOCKER" ]]; then
  docker compose exec -T postgres psql -U postgres -c "DROP DATABASE IF EXISTS ${STAGING_DB};" >/dev/null
else
  psql -U postgres -c "DROP DATABASE IF EXISTS ${STAGING_DB};" >/dev/null
fi

echo "=== OK: Backup e restore validados ==="
