#!/usr/bin/env bash
# Restore do Postgres via pg_restore
# Uso: ./scripts/restore-postgres.sh ARQUIVO.dump [TARGET_DB]
# Com Docker: ./scripts/restore-postgres.sh --docker ARQUIVO.dump [TARGET_DB]
#
# ATENÇÃO: Restore substitui o banco. Em produção, restaurar em DB de staging/teste primeiro.
# TARGET_DB padrão: bom_jesus (use bom_jesus_staging para testes)

set -e

USE_DOCKER=""
FILE=""
TARGET_DB="bom_jesus"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --docker)
      USE_DOCKER=1
      shift
      ;;
    *.dump)
      FILE="$1"
      shift
      ;;
    *)
      TARGET_DB="$1"
      shift
      ;;
  esac
done

if [[ -z "$FILE" || ! -f "$FILE" ]]; then
  echo "Uso: $0 [--docker] ARQUIVO.dump [TARGET_DB]"
  echo "Exemplo: $0 --docker ./backups/bom_jesus_20260220_120000.dump bom_jesus_staging"
  exit 1
fi

echo "Restore: $FILE -> $TARGET_DB"

do_restore() {
  # Drop e recria o DB para restore limpo
  psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$TARGET_DB'" | grep -q 1 && \
    psql -U postgres -c "DROP DATABASE ${TARGET_DB};"
  psql -U postgres -c "CREATE DATABASE ${TARGET_DB};"
  pg_restore -U postgres -d "$TARGET_DB" --no-owner --no-acl "$FILE"
}

if [[ -n "$USE_DOCKER" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  PROJ_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
  FILE_ABS="$(cd "$(dirname "$FILE")" && pwd)/$(basename "$FILE")"
  (
    cd "$PROJ_DIR"
    docker compose exec -T postgres psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$TARGET_DB' AND pid <> pg_backend_pid();" 2>/dev/null || true
    docker compose exec -T postgres psql -U postgres -c "DROP DATABASE IF EXISTS ${TARGET_DB};"
    docker compose exec -T postgres psql -U postgres -c "CREATE DATABASE ${TARGET_DB};"
    cat "$FILE_ABS" | docker compose exec -i postgres pg_restore -U postgres -d "$TARGET_DB" --no-owner --no-acl
  )
else
  do_restore
fi

echo "Restore concluído em $TARGET_DB"
