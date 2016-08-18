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

import Pyro4
import os
import sys
from python_api.mpi_service import Aggregator
import python_api.config as config


def main(host):
    basePath = os.path.dirname(os.path.realpath(sys.argv[0]))

    config.initConfig(os.path.join(basePath, 'tiledb.cfg'))

    Pyro4.Daemon.serveSimple(
        {Aggregator(config): "tile.master.{0}".format(host)},
        ns=True, host=host)

if __name__ == '__main__':
    import argparse
    description = "This script starts he Pyro4 master for the Python API"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-H", "--host", required=True, type=str,
                        default=os.getenv('HOSTNAME'),
                        help="Hostname or the ip that the slave is running on")
    args = parser.parse_args()

    main(args.host)
