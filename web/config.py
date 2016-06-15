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
