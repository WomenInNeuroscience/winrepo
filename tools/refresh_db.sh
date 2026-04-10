#!/bin/bash
#
# Reset the local dev database and populate it with test data.
# Only for local development — never run this in production.

set -eu

BASEDIR=$(realpath "$(dirname "$0")/..")
cd "${BASEDIR}"

rm -f db-dev.sqlite3

echo "==> Running migrations..."
python manage.py migrate

echo "==> Loading fixtures..."
python manage.py refresh_fixtures --profiles=100

echo "==> Dev database ready."
