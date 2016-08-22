#!/usr/bin/env python
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


import sys
import Pyro4
import Pyro4.util
import json

sys.excepthook = Pyro4.util.excepthook

import python_api.util as util


def process(chromosome, start, end, attributes):
    nameServer = Pyro4.locateNS()
    masters = nameServer.list(regex="tile.master*")

    for name, uri in masters.items():
        api = Pyro4.Proxy(uri)
        num_samples = api.getNumSamples()
        util.log("Total Samples in {0} = {1} ".format(name, num_samples))

        util.log("Results from {0}".format(name))

        if end is not None:
            data = api.getValidPositions(chromosome, start, end)
            data = json.loads(data)
            print "Valid indices : {0}".format(data['indices'])
            print "Valid Positions : \n\tStart:{0} \n\tEnd:{1} ".format(data['POSITION'], data['END'])

            data = api.getPositionRange(chromosome, start, end, attributes)
        else:
            data = api.getPosition(chromosome, start, attributes)
        data = json.loads(data)
        util.log("{1}: Sample Names Received : {0} ".format(
            api.getSampleNames(data['indices']), name))
        if len(data) > 0:
            sample_index = 0
            print "Example:"
            print "\t Sample Id : {0} ".format(data['indices'][sample_index])
            print "\t Attribute \tValue"
            for attribute in attributes:
                print "\t {0} \t\t {1} ".format(attribute, data[attribute][sample_index])

        util.log("{1}: Total Samples Received : {0} ".format(
            len(data['indices']), name))

    return 0

if __name__ == '__main__':
    import argparse
    description = "Example on how to use the Python API. "
    description += "Sample Query: {0} -c 10 -s 100 -e 100000 \
                    -a ALT REF QUAL PL AC AN AF".format(sys.argv[0])
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-c", "--chromosome", required=True,
                        type=str, help="Chromosome")
    parser.add_argument("-s", "--start", required=True,
                        type=long, help="start position")
    parser.add_argument("-e", "--end", required=False,
                        type=long, help="end position")
    parser.add_argument(
        "-a",
        "--attributes",
        nargs='+',
        required=True,
        type=str,
        help="List of attributes to fetch")

    args = parser.parse_args()

    process(args.chromosome, args.start, args.end, args.attributes)
