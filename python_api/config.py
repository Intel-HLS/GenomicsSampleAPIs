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

import python_api.util as util


class MPIConfig():
    """
    Configuration for starting a MPI fetch in a multi-node scenario
    """
    MPIRUN = None
    HOSTS = None
    HOSTFLAG = None
    IF_INCLUDE = None
    ENV = None
    EXEC = None
    TEMP_DIR = None
    ID_MAPPING = None
    NUM_PROCESSES = None


def initMPIConfig(parser):
    """
    Initializes the MPIConfi static class from the config file 
    """
    if not parser.has_section("mpi"):
        return
    MPIConfig.MPIRUN = parser.get('mpi', 'MPIRUN')
    MPIConfig.HOSTS = parser.get('mpi', 'HOSTS')
    MPIConfig.HOSTFLAG = parser.get('mpi', 'HOSTFLAG')
    MPIConfig.EXEC = parser.get('mpi', 'EXECUTABLE')
    MPIConfig.TEMP_DIR = parser.get('mpi', 'TEMP_DIR')
    MPIConfig.ID_MAPPING = parser.get('mpi', 'LOADER_JSON')
    MPIConfig.NUM_PROCESSES = parser.get('mpi', 'NUM_PROCESSES')

    if parser.has_option('mpi', 'BTL_TCP_IF_INCLUDE'):
        MPIConfig.IF_INCLUDE = parser.get('mpi', 'BTL_TCP_IF_INCLUDE')
    if parser.has_option('mpi', 'INCLUDE_ENV'):
        MPIConfig.ENV = parser.get('mpi', 'INCLUDE_ENV')


def initConfig(configFile):
    """
    Initialize the configuration variables from the configFile
    """
    parser = ConfigParser.RawConfigParser()
    parser.read(configFile)

    debug = parser.get('mode', 'DEBUG')
    if debug == 'ON':
        util.DEBUG = True
    else:
        util.DEBUG = False

    initMPIConfig(parser)
