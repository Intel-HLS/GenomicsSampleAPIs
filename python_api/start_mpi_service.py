#!/usr/bin/env python 

import Pyro4
import os, sys
from python_api.mpi_service import Aggregator
import python_api.config as config

def main(host):
  basePath = os.path.dirname(os.path.realpath(sys.argv[0]))

  config.initConfig(os.path.join(basePath, 'tiledb.cfg'))
  
  Pyro4.Daemon.serveSimple(
    { Aggregator(config) : "tile.master.{0}".format(host) }, 
    ns = True, host=host )

if __name__ == '__main__':
  import argparse
  description = "This script starts he Pyro4 master for the Python API"
  parser = argparse.ArgumentParser(description = description)

  parser.add_argument("-H", "--host", required=True, type=str,
                      default=os.getenv('HOSTNAME'),
                      help="Hostname or the ip that the slave is running on")
  args = parser.parse_args()

  main(args.host)