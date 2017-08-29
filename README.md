<h1>NginxCtl</h1>

The nginxctl allows to control some of the functionlities of nginx daemon.
This tool is similar to apachectl and which main feature is to list
domains configured on a nginx webserver.

<h2>Download/Installation</h2>

```
wget https://raw.githubusercontent.com/LukeShirnia/nginxctl/master/nginxctl.py -O nginxctl.py 
python nginxctl.py
```


<h2>Usage</h2>

```
Usage: nginxctl.py [option]
Example: nginxctl.py -v


Available options:
	-S list nginx vhosts
	-t configuration test
	-h help
```

Here is an example of running the option to discover virtual hosts

```
# python nginxctl.py -S
nginx vhost configuration:
*:8080 is a Virtualhost
	port 8080 namevhost  example.com  (/etc/nginx/sites-enabled/example.com:5)
[::]:80 is a Virtualhost
	port 80 namevhost  example.com  (/etc/nginx/sites-enabled/example.com:5)

```
