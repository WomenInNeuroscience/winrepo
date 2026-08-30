#!/bin/bash
#
# Pull a backup of the production MySQL database from PythonAnywhere
# to the local machine.
#
# Usage: ./pull_db.sh
#
# Prerequisites:
#   - SSH access to PythonAnywhere (public key in ~/.ssh/authorized_keys)
#   - DB env vars set in ~/winrepo-prod/.env on PythonAnywhere
#     (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)

set -eu

PA_USER="winrepo"
PA_HOST="${PA_USER}@ssh.pythonanywhere.com"
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
REMOTE_FILE="/tmp/winrepo_${TIMESTAMP}.sql.gz"

LOCAL_DIR="$(realpath "$(dirname "$0")/..")/backups"
mkdir -p "${LOCAL_DIR}"
LOCAL_FILE="${LOCAL_DIR}/winrepo_${TIMESTAMP}.sql.gz"

echo "==> Dumping database on PythonAnywhere..."
ssh "${PA_HOST}" bash -s "${REMOTE_FILE}" <<'REMOTE'
set -eu
OUTFILE="$1"
cd ~/winrepo-prod
DB_HOST=$(grep '^DB_HOST=' .env | cut -d= -f2-)
DB_NAME=$(grep '^DB_NAME=' .env | cut -d= -f2-)
DB_USER=$(grep '^DB_USER=' .env | cut -d= -f2-)
DB_PASSWORD=$(grep '^DB_PASSWORD=' .env | cut -d= -f2-)
mysqldump \
  -h "${DB_HOST}" \
  -u "${DB_USER}" \
  -p"${DB_PASSWORD}" \
  --single-transaction \
  --no-tablespaces \
  --column-statistics=0 \
  "${DB_NAME}" \
  | gzip > "${OUTFILE}"
REMOTE

echo "==> Downloading to ${LOCAL_FILE}..."
scp "${PA_HOST}:${REMOTE_FILE}" "${LOCAL_FILE}"

echo "==> Cleaning up remote temp file..."
ssh "${PA_HOST}" "rm -f ${REMOTE_FILE}"

echo "==> Done. Backup saved to ${LOCAL_FILE}"
ls -lh "${LOCAL_FILE}"
