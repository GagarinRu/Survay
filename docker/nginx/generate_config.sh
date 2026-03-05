#!/bin/sh
set -e

envsubst '${NGINX_APP_HOST} ${APP_GUVICORN_PORT} ${NGINX_PORT}' \
  < /etc/nginx/site.conf.template \
  > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'