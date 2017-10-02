import unittest
import nginxctl
import mock
import tempfile


class nginxCtlTests(unittest.TestCase):
    def test_strip_line(self):
        """ Test line can be stripped"""
        test_str = '''"nginxCtl 'is' an amzing tool;'''
        result_test_str = "nginxCtl is an amzing tool"
        n = nginxctl.nginxCtl()
        self.assertEqual(n._strip_line(test_str), result_test_str)

    @mock.patch('nginxctl.nginxCtl.get_conf_parameters')
    def test_nginx_conf(self, conf_param):
        n = nginxctl.nginxCtl()
        conf_param.return_value = {'--conf-path': '/etc/nginx/nginx.conf',
                                   '--lock-path': '/var/lock/nginx.lock'}
        assert n.get_nginx_conf() == '/etc/nginx/nginx.conf'
        assert n.get_nginx_lock() == '/var/lock/nginx.lock'

    def test_get_vhosts_info(self):
        test_vhost_content = "server {\n\
                                    listen 8080;\n\
                                    listen [::]:80;\n\
                                    server_name example.com;\n\
                                    root /var/www/html;\n\
                                    index index.html;\n\
                                    client_max_body_size 4G;\n\
                                    location /media {\n\
                                        alias   /production/example/media;\n\
                                        expires max;\n\
                                        access_log off;\n\
                                    }\n\
                                    # Error pages\n\
                                    error_page 500 502 503 504 /500.html;\n\
                                    location = /500.html {\n\
                                        root /production/example/static/;\n\
                                    }\n\
                                    access_log /var/log/nginx/example.access.log;\n\
                                    error_log /var/log/nginx/example.error.log;\n\
                                    }\n"
        vhost_file = tempfile.NamedTemporaryFile(delete=False)
        vhost_file.write(test_vhost_content)
        vhost_file.seek(0)
        n = nginxctl.nginxCtl()
        vhost_info = n._get_vhosts_info(vhost_file.name)
        servername = vhost_info[0]['servername']
        ip_port = vhost_info[0]['ip_port']
        self.assertEqual('example.com', servername)
        self.assertEqual(['8080', '[::]:80'], ip_port)
        vhost_file.close()


if __name__ == '__main__':
    unittest.main()
