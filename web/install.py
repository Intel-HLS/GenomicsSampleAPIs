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

#!/usr/bin/env python

import ConfigParser
import os
import sys
import site
import grp
import argparse


def installPaths(ga4ghPath):
    # Add path into the python site-packages of this user
    py_site_packages = site.USER_SITE

    if not os.path.exists(py_site_packages):
        os.makedirs(py_site_packages)

    pathFile = os.path.join(py_site_packages, "GA4GHAPI.pth")
    print "Setting up paths @ {0} ".format(pathFile)

    fp = open(pathFile, 'w')
    fp.write(ga4ghPath + "\n")
    fp.close()

def updateConfigs(basePath, ga4ghPath):
    configFile = os.path.join(ga4ghPath, "ga4gh_test.conf")
    print 'configFile'
    print "Updating Config file @ {0} ".format(configFile)

    parser = ConfigParser.RawConfigParser()
    parser.read(configFile)

    # consider having this part fill from the import process
    if(parser.has_section('auto_configuration')):
        parser.set('auto_configuration', 'SEARCHLIB',
                   getPath(basePath, "search_library/lib/libquery.so"))

    with open(configFile, 'w') as fp:
        parser.write(fp)

    return parser.get('virtualenv', 'site_packages')


def getPath(basePath, appendPath):
    set_file = os.path.join(basePath, appendPath)
    if not os.path.exists(set_file):
        raise Exception("{0} does not exist".format(set_file))
    return set_file


def getHttpdConf(sockpath="unix:/var/uwsgi/ga4gh.sock", port=8008):
    print ""
    print "try this in your /etc/nginx/conf.d directory"
    print "you may adjust socket and port to you use"
    print """
  server {
      listen %s;
      server_name localhost;
      charset     utf-8;
      client_max_body_size 100M;

      location / {
          include uwsgi_params;
          uwsgi_pass %s;
      }
  }
  """ % (port, sockpath)

    print "copy ga4gh.service to your /etc/systemd/system/ga4gh.service"
    print ""


def getuwsgiConf(basePath, sockpath="/var/uwsgi/ga4gh.sock"):

    iniPath = os.path.join(basePath, "web")
    myuser = os.getenv('USER')

    # if virtual_env set in environment, else pull from config
    configFile = os.path.join(basePath, "web/ga4gh_test.conf")
    parser = ConfigParser.RawConfigParser()
    parser.read(configFile)
    if parser.has_section('virtualenv'):
        venv = parser.get('virtualenv', 'virtualenv')

    virtualenv = os.getenv('VIRTUAL_ENV', venv)

    configFile = os.path.join(iniPath, "ga4gh.ini")

    # fix this logic, if it doesn't exist create it - if it does overwrite it

    parser = ConfigParser.RawConfigParser()
    parser.read(configFile)
    if(not parser.has_section('uwsgi')):
        parser.add_section('uwsgi')

    parser.set('uwsgi', 'master', 'true')
    parser.set('uwsgi', 'socket', sockpath)
    parser.set('uwsgi', 'base', iniPath)
    parser.set('uwsgi', 'home', virtualenv)
    parser.set('uwsgi', 'env', "PYTHONPATH=" + iniPath)
    parser.set('uwsgi', 'uid', myuser)
    parser.set('uwsgi', 'gid', grp.getgrnam(myuser).gr_name)
    parser.set('uwsgi', 'wsgi_file', 'wsgi.py')
    parser.set('uwsgi', 'module', 'wsgi')
    parser.set('uwsgi', 'callable', 'application')
    parser.set('uwsgi', 'chmod-socket', '666')
    parser.set('uwsgi', 'logger', 'syslog')
    parser.set('uwsgi', 'no-default-app', 'true')
    parser.set('uwsgi', 'need-app', 'true')

    with open(configFile, 'w') as fp:
        parser.write(fp)

    configFile = os.path.join(iniPath, "ga4gh.service")

    bindir = os.path.join(virtualenv, "bin")

    parser = ConfigParser.ConfigParser()
    parser.optionxform = str
    parser.read(configFile)

    if(not parser.has_section('Service')):
        parser.add_section('Service')

    parser.set('Service', 'User', myuser)
    parser.set('Service', 'Group', grp.getgrnam(myuser).gr_name)
    parser.set('Service', 'WorkdingDirectory', basePath)
    parser.set('Service', 'Environment', "PATH=" + bindir +
               ' LD_LIBRARY_PATH=/usr/lib64/openmpi/lib')
    parser.set('Service', 'ExecStart', os.path.join(
        bindir, "uwsgi") + " --ini " + os.path.join(iniPath, "ga4gh.ini"))

    with open(configFile, 'w') as fp:
        parser.write(fp)

if __name__ == "__main__":
    # Get the installation path for the APIs repo
    apar = argparse.ArgumentParser()

    apar.add_argument(
        "-p",
        "--port",
        type=int,
        default=8008,
        help="port for web server")

    apar.add_argument(
        "-s",
        "--socket",
        type=str,
        default="unix:/var/uwsgi/ga4gh.sock",
        help="string with socket information for uwsgi")

    args = apar.parse_args()
    listenPort = args.port
    socket = args.socket

    basePath = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
    ga4ghPath = os.path.join(basePath, "web")

    installPaths(ga4ghPath)
    updateConfigs(basePath, ga4ghPath)
    getHttpdConf(sockpath=socket, port=listenPort)
    getuwsgiConf(basePath)
    print "Installation Complete"
