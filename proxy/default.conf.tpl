server {
    listen ${LISTEN_PORT};
    server_name api.foodport.com.my;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name api.foodport.com.my;

    ssl_certificate /etc/nginx/ssl/api_foodport_com_my.crt;
    ssl_certificate_key /etc/nginx/ssl/api_foodport_com_my.key;

    location /static {
        alias /vol/static;
    }

    location / {
        uwsgi_pass           ${APP_HOST}:${APP_PORT};
        include              /etc/nginx/uwsgi_params;
        client_max_body_size 10M;

        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization';
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range';
    }
}