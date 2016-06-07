#!/usr/bin/env python 

import os, sys
import json

import Pyro4, Pyro4.util
sys.excepthook = Pyro4.util.excepthook

def process(chromosome, position, attributes):
  nameServer = Pyro4.locateNS()
  nodes = nameServer.list(regex = "tile.master*")

  for name, uri in nodes.items():
    api = Pyro4.Proxy(uri)

    print "Results from {0} ".format(name)

    data =  api.getPosition(chromosome, position, attributes)
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
  parser = argparse.ArgumentParser(description = description)

  parser.add_argument("-c", "--chromosome", required=True, type=str, nargs='+', help="Chromosome")
  parser.add_argument("-p", "--position", required=True, type=long, nargs='+',
                      help="position in the chromosome")
  parser.add_argument("-a", "--attributes", nargs='+', required=True, type=str, 
                      help="List of attributes to fetch")

  args = parser.parse_args()

  process(args.chromosome, args.position, args.attributes)