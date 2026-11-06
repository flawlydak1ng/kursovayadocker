FROM nginx:alpine

ARG APP_VERSION=dev

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
RUN sed -i "s/__VERSION__/${APP_VERSION}/g" /usr/share/nginx/html/index.html

HEALTHCHECK --interval=5s --timeout=3s --retries=5 \
  CMD wget -qO /dev/null http://127.0.0.1/ || exit 1
