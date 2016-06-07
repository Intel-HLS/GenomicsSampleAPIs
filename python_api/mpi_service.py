import python_api.util as util

import json, random, os
import subprocess

class Aggregator():
  """
  Aggregator has methods that is overloaded from the API class to send the request 
  to multiple end-points using MPI and fetch tile db data
  """
  def __init__(self, config):
    self.mpiConfig  = config.MPIConfig()
    with open(self.mpiConfig.ID_MAPPING, 'r') as fp:
      self.initSamplesInfo(json.load(fp))

  def initSamplesInfo(self, loader_json):
    """
    Looks up loader_json and updates the dictionary for future queries
    """
    if "callset_mapping_file" in loader_json:
      callset_mapping_file = loader_json["callset_mapping_file"]
    else:
      with open(loader_json["vid_mapping_file"]) as fp:
        callset_mapping_file = json.load(fp)["callset_mapping_file"]
    with open(callset_mapping_file, 'r') as fp:
      callset_mapping_json = json.load(fp)["callsets"]

    if "limit_callset_row_idx" in loader_json:
      row_idx_limit = long(loader_json["limit_callset_row_idx"])
    else:
      row_idx_limit = len(callset_mapping_json)

    self.sampleId2Name = dict()
    self.sampleName2Id = dict()

    self.numSamples = 0
    for sample_name in callset_mapping_json.keys():
      tile_row_id = callset_mapping_json[sample_name]["row_idx"]
      if tile_row_id > row_idx_limit:
        continue
      self.sampleName2Id[sample_name] = tile_row_id
      self.sampleId2Name[tile_row_id] = sample_name
      self.numSamples += 1

  def getNumSamples(self):
    """
    API to get the total number of samples in the given Tile DB.
    """
    return self.numSamples

  def getSampleNames(self, sampleIds):
    result = [None] * len(sampleIds)
    index = 0
    for sampleId in sampleIds:
      if sampleId in self.sampleId2Name:
        result[index] = self.sampleId2Name[sampleId]
      index += 1
    return result

  def getValidPositions(self, chromosome, start, end):
    attribute = "REF"
    result = self.getPositionRange(chromosome, start, end, [attribute])
    data = json.loads(result)
    del data[attribute]
    # Flatten the start and end
    data['POSITION'], data['END'] = util.flattenStartEnd(data['POSITION'], data['END'])

    return json.dumps(data)

  def getPosition(self, chromosome, position, attribute_list):
    if isinstance(chromosome, list):
      if len(chromosome) == len(position) :
        return self.getMultiPosition(chromosome, position, None, attribute_list, "Positions-JSON")
      else:
        raise ValueError("len(chromosome) ({0}) != len(position) ({1}) ".format(len(chromosome), len(position)))
    else:
      return self.getMultiPosition([chromosome], [position], None, attribute_list, "Cotton-JSON")

  def getMultiPosition(self, chromosome, position, end, attribute_list, output_format):
    if 'END' in attribute_list:
      attribute_list.remove('END')
    if 'POSITION' in attribute_list:
      attribute_list.remove('POSITION')

    jsonFile = self.createJson(chromosome = chromosome, start = position, end = end, attributes = attribute_list)
    if util.DEBUG:
      util.log("JSON File: {0}".format(jsonFile))

    result = self.runMPI(jsonFile, output_format)
    if not util.DEBUG:
      subprocess.call(["rm", jsonFile])

    if util.DEBUG:
      util.log("[MPI_Service] Received data from mpirun")

    return result

  def getPositionRange(self, chromosome, position, end, attribute_list):
    if isinstance(chromosome, list):
      if len(chromosome) == len(position) and len(chromosome) == len(end):
        return self.getMultiPosition(chromosome, position, end, attribute_list, "Positions-JSON")
      else:
        raise ValueError("len(chromosome) ({0}), len(position) ({1}), len(end) ({2}) MUST be equal".format(len(chromosome), len(position), len(end)))
    else:
      return self.getMultiPosition([chromosome], [position], [end], attribute_list, "Cotton-JSON")

  def runMPI(self, jsonFile, output_format):
    if util.DEBUG:
      util.log("[Run MPI] Starting mpirun subprocess")
    processArgs = [self.mpiConfig.MPIRUN, "-np", str(self.mpiConfig.NUM_PROCESSES),
                      self.mpiConfig.HOSTFLAG, self.mpiConfig.HOSTS]
    if self.mpiConfig.IF_INCLUDE != None:
      processArgs.extend(["--mca", "btl_tcp_if_include", self.mpiConfig.IF_INCLUDE])
    if self.mpiConfig.ENV != None:
      processArgs.extend(["-x", self.mpiConfig.ENV])

    processArgs.extend([self.mpiConfig.EXEC, "-j", jsonFile, "-O", output_format, "-l", self.mpiConfig.ID_MAPPING])
    if util.DEBUG:
      util.log("MPI Args: {0} ".format(processArgs))
    pipe = subprocess.Popen(processArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = pipe.communicate()

    if pipe.returncode != 0:
      raise Exception("MPI process failed with stdout: \n-- \n{0} \n--\nstderr: \n--\n{1} \n--".format(output, error))

    return output

  def createJson(self, chromosome, start, end, attributes):
    """
    Creates the JSON file which is the input to the MPI process
    and returns the file name
    """
    jsonObj = dict()

    jsonObj["query_attributes"] = attributes

    query_positions = [None] * len(chromosome)
    if end == None or len(end) == 0 or start == end:
      for i in xrange(0, len(chromosome)):
        query_positions[i] = dict({chromosome[i] : start[i]})
    else:
      for i in xrange(0, len(chromosome)):
        query_positions[i] = dict({chromosome[i] : [start[i], end[i]]})
    jsonObj["query_column_ranges"] = [query_positions]

    datetime = util.now()
    outFile = "_".join(str(v) for v in [datetime.second, datetime.microsecond, random.randint(0, 100000000),".json"])
    outFile = os.path.join(self.mpiConfig.TEMP_DIR, outFile)

    with open(outFile, 'w') as outFP:
      outFP.write(json.dumps(jsonObj, indent=2))

    return outFile
