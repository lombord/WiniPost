FROM nginxinc/nginx-unprivileged:1-alpine3.18-slim


COPY ./proxy_params ./default.conf.tpl /etc/nginx/
COPY ./start.sh /

USER root

RUN touch /etc/nginx/conf.d/default.conf && \
    mkdir -p /vol/web/ && chmod 755 -R /vol/web && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /start.sh

ENV APP_HOST=django \
    APP_PORT=8000 \
    LISTEN_PORT=8080

USER nginx
EXPOSE 8080
ENTRYPOINT [ "sh", "-c", "/start.sh" ]