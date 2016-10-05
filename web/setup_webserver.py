#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
  The MIT License (MIT)
  Copyright (c) 2016 Intel Corporation

  Permission is hereby granted, free of charge, to any person obtaining a copy of 
  this software and associated documentation files (the "Software"), to deal in 
  the Software without restriction, including without limitation the rights to 
  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
  the Software, and to permit persons to whom the Software is furnished to do so, 
  subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all 
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""


import ConfigParser
import os
import re
import subprocess
import sys

import argparse
import stat


class WebServerBuilder:

    def __init__(
        self,
        port,
        socket_path,
        array_name,
        service_directory,
        service_extension,
        nginx_conf_directory,
        ):

        self.port = str(port)
        self.socket_path = socket_path
        self.array_name = array_name
        self.uwsgi_socket_path = os.path.join(self.socket_path,
                'ga4gh_{}.sock'.format(self.array_name))
        self.service_directory = service_directory
        self.service_extension = service_extension
        self.nginx_conf_directory = nginx_conf_directory
        self.webserver_path = \
            os.path.dirname(os.path.realpath(sys.argv[0]))

    def setup_web_server(self, skip_services):
        try:
            self.setup_uwsgi_ini()
            self.setup_uwsgi_log()
            self.setup_webserver_conf()
            self.setup_ga4gh_service()
            self.setup_nginx_conf()
        except Exception, e:
            raise Exception('''ERROR creating files.
    Check permissions on folders.'
    Run with sudo in order to write files to system paths'

ERROR LOG:
{}'''.format(e))

        if not skip_services:
            try:
                run_command(['sudo', 'systemctl', 'daemon-reload'])
                run_command(['sudo', 'service',
                            'ga4gh_{}'.format(self.array_name),
                            'restart'])
                run_command(['sudo', 'service', 'nginx', 'restart'])
            except Exception, e:
                raise Exceception('''
ERROR: Unable to restart services.
Check sudo permissions and/or your Linux distribution manual to run equivalents for these commands:
    systemctl daemon-reload
    service ga4gh_{0} restart
    service nginx restart

ERROR LOG:
{1}'''.format(self.array_name,
                                  e))

    def setup_uwsgi_ini(self):
        input_file = os.path.join(self.webserver_path, 'templates',
                                  'ga4gh.ini.template')
        output_file = os.path.join(self.webserver_path,
                                   'ga4gh_{}.ini'.format(self.array_name))
        writeConfig(input_file, output_file, [('<Array_Name>',
                    self.array_name), ('<uwsgi_socket_path>',
                    self.uwsgi_socket_path)])

    def setup_webserver_conf(self):
        input_file = os.path.join(self.webserver_path, 'templates',
                                  'ga4gh.cfg.template')
        output_file = os.path.join(self.webserver_path,
                                   'ga4gh_{}.conf'.format(self.array_name))
        writeConfig(input_file, output_file, [('<Array_Name>',
                    self.array_name)])

    def setup_uwsgi_log(self):
        output_file = os.path.join('/var/log/uwsgi',
                                   'uwsgi_{}.log'.format(self.array_name))
        with open(output_file, 'a') as outFP:
            pass
        os.chmod(output_file, stat.S_IRUSR | stat.S_IWUSR
                 | stat.S_IRGRP | stat.S_IWGRP)
        print '[INFO] Updated: {}'.format(output_file)

    def setup_ga4gh_service(self):
        input_file = os.path.join(self.webserver_path, 'templates',
                                  'ga4gh.{}.template'.format(self.service_extension))
        temporary_file = os.path.join(self.webserver_path, 'templates',
                'ga4gh_{0}.{1}'.format(self.array_name,
                self.service_extension))
        output_file = os.path.join(self.service_directory,
                                   'ga4gh_{0}.{1}'.format(self.array_name,
                                   self.service_extension))
        writeConfig(input_file, temporary_file, [('<Array_Name>',
                    self.array_name)])

        run_command(['sudo', 'mv', temporary_file, output_file])

    def setup_nginx_conf(self):
        input_file = os.path.join(self.webserver_path, 'templates',
                                  'nginx_ga4gh.conf.template')
        temporary_file = os.path.join(self.webserver_path, 'templates',
                'nginx_ga4gh_{}.conf'.format(self.array_name))
        output_file = os.path.join(self.nginx_conf_directory,
                                   'nginx_ga4gh_{}.conf'.format(self.array_name))
        writeConfig(input_file, temporary_file, [('<uwsgi_socket_path>'
                    , self.uwsgi_socket_path), ('<PORT>', self.port)])
        run_command(['sudo', 'mv', temporary_file, output_file])


def run_command(processArgs):
    print '[INFO] Executing: {}'.format(processArgs)
    pipe = subprocess.Popen(processArgs, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (output, error) = pipe.communicate()

    if pipe.returncode != 0:
        raise Exception('''CMD: {0} 
OUTPUT: {1}

ERROR: {2}'''.format(' '.join(processArgs),
                        output, error))


def writeConfig(input_file, output_file, substitute_strings):

    with open(input_file, 'r') as inFP:
        with open(output_file, 'w') as outFP:
            for line in inFP:
                for (pattern, repl) in substitute_strings:
                    line = re.sub(pattern, repl, line)
                outFP.write(line)
    print '[INFO] Updated: {}'.format(output_file)


if __name__ == '__main__':
    parser = \
        argparse.ArgumentParser(description='Uses the templates from Ansible to bring up a web server'
                                )

    parser.add_argument('-p', '--port', type=int, required=True,
                        help='Port to run the web server at')
    parser.add_argument('-s', '--socket_path', type=str, required=True,
                        help='Path to where the uwsgi unix socket needs to be created'
                        )
    parser.add_argument('-a', '--array_name', type=str, required=True,
                        help='Name of the array')
    parser.add_argument('-d', '--service_directory', type=str,
                        default='/etc/systemd/system',
                        help='Path to where the system services need to be installed'
                        )
    parser.add_argument('-e', '--service_extension', default='service',
                        help='File extension for system services')
    parser.add_argument('-n', '--nginx_conf_directory', type=str,
                        default='/etc/nginx/conf.d/',
                        help='Path to where the nginx conf need to be')
    parser.add_argument('-x', '--skip_services', action='store_true',
                        help='Set this if service restarts will be handled outside this script'
                        )

    args = parser.parse_args()

    builder = WebServerBuilder(
        args.port,
        args.socket_path,
        args.array_name,
        args.service_directory,
        args.service_extension,
        args.nginx_conf_directory,
        )
    builder.setup_web_server(args.skip_services)
