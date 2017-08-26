#!/usr/bin/env python
import subprocess
import re
import sys
import os
import urllib2


class bcolors:
    """
    This class is to display differnet colour fonts
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    UNDERLINE = '\033[4m'


class nginxCtl:
    """
    A class for nginxCtl functionalities
    """


    def get_conf_parameters(self):
        """
        Finds nginx configuration parameters

        :returns: list of nginx configuration parameters
        """
        conf = "nginx -V 2>&1 | grep 'configure arguments:'"
        p = subprocess.Popen(
            conf, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, err = p.communicate()
        output = re.sub('configure arguments:', '', output)
        dict = {}
        for item in output.split(" "):
            if len(item.split("=")) == 2:
                dict[item.split("=")[0]] = item.split("=")[1]
        return dict


    def get_nginx_conf(self):
        """
        :returns: nginx configuration path location
        """
        try:
            return self.get_conf_parameters()['--conf-path']
        except KeyError:
            print "nginx is not installed!!!"
            sys.exit()


    def configtest_nginx(self):
        """
        Ensure there is no syntax errors are reported.
        The 'nginx -t' command is used for this.
        """
        p = subprocess.Popen(
            "nginx -t",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
            )
        output, err = p.communicate()
        print err
    
   
    def full_status(self):
        """
        Checks against /server-status for server statistics
        """
        try:
            request = urllib2.urlopen('http://localhost/server-status')
            if str(request.getcode()) == "200":
                print """
Nginx Server Status
-------------------
%s
                    """ % request.read()
            else:
                print """
Nginx Server Status
-------------------
server-status did not return a 200 response.
                    """
        except (urllib2.HTTPError, urllib2.URLError):
            print """
Nginx Server Status
-------------------
Attempt to query /server-status returned an error
                """


    def _get_vhosts(self):
        """
        get vhosts
        """
        ret = []
        for f in self._get_all_config():
            ret += self._get_vhosts_info(f)
        return ret


    def _strip_line(self, path, remove=None):
        """ Removes any trailing semicolons, and all quotes from a string
        """
        if remove is None:
            remove = ['"', "'", ';']
        for c in remove:
            if c in path:
                path = path.replace(c, '')

        return path


    def _get_full_path(self, path, root, parent=None):
        """ Returns a potentially relative path and returns an absolute one
            either relative to parent or root, whichever exists in that order
        """
        if os.path.isabs(path) and os.path.exists(path):
            return path

        if parent:
            if os.path.isfile(parent):
                parent = os.path.dirname(parent)
            candidate_path = os.path.join(parent, path)
            if os.path.isabs(candidate_path) and os.path.exists(candidate_path):
                return candidate_path

        candidate_path = os.path.join(root, path)
        if os.path.isabs(candidate_path) and os.path.exists(candidate_path):
            return candidate_path

        return path


    def _get_includes_line(self, line, parent, root):
        """ Reads a config line, starting with 'include', and returns a list
            of files this include corresponds to. Expands relative paths,
            unglobs globs etc.
        """
        path = self._strip_line(line.split()[1])
        orig_path = path
        included_from_dir = os.path.dirname(parent)

        if not os.path.isabs(path):
            """ Path is relative - first check if path is
                relative to 'current directory' """
            path = os.path.join(included_from_dir, self._strip_line(path))
            if not os.path.exists(os.path.dirname(path)) or not os.path.isfile(path):
                """ If not, it might be relative to the root """
                path = os.path.join(root, orig_path)

        if os.path.isfile(path):
            return [path]
        elif '/*' not in path and not os.path.exists(path):
            """ File doesn't actually exist - probably IncludeOptional """
            return []

        """ At this point we have an absolute path to a basedir which
            exists, which is globbed
        """
        basedir, extension = path.split('/*')
        try:
            if extension:
                return [
                    os.path.join(basedir, f) for f in os.listdir(
                        basedir) if f.endswith(extension)]

            return [os.path.join(basedir, f) for f in os.listdir(basedir)]
        except OSError:
            return []


    def _get_all_config(self, config_file=None):
        """
        Reads all config files, starting from the main one, expands all
        includes and returns all config in the correct order as a list.
        """
        config_file = "/etc/nginx/nginx.conf" if config_file is None else config_file
        ret = [config_file]

        config_data = open(config_file, 'r').readlines()

        for line in [line.strip().strip(';') for line in config_data]:
            if line.startswith('#'):
                continue
            line = line.split('#')[0]
            if line.startswith('include'):
                includes = self._get_includes_line(line,
                                                   config_file,
                                                   "/etc/nginx/")
                for include in includes:
                    try:
                        ret += self._get_all_config(include)
                    except IOError:
                        pass
        return ret


    def _get_vhosts_info(self, config_file):
        server_block_boundry = []
        server_block_boundry_list = []
        vhost_data = open(config_file, "r").readlines()
        open_brackets = 0
        found_server_block = False
        for line_number, line in enumerate(vhost_data):
            if line.startswith('#'):
                continue
            line = line.split('#')[0]
            line = line.strip().strip(';')
            if re.match(r"server.*{", line):
                server_block_boundry.append(line_number)
                found_server_block = True
            if '{' in line:
                open_brackets += 1
            if '}' in line:
                open_brackets -= 1
            if open_brackets == 0 and found_server_block:
                server_block_boundry.append(line_number)
                server_block_boundry_list.append(server_block_boundry)
                server_block_boundry = []
                found_server_block = False

        server_dict_ret = []
        for server_block in server_block_boundry_list:
            alias = []
            ip_port = []
            server_name_found = False
            server_dict = {}
            for line_num, li in enumerate(vhost_data, start=server_block[0]):
                l = vhost_data[line_num]
                if line_num >= server_block[1]:
                    server_dict['alias'] = alias
                    server_dict['l_num'] = server_block[0]
                    server_dict['config_file'] = config_file
                    server_dict['ip_port'] = ip_port
                    server_dict_ret.append(server_dict)
                    server_name_found = False
                    break

                if l.startswith('#'):
                    continue
                l = l.split('#')[0]
                l = l.strip().strip(';')

                if l.startswith('server_name') and server_name_found:
                    alias += l.split()[1:]

                if l.startswith('server_name'):
                    server_dict['servername'] = "default_server_name" if l.split()[1] == "_" else l.split()[1]
                    server_name_found = True
                    if len(l.split()) >= 2:
                        alias += l.split()[2:]
                if l.startswith('listen'):
                    ip_port.append(l.split()[1])
        return server_dict_ret


    def get_vhosts(self):
        vhosts_list = self._get_vhosts()
        print "%snginx vhost configuration:%s" % (bcolors.BOLD, bcolors.ENDC)
        for vhost in vhosts_list:
            ip_ports = vhost['ip_port']
            for ip_port_x in ip_ports:
                if '[::]' in ip_port_x:
                    pattern = re.compile(r'(\[::\]):(\d{2,5})')
                    pattern_res = re.match(pattern, ip_port_x)
                    ip = pattern_res.groups()[0]
                    port = pattern_res.groups()[1]
                else:
                    ip_port = ip_port_x.split(':')
                    try:
                        ip = ip_port[0]
                        port = ip_port[1]
                    except:
                        ip = '*'
                        port = ip_port[0]
                servername = vhost.get('servername', None)
                serveralias = vhost.get('alias', None)
                line_number = vhost.get('l_num', None)
                config_file = vhost.get('config_file', None)
                print "%s:%s is a Virtualhost" % (ip, port)
                print "\tport %s namevhost %s %s %s (%s:%s)" % (port,
                                                                bcolors.OKGREEN,
                                                                servername,
                                                                bcolors.ENDC,
                                                                config_file,
                                                                line_number)
                for alias in serveralias:
                    print "\t\talias %s %s %s" % (bcolors.CYAN,
                                                  alias,
                                                  bcolors.ENDC)


def main():
    n = nginxCtl()

    def usage():
        print ("Usage: %s [option]" % sys.argv[0])
        print ("Example: %s -S" % sys.argv[0])
        print "\n"
        print "Available options:"
        print "\t-S list nginx vhosts"
        print "\t-t configuration test"
        print "\t-k status|fullstatus"
        print "\t-h help"


    commandsDict = {"-S": n.get_vhosts,
                    "-t": n.configtest_nginx,
                    "-h": usage}
    subcommandsDict = {"fullstatus": n.full_status}
    allCommandsDict = {"-S": n.get_vhosts,
                       "-t": n.configtest_nginx,
                       "-k": usage,
                       "-h": usage,
                       "fullstatus": n.full_status}
    commandline_args = sys.argv[1:]
    if len(commandline_args) == 1:
        for argument in commandline_args:
            if argument in allCommandsDict:
                allCommandsDict[argument]()
            else:
                usage()
    elif len(commandline_args) == 2:
        if sys.argv[1] == "-k":
            flag = sys.argv[2:]
            for f in flag:
                if f in subcommandsDict:
                    subcommandsDict[f]()
        else:
            usage()
    else:
        usage()
if __name__ == "__main__":
    main()
