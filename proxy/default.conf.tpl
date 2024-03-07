server {
    listen ${LISTEN_PORT};

    location /static {
        alias /vol/web;
    }

    location / {
        proxy_pass  http://${APP_HOST}:${APP_PORT};
        include     /etc/nginx/proxy_params;
        client_max_body_size    50M;
    }
}