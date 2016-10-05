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
import json

import Pyro4
import Pyro4.util
sys.excepthook = Pyro4.util.excepthook


def process(chromosome, position, attributes):
    nameServer = Pyro4.locateNS()
    nodes = nameServer.list(regex="tile.master*")

    for name, uri in nodes.items():
        api = Pyro4.Proxy(uri)

        print "Results from {0} ".format(name)

        data = api.getPosition(chromosome, position, attributes)
        data = json.loads(data)

        totalSamples = 0

        print "Contig\tPosition\t#Samples"
        for contig in data.keys():
            for pos in data[contig].keys():
                totalSamples += len(data[contig][pos]['indices'])
                print "{0} \t{1} \t{2} ".format(contig, pos, len(data[contig][pos]['indices']))

        if totalSamples == 0:
            return 0
        print "Example: "

        # Using sample index 0 as an example
        sample_index = 0
        result = data[chromosome[0]][str(position[0])]
        print "\t Sample Id : {0} ".format(result['indices'][sample_index])
        print "\t Attribute \tValue"
        for attribute in attributes:
            print "\t {0} \t\t {1} ".format(attribute, result[attribute][sample_index])

        print

    return 0

if __name__ == '__main__':
    import argparse
    description = "Example on how to use the Python API. "
    description += "Sample Query: {0} -c 1 -p 100 \
                    -a ALT REF QUAL PL".format(sys.argv[0])
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-c", "--chromosome", required=True,
                        type=str, nargs='+', help="Chromosome")
    parser.add_argument(
        "-p",
        "--position",
        required=True,
        type=long,
        nargs='+',
        help="position in the chromosome")
    parser.add_argument(
        "-a",
        "--attributes",
        nargs='+',
        required=True,
        type=str,
        help="List of attributes to fetch")

    args = parser.parse_args()

    process(args.chromosome, args.position, args.attributes)
