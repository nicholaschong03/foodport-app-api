server {
    listen ${LISTEN_PORT};

    location /static {
        alias /vol/static;
        add_header 'Access-Control-Allow-Origin' '*';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range';
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range';
        add_header 'Cache-Control' 'no-cache, must-revalidate, proxy-revalidate';

    }

    location / {
        uwsgi_pass           ${APP_HOST}:${APP_PORT};
        include              /etc/nginx/uwsgi_params;
        client_max_body_size 10M;
        add_header 'Cache-Control' 'no-cache, must-revalidate, proxy-revalidate';

    }
}