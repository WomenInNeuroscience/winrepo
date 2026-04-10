#!/bin/bash
#
# Deploy script for PythonAnywhere.
# Called by the CD pipeline (GitHub Actions) after tests pass on main.
#
# Required environment variables (set in .env or PythonAnywhere dashboard):
#   PYTHONANYWHERE_TOKEN
#   PYTHONANYWHERE_USERNAME
#   PYTHONANYWHERE_DOMAIN

set -eu

BASEDIR=$(realpath "$(dirname "$0")/..")
cd "${BASEDIR}"

echo "==> Pulling latest code..."
git pull

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Reloading webapp..."
curl -s \
  -X POST \
  -H "Authorization: Token ${PYTHONANYWHERE_TOKEN}" \
  "https://www.pythonanywhere.com/api/v0/user/${PYTHONANYWHERE_USERNAME}/webapps/${PYTHONANYWHERE_DOMAIN}/reload/"

echo ""
echo "==> Deploy complete."
