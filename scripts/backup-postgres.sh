#!/usr/bin/env bash
# Backup do Postgres via pg_dump
# Uso: ./scripts/backup-postgres.sh [DIR_DESTINO]
# Com Docker: ./scripts/backup-postgres.sh --docker [DIR_DESTINO]

set -e

BACKUP_DIR="${1:-./backups}"
if [[ "$1" == "--docker" ]]; then
  USE_DOCKER=1
  BACKUP_DIR="${2:-./backups}"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# Resolve path relativo ao projeto
[[ "$BACKUP_DIR" != /* ]] && BACKUP_DIR="$PROJ_DIR/$BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILE="$BACKUP_DIR/bom_jesus_${TIMESTAMP}.dump"

echo "Backup iniciado: $FILE"

if [[ -n "$USE_DOCKER" ]]; then
  cd "$PROJ_DIR"
  docker compose exec -T postgres pg_dump -U postgres -Fc bom_jesus > "$FILE"
else
  pg_dump -U postgres -Fc bom_jesus > "$FILE"
fi

echo "Backup concluído: $FILE ($(du -h "$FILE" | cut -f1))"
