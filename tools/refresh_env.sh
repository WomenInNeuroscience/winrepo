#!/bin/bash

cd ${HOME}/winrepo
git pull

./tools/refresh_db.sh

curl \
-H 'Authorization: Token ${PYTHONANYWHERE_TOKEN}' \
https://www.pythonanywhere.com/api/v0/user/${PYTHONANYWHERE_USERNAME}/webapps/${PYTHONANYWHERE_DOMAIN}/reload/
