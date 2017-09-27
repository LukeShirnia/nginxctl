# Unit Test NginxCtl

import pytest
import textwrap
import nginxctl

NGINX_CONF = textwrap.dedent("""\
    user nginx;
    worker_processes auto;
    error_log /var/log/nginx/error.log;
    pid /run/nginx.pid;
    include /usr/share/nginx/modules/*.conf;
    events {
        worker_connections 1024;
    }
    http {
        log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                          '$status $body_bytes_sent "$http_referer" '
                          '"$http_user_agent" "$http_x_forwarded_for"';
        access_log  /var/log/nginx/access.log  main;
        sendfile            on;
        tcp_nopush          on;
        tcp_nodelay         on;
        keepalive_timeout   65;
        types_hash_max_size 2048;
        include             /etc/nginx/mime.types;
        default_type        application/octet-stream;
        include /etc/nginx/conf.d/*.conf;
        server {
            listen       80 default_server;
            listen       [::]:80 default_server;
            server_name  _;
            root         /usr/share/nginx/html;
            include /etc/nginx/default.d/*.conf;
            location / {
            }
            error_page 404 /404.html;
                location = /40x.html {
            }
            error_page 500 502 503 504 /50x.html;
                location = /50x.html {
            }
        }
    }
""")
NGINX_SERVERBLOCK("""\
    server {
        listen 80;
        server_name randomwebsite.com www.randomwebsite.com;
        access_log /var/log/nginx/randomwebsite.com.access.log;
        error_log /var/log/nginx/randomwebsite.com.access.log;
        root /var/www/vhost/test1/;
    location / {
        index index.html index.htm index.php;
    }
    location ~ \.php$ {
        include /etc/nginx/fastcgi_params;
        fastcgi_pass  127.0.0.1:9000; #this means php-fpm will run on a port
        # fastcgi_pass unix:/run/php-fpm/example.com.sock; or you could have php-fpm running on a socket
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME /var/www/html/randomwebsite.com$fastcgi_script_name;
        }
    }
""")

@pytest.fixture
def mock_nginx(nf):
    nf.CreateFile('/etc/nginx/nginx.conf', contents=NGINX_CONF)
    nf.CreateFiles('/etc/nginx/conf.d/example.com.conf', contents=NGINX_SERVERBLOCK)
    return nf
