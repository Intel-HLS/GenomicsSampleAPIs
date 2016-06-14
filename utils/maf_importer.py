#!/usr/bin/env python

import sys, os, uuid, json, traceback
from multiprocessing import Pool

import utils.csvline as csvline
from utils.file2tile import File2Tile, IDX
import utils.helper as helper
from metadb.api import DBImport, DBQuery
from utils.configuration import ConfigReader
from metadb.api import DBImport
from metadb.models import CallSetToDBArrayAssociation

CSVLine = csvline.CSVLine

class MAF(File2Tile):
    """
    Class implementing the conversion from MAF to Tile DB CSV
    """

    def __init__(self, config_file):
        """
        Constructor takes the config file for the given input data
        """
        # reference to super object
        self.m_super = None

        # placeholder for values from previous line
        # csv line values
        self.prev_IndividualId = None
        self.prev_SourceSampleId = None
        self.prev_TargetSampleId = None
        self.prev_ChromosomePosition = None
        self.prev_TileDBPosition = None
        self.prev_TileDBValues = None
        self.prev_CallSetName = None
        self.prev_VariantSetId = None
        self.GT = None

        # metadb objects
        self.curr_Individual = None
        self.curr_SourceSample = None
        self.curr_TargetSample = None
        self.curr_CallSet = None

        # instance of the CSVLine object
        self.m_csv_line = None

        self.m_super = super(MAF, self)
        self.m_super.__init__(config_file)

        self.m_csv_line = CSVLine()

        self.PLOIDY = self.config.Constants['PLOIDY']

        self.dbimport = DBImport(self.config.DB_URI)
        self.dbquery = DBQuery(self.config.DB_URI)
        # Redundant to call register since all the info is registered already
        # But using it to get the vs.id to use
        dba, vs, rs = helper.registerWithMetadb(self.config)
        self.prev_VariantSetId = vs.id

    def generateCSV(self, inputFile, outFile, bVerbose = False):
        """
        Implements the MAF specifics to generate a CSV output
        """

        self.initFilePointers(inputFile, outFile)

        nLine = 0L
        try:
            while( self.parseNextLine() ):
                self.checkSample()
                nLine += 1
                if( bVerbose and (nLine % 50 == 0)):
                    progressPrint("@Line {0} in file {1}".format(nLine, inputFile))

            # Cleanup and write the last CSV Line
            self.writeCSVLine()
        except:
            print "\nFAILED execution @ line " + str(nLine)
            raise
        finally:
            # Close File Pointers
            self.closeFilePointers()

        # Reset to None in case the object is called to Generate CSV again
        self.prev_IndividualId = None
        self.prev_SourceSampleId = None
        self.prev_TargetSampleId = None

    def checkSample(self):
        """
        Compares the current sample and the stored previous sample to return a bool
        - If a new sample is identified, write the existing data, and copy current
        - If it is the same sample, then compare with previous and append if new
        """
        if( self.prev_SourceSampleId == None or self.prev_TargetSampleId == None):
            # first sample copy data
            self.saveCurrentData()
        elif( self.prev_SourceSampleId != self.SourceSampleId or
              self.prev_TargetSampleId != self.TargetSampleId or
              self.prev_CallSetName != self.CallSetName or
              self.prev_TileDBPosition != self.TileDBPosition or
              self.prev_IndividualId != self.IndividualId):
            # We have to write the current line and save a new line since the current
            # data differs by the SampleId, CallSetName, VariantSetName or TileDBPosition
            self.writeCSVLine()
            self.saveCurrentData()
        else:
            # This case is reached if the SampleId, CallSetName, TileDBPosition are
            # the same. Verify if there is a delta in the ALT field, then
            # append new data for fields whose type is an array
            # Picking ALT value at 0 since we know that MAF always has only one ALT per line.
            # If that is not the case, then this code needs to be updated
            if 'ALT' in self.TileDBValues.keys() \
              and self.TileDBValues['ALT'][0] not in self.prev_TileDBValues['ALT']:
                for key in self.TileDBValues.keys():
                    if( key in CSVLine.arrayFields ):
                        for value in self.TileDBValues[key]:
                            if 'GT' == key:
                                self.prev_TileDBValues[key].append(str(len(self.prev_TileDBValues[key]) + 1))
                                continue
                            self.prev_TileDBValues[key].append(value)

    def saveCurrentData(self):
        """
        Copies the current data into the prev_ variables
        """
        if (self.prev_SourceSampleId != self.SourceSampleId or
          self.prev_TargetSampleId != self.TargetSampleId or
          self.prev_IndividualId != self.IndividualId or
          self.prev_CallSetName != self.CallSetName):

            with self.dbimport.getSession() as metadb:

                self.prev_IndividualId = self.IndividualId
                self.prev_SourceSampleId = self.SourceSampleId
                self.prev_TargetSampleId = self.TargetSampleId

                self.curr_Individual = metadb.registerIndividual(guid=str(uuid.uuid4()), name=self.prev_IndividualId)
                self.curr_SourceSample = metadb.registerSample(guid=str(uuid.uuid4()), individual_guid=self.curr_Individual.guid, name=self.SourceSampleId, info={'type':'source'})
                self.curr_TargetSample = metadb.registerSample(guid=str(uuid.uuid4()), individual_guid=self.curr_Individual.guid, name=self.TargetSampleId, info={'type':'target'})

                self.prev_CallSetName = self.CallSetName # "CallSet_"+self.prev_TargetSampleId+"_"+self.prev_SourceSampleId

                self.curr_CallSet = metadb.registerCallSet(
                  guid=str(uuid.uuid4()),
                  source_sample_guid=self.curr_SourceSample.guid,
                  target_sample_guid=self.curr_TargetSample.guid,
                  workspace=self.config.TileDBSchema['workspace'],
                  array_name=self.config.TileDBSchema['array'],
                  name=self.prev_CallSetName,
                  variant_set_ids=[self.prev_VariantSetId]
                  )

            row_id = None
            with self.dbquery.getSession() as query:
                row_id = query.callSetIds2TileRowId([self.curr_CallSet.id],
                                                  self.config.TileDBSchema['workspace'],
                                                  self.config.TileDBSchema['array'],
                                                  isGUID = False
                                                  )[0]
            my_sample_name = "{0}-{1}-{2}-{3}".format(self.prev_IndividualId,
                                                      self.SourceSampleId,
                                                      self.TargetSampleId,
                                                      self.curr_CallSet.id)
            self.callset_mapping[my_sample_name] = {"row_idx": long(row_id),
                                                    "idx_in_file": long(row_id),
                                                    "filename": self.output_file}

        self.prev_ChromosomePosition = self.ChromosomePosition
        self.prev_TileDBPosition = self.TileDBPosition
        self.prev_TileDBValues = self.TileDBValues

    def writeCSVLine(self):
        """
        Creates the CSV object from the data set we have and writes it to disk
        """
        if( self.prev_SourceSampleId == None or self.prev_TargetSampleId == None or self.prev_IndividualId == None):
            return
        """
        Since MAF represents insertions and deletions with a '-' it needs to
        be processed before adding to the CSV Line
        1. Insertions
          Ref = get_ref_from_ensembl(MAF_chr, MAF_start-1, MAF_start - 1)
          Alt = Ref + Alt # Concatenate Ref and Alt
          Chr = MAF_Chr
          Start = MAF_Start - 1
          End = Start
        2. Deletions
          NewRef = get_ref_from_ensembl(MAF_chr, MAF_start-1, MAF_start-1)
          Ref = NewRef + MAF_Ref
          Alt = NewRef
          Chr = MAF_Chr
          Start = MAF_Start - 1
          End = MAF_End
        """
        # Insertion
        if( self.prev_TileDBValues["REF"] == "-" ):
            assembly = self.prev_ChromosomePosition[IDX.CHR_ASSEMBLY]
            chromosome = self.prev_ChromosomePosition[IDX.CHR_CHR]
            start = self.prev_ChromosomePosition[IDX.CHR_START] - 1
            end = start # self.prev_ChromosomePosition[IDX.CHR_END]

            ref = helper.getReference(assembly, chromosome, start, start)
            self.prev_TileDBValues["REF"] = ref
            index = 0
            for value in self.prev_TileDBValues["ALT"]:
                self.prev_TileDBValues["ALT"][index] = ref + value
                index += 1
            with self.dbquery.getSession() as query:
                self.prev_TileDBPosition = query.contig2Tile(self.array_idx, chromosome, [start, end])
        else:
            bFlag = False
            for value in self.prev_TileDBValues["ALT"]:
                if( value == "-" ):
                    bFlag = True
                    break
            if( bFlag ):
                assembly = self.prev_ChromosomePosition[IDX.CHR_ASSEMBLY]
                chromosome = self.prev_ChromosomePosition[IDX.CHR_CHR]
                start = self.prev_ChromosomePosition[IDX.CHR_START] - 1
                end = self.prev_ChromosomePosition[IDX.CHR_END]

                ref = helper.getReference(assembly, chromosome, start, start)
                self.prev_TileDBValues["REF"] = ref + self.prev_TileDBValues["REF"]
                index = 0
                for value in self.prev_TileDBValues["ALT"]:
                    if( value == "-" ):
                        self.prev_TileDBValues["ALT"][index] = ref
                    else:
                        self.prev_TileDBValues["ALT"][index] = ref + value
                    index += 1

                with self.dbquery.getSession() as query:
                    self.prev_TileDBPosition = query.contig2Tile(self.array_idx, chromosome, [start, end])

        row_id = None
        with self.dbquery.getSession() as query:
            row_id = query.callSetIds2TileRowId([self.curr_CallSet.id],
                                                self.config.TileDBSchema['workspace'],
                                                self.config.TileDBSchema['array'],
                                                isGUID = False
                                                )[0]
        self.m_csv_line.set("SampleId", row_id)
        self.m_csv_line.set("Location", self.prev_TileDBPosition[IDX.START])
        self.m_csv_line.set("End", self.prev_TileDBPosition[IDX.END])

        # set ALT value first to avoid failures from set function
        # Append "&" at the very end since that is what TileDB expects
        self.m_csv_line.set("ALT", self.prev_TileDBValues["ALT"])
        self.m_csv_line.set("PLOIDY", self.PLOIDY)

        for key in self.prev_TileDBValues.keys():
            if( key == "ALT" ):
                continue
            value = self.prev_TileDBValues[key]

            # If the field is an array type and there are no entires then
            # do not set it since the csvline.py would have taken care of it already
            if key in CSVLine.arrayFields and len(value) == 0 :
                continue

            # For MAF the GT value from the MAF file is the first entry and
            # the second is always a 0
            if( key == "GT" ):
                if len(self.prev_TileDBValues['ALT']) > self.PLOIDY:
                    value = ['-1', '-1']
                if len(value) == 1 :
                    value.append('0')
            # Cleanup Value
            if( value == "" ):
                value = csvline.EMPTYCHAR # Empty Char in Tile DB
            self.m_csv_line.set(key, value)
        # Write the line into file
        self.outFile.write(self.m_csv_line.getCSVLine() +  "\n")

    def checkCSV(self, inFile):
        """
        Sorts the output that was generated by the Location
        Checks if there are more than 1 entries for a sample at the Location
        and merges them
        """
        # print "Checking CSV File for global merging"
        import subprocess
        tmpFile = inFile + '.sorted'
        # Sort the file by column 2 which is the position
        with open(inFile + ".original", 'w') as tmpFP:
            subprocess.call(["cat", inFile], stdout=tmpFP)
        with open(tmpFile, 'w') as tmpFP:
            subprocess.call(["sort", "-k", "2", "-n", "-t", ",", inFile], stdout=tmpFP)

        p = subprocess.Popen(["wc", "-l", inFile], stdout=subprocess.PIPE)
        line_count = p.communicate()[0].split(' ')[0]
        count = 0

        with open(tmpFile, 'r') as inFP, open(inFile, 'w') as outFP:
            prev_Location = None
            csvMap = dict()

            for line in inFP:
                csv = csvline.CSVLine()
                csv.loadCSV(line)
                SId = csv.get('SampleId')
                Location = csv.get('Location')

                if Location != prev_Location :
                    for l in csvMap.values():
                        outFP.write(l.getCSVLine())
                        outFP.write('\n')
                    prev_Location = Location
                    del csvMap
                    csvMap = dict()
                    csvMap[SId] = csv
                else:
                    if SId in csvMap.keys():
                        self.combineCSVs(csvMap[SId], csv)
                    else:
                        csvMap[SId] = csv
                count += 1
            for l in csvMap.values():
                outFP.write(l.getCSVLine())
                outFP.write('\n')
        # print ""

    def combineCSVs(self, aggCSV, newCSV):
        """
        Combines the data from newCSV into aggCSV
        NOTE: PL, AD, SB values cannot be merged unless a method is written to
        merge them as a special case. They are ignored for now
        """
        isNew = False
        aggALT = aggCSV.get('ALT')
        for alt in newCSV.get('ALT'):
            if alt not in aggALT:
                isNew = True
                break
        if not isNew:
            return
        updateList = list()
        try:
            for attribute in aggCSV.arrayFields:
                if attribute in ['SB', 'AD', 'PL']:
                    continue

                aggAttr = aggCSV.get(attribute)
                newAttr = newCSV.get(attribute)
                if attribute == 'GT':
                    if len(aggAttr) == 2:
                        aggAttr = [-1, -1]
                    else:
                        aggAttr.append(len(aggAttr) + 1)
                else:
                    aggAttr.extend(newAttr)
                updateList.append((attribute, aggAttr))

            for (attr, val) in updateList:
                aggCSV.set(attr, val)
        except Exception, e:
            print attribute, zip(aggCSV.fields, aggCSV.values), zip(newCSV.fields, newCSV.values)
            raise e

    def setupCallSetMapping(self, outFile):
        self.callset_mapping = dict()
        self.output_file = outFile

def poolGenerateCSV((config_file, inputFile, outFile, bGzipped)):
    """
    This function is used by multiprocess.Pool to generate CSV for each input file
    """
    try:
        maf = MAF(config_file)
        maf.setupCallSetMapping(outFile)
        maf.generateCSV(helper.getFilePointer(inputFile, bGzipped, 'r'),
                        helper.getFilePointer(outFile, False, 'w'), bVerbose=False)
        maf.checkCSV(outFile)
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        print "Error processing {0}".format(inputFile)
        print str(e)
        return (-1, inputFile)
    return (0, outFile, maf.callset_mapping)

def parallelGen(config_file, inputFileList, outputDir, combinedOutputFile, bGzipped):
    """
    Function that spawns the Pool of MAF objects to work on each of the input files
    Once the BookKeeping support moves to a real DB, move from threads to multiprocessing.Pool
    """
    config = ConfigReader(config_file)
    dba, vs, rs = helper.registerWithMetadb(config)

    function_args = [None] * len(inputFileList)
    index = 0
    for inFile in inputFileList:
        outFile = outputDir + "/" + helper.getFileName(inFile) + ".csv"
        function_args[index] = (config_file, inFile, outFile, bGzipped)
        index += 1
    combinedOutput = outputDir + "/" + combinedOutputFile
    callset_mapping = dict()
    callset_mapping["unsorted_csv_files"] = list()
    callset_mapping["callsets"] = dict()
    callsets = callset_mapping["callsets"]

    pool = Pool()
    failed = list()
    for returncode in pool.imap_unordered(poolGenerateCSV, function_args):
        if returncode[0] == -1:
            failed.append(returncode[1])
        else:
            print "Completed: {0} with {1} Call Sets".format(returncode[1], len(returncode[2]))
            os.system('cat %s >> %s'%(returncode[1], combinedOutput))
            callset_mapping["unsorted_csv_files"].append(returncode[1])
            callsets.update(returncode[2])

    if len(failed):
        print "\nERROR: Following files failed to process:"
        for f in failed:
            print "\t{0}".format(f)
        raise Exception("Execution failed on {0}".format(failed))

    helper.createMappingFiles(outputDir, callset_mapping, rs.id, config.DB_URI, combinedOutputFile=combinedOutputFile)
