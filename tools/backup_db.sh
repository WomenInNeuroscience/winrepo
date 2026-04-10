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

KEEP_DAYS=30
BACKUP_DIR="${HOME}/backups"
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "==> Backing up ${DB_NAME}..."
mysqldump \
  -h "${DB_HOST}" \
  -u "${DB_USER}" \
  -p"${DB_PASSWORD}" \
  --single-transaction \
  --routines \
  "${DB_NAME}" \
  | gzip > "${BACKUP_FILE}"

echo "==> Backup saved to ${BACKUP_FILE}"

echo "==> Pruning backups older than ${KEEP_DAYS} days..."
find "${BACKUP_DIR}" -name "*.sql.gz" -mtime +${KEEP_DAYS} -delete

echo "==> Done."
