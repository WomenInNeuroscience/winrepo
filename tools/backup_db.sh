#!/bin/bash
#
# Back up the production MySQL database on PythonAnywhere.
# Can be scheduled as a daily task via the PythonAnywhere "Tasks" tab.
#
# Required environment variables:
#   DB_HOST     — MySQL hostname (e.g. username.mysql.pythonanywhere-services.com)
#   DB_NAME     — database name
#   DB_USER     — database user
#   DB_PASSWORD — database password
#
# Backups are stored in ~/backups/ with a date stamp.
# Old backups beyond KEEP_DAYS are automatically pruned.

set -eu

# Load environment from .env (safe parser — avoids shell-expansion issues
# with values containing $, backticks, etc., e.g. winrepo$winrepo_prod).
BASEDIR=$(realpath "$(dirname "$0")/..")
if [[ -f "${BASEDIR}/.env" ]]; then
  while IFS='=' read -r key value; do
    [[ -z "$key" || "$key" == \#* ]] && continue
    export "$key"="$value"
  done < "${BASEDIR}/.env"
fi

KEEP_DAYS=30
BACKUP_DIR="${HOME}/backups"
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
# Sanitize DB_NAME for filename (replace $ with _)
SAFE_DB_NAME="${DB_NAME//\$/_}"
BACKUP_FILE="${BACKUP_DIR}/${SAFE_DB_NAME}_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "==> Backing up ${DB_NAME}..."
# --no-tablespaces: PythonAnywhere users lack PROCESS privilege
# --column-statistics=0: MySQL 8 client vs older server compatibility
mysqldump \
  -h "${DB_HOST}" \
  -u "${DB_USER}" \
  -p"${DB_PASSWORD}" \
  --single-transaction \
  --routines \
  --no-tablespaces \
  --column-statistics=0 \
  "${DB_NAME}" \
  | gzip > "${BACKUP_FILE}"

echo "==> Backup saved to ${BACKUP_FILE}"

echo "==> Pruning backups older than ${KEEP_DAYS} days..."
find "${BACKUP_DIR}" -name "*.sql.gz" -mtime +${KEEP_DAYS} -delete

echo "==> Done."
