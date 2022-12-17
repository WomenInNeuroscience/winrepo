#!/bin/bash

set -eu

BASEDIR=$(realpath $(dirname "$0")/..)
cd ${BASEDIR}
git pull

python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate

# ./tools/refresh_db.sh

curl \
-X POST \
-H "Authorization: Token ${PYTHONANYWHERE_TOKEN}" \
https://www.pythonanywhere.com/api/v0/user/${PYTHONANYWHERE_USERNAME}/webapps/${PYTHONANYWHERE_DOMAIN}/reload/
