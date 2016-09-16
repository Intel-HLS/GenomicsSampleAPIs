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

import os
import ConfigParser


class LoadedConfig(object):
    SEARCHLIB = None
    BASEPATH = None
    WORKSPACE = None
    ARRAYNAME = None
    FIELDS = None
    SQLALCHEMY_DATABASE_URI = None
    DEBUG = None
    HOST = None
    VIRTUALENV = None
    SITE_PACKAGES = None


def initConfig(conf_file):
    conf_file = os.getenv('GA4GH_CONF', conf_file)
    configParser = ConfigParser.RawConfigParser()
    configParser.read(conf_file)
    LoadedConfig.WORKSPACE = configParser.get('tiledb', 'WORKSPACE')
    LoadedConfig.ARRAYNAME = configParser.get('tiledb', 'ARRAYNAME')
    LoadedConfig.FIELDS = configParser.get('tiledb', 'FIELDS').split(',')
    LoadedConfig.SQLALCHEMY_DATABASE_URI = configParser.get(
        'tiledb', 'SQLALCHEMY_DATABASE_URI')

    LoadedConfig.SEARCHLIB = configParser.get(
        'auto_configuration', 'SEARCHLIB')

    LoadedConfig.DEBUG = configParser.get('web_configuration', 'DEBUG')
    LoadedConfig.HOST = configParser.get('web_configuration', 'HOST')

    LoadedConfig.VIRTUALENV = configParser.get('virtualenv', 'VIRTUALENV')
    LoadedConfig.SITE_PACKAGES = configParser.get(
        'virtualenv', 'SITE_PACKAGES')
