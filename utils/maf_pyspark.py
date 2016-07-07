from pyspark import SparkContext, SparkConf
import uuid
import os
import sys

conf = (SparkConf()
        .set("spark.driver.maxResultSize", "4g")
        .set("spark.python.worker.memory", "2g")
        .set("spark.storage.memoryFraction", "0.1"))

pyFiles = [
    os.path.abspath('csvline.py'),
    os.path.abspath('helper.py'),
    os.path.abspath('file2tile.py')
]

sc = SparkContext(conf=conf, pyFiles=pyFiles)

from utils.csvline import CSVLine
from utils.file2tile import IDX
import utils.helper as helper

# investigate
base = sys.path.append(os.path.abspath('.'))
from metadb.api import DBImport, DBQuery
from metadb.models import CallSetToDBArrayAssociation
from utils.configuration import ConfigReader

indices = None
keysEndPosition = None
keysList = ['SourceSampleName', 'TargetSampleName',
            'CallSetName', 'IndividualName']
level2KeysEndPosition = None
level2KeysList = ['assembly', 'chromosome', 'start', 'end']
otherAttributes = None
rowIdMap = None
GTMap = None


class CONST(IDX):
    MAP = 0
    POSITION = 1
    INDEX = 1
    PLOIDY = 0


class MAF_Spark:
    header = None
    indices = dict()

    def __init__(self, config_file, outFile, logFile):
        self.outFile = outFile
        self.logFile = logFile
        self.config = ConfigReader(config_file)
        global config
        config = self.config
        self.dbimport = DBImport(self.config.DB_URI)
        self.dbquery = DBQuery(self.config.DB_URI)

    def setupCallSetMapping(self, output_file):
        self.callset_mapping = dict()
        self.output_file = output_file

    def genIndices(self):
        position = 0
        self.indices['SourceSampleName'] = [
            self.header.index(self.config.SourceSampleIdMap), position]

        position += 1
        self.indices['TargetSampleName'] = [
            self.header.index(self.config.TargetSampleIdMap), position]

        position += 1
        if self.config.IndividualIdMap is None:
            self.config.IndividualIdMap = self.config.SourceSampleIdMap

        self.indices['IndividualName'] = [
            self.header.index(self.config.IndividualIdMap), position]

        position += 1
        if self.config.CallSetIdMap[IDX.FLAG]:
            CallSetNameIndex = self.header.index(
                self.config.CallSetIdMap[IDX.VALUE])
        else:
            CallSetNameIndex = self.config.CallSetIdMap[IDX.VALUE]
        self.config.CallSetIdMap[IDX.VALUE] = CallSetNameIndex
        self.indices['CallSetName'] = [self.config.CallSetIdMap, position]

        position += 1
        mykeysEndPosition = position

        if self.config.PositionMap['assembly'][IDX.FLAG]:
            AssemblyIndex = self.header.index(
                self.config.PositionMap['assembly'][IDX.VALUE])
        else:
            AssemblyIndex = self.config.PositionMap['assembly'][IDX.VALUE]
        self.config.PositionMap['assembly'][IDX.VALUE] = AssemblyIndex
        self.indices['assembly'] = [
            self.config.PositionMap['assembly'], position]

        position += 1
        self.indices['chromosome'] = [self.header.index(
            self.config.PositionMap['chromosome']), position]
        position += 1
        self.indices['start'] = [self.header.index(
            self.config.PositionMap['Location']), position]
        position += 1
        self.indices['end'] = [self.header.index(
            self.config.PositionMap['End']), position]
        position += 1
        myLevel2KeysEndPosition = position

        otherIndex = 0
        my_otherAttributes = list()
        for k, v in self.config.TileDBMap.items():
            self.indices[k] = [self.header.index(v), position]
            if k not in keysList and k not in level2KeysList:
                my_otherAttributes.append(k)
                otherIndex += 1
            position += 1

        global indices, keysEndPosition, level2KeysEndPosition, otherAttributes, GTMap
        indices = self.indices
        keysEndPosition = mykeysEndPosition
        level2KeysEndPosition = myLevel2KeysEndPosition
        otherAttributes = my_otherAttributes
        GTMap = self.config.GTMap

        CONST.PLOIDY = self.config.Constants['PLOIDY']

    def sparkConvert(self, inFileList):
        HeaderStartsWith = self.config.HeaderStartsWith
        # Convert text files to RDD
        textFiles = sc.textFile(",".join(inFileList))

        # Remove lines that are not header, and comments
        dataLines = textFiles.filter(lambda l: not l.startswith(
            HeaderStartsWith)).filter(lambda l: not l.startswith('#'))
        # Get the header line so that we can map fields
        self.header = textFiles.filter(
            lambda l: l.startswith(HeaderStartsWith)) .take(1)[0].strip().split(
            self.config.SeperatorMap['line'])
        # Generate the indices for attributes where the data will be on the list,
        # so that we can get the attribute value for future processing
        self.genIndices()
        # Split lines into fields
        # self.config.SeperatorMap['line']))
        inputFields = dataLines.map(lambda l: l.split('\t'))

        global indices, dbimport, dbquery
        dbimport = self.dbimport
        dbquery = self.dbquery

        # Get fields of interest and only keep the ones that are distict and
        # drop duplicate lines
        print "Fetching fields; removing duplicates; and doing map-reduce"
        tileFields = inputFields.map(getFields).distinct()
        # Convert tuple into key, value pair, where
        # key = (SampleName, CallSetName, VariantName) and value = (attributes)
        processedFields = tileFields.map(kvPairsBySample)
        # GroupBy samples so that we can generate unique row IDs in Tile DB
        reduxTuple = processedFields.groupByKey()
        # Generate Unique IDs based on the keys
        allKeys = reduxTuple.keys().collect()

        print "Updating Meta DB"
        updateIds(allKeys, self.callset_mapping, self.output_file)

        print "Using Meta DB IDs to combining fields, and generate CSV objects"
        # Since we have the unique Ids, flatMap so that we can parallelize compute further
        # Now make key = (ID, location), and value = (attributes)
        kvValuesByLocation = reduxTuple.flatMapValues(
            lambda x: x).map(kvPairsByLocation)
        # reduce the data by their keys and combine the attributes along the way
        positionalEntries = kvValuesByLocation.reduceByKey(combineData)
        # Now that we have the combined data, check if ALT or REF is a '-' and replace it
        # with correct allele. Also create the CSVLine object.
        # Collect all csv_line objects and we can quickly iterate through this and write into the
        # output file
        csv_objects = positionalEntries.mapPartitions(
            updateRefAltPos).collect()
        print "Writing CSV"

        with open(self.outFile, 'w') as outFP, open(self.logFile, "w") as outLog:
            outLog.write(
                "INFO: Total Tile DB Rows : {0} \n".format(len(rowIdMap)))
            count = 0
            size = len(csv_objects)
            outLog.write("INFO: Total Lines : {0} \n".format(size))
            for m_csv_line in csv_objects:
                # If an exception was thrown during the creating on csv line,
                # then the isValid will be false
                if m_csv_line.isValid:
                    outFP.write(m_csv_line.getCSVLine())
                    outFP.write("\n")
                else:
                    outLog.write(m_csv_line.error)
                    outLog.write("\n")
                count += 1
                helper.progressPrint("%d of %d Completed" % (count, size))
        print


def getFields(fields):
    global indices

    outFields = ['*'] * len(indices)
    for key, index in indices.items():
        if key in ['CallSetName', 'assembly']:
            if not index[CONST.MAP][CONST.FLAG]:
                # Dynamic naming is off so just pick the name that was provided
                outFields[index[CONST.POSITION]] = index[
                    CONST.MAP][CONST.INDEX]
            else:
                # Dynamic naming is on, so pick the name from the file
                outFields[index[CONST.POSITION]] = fields[
                    index[CONST.MAP][CONST.INDEX]]
            continue
        outFields[index[CONST.POSITION]] = fields[index[CONST.MAP]]

    return tuple(outFields)


def kvPairsBySample(inTuple):

    global indices, keysEndPosition, keysList
    keys = [None] * keysEndPosition
    values = [None] * (len(indices) - keysEndPosition)

    i = 0
    for key in keysList:
        keys[i] = inTuple[indices[key][CONST.POSITION]]
        i += 1

    for key, index in indices.items():
        if key in keysList:
            continue
        values[keysEndPosition - index[CONST.POSITION]
               ] = inTuple[indices[key][CONST.POSITION]]

    return (tuple(keys), tuple(values))


def updateIds(keys, callset_mapping, output_file):
    global rowIdMap, indices, dbimport, dbquery, variantSetId

    rowIdMap = dict()
    with dbimport.getSession() as metadb:
        for k in keys:

            individual_name = k[keysList.index('IndividualName')]
            if k[keysList.index('IndividualName')] == k[
                    keysList.index('SourceSampleName')]:
                individual_name = 'Individual_' + \
                    k[keysList.index('SourceSampleName')]

            Individual = metadb.registerIndividual(
                guid=str(uuid.uuid4()),
                name=individual_name
            )

            SourceSample = metadb.registerSample(
                guid=str(uuid.uuid4()),
                name=k[keysList.index('SourceSampleName')],
                individual_guid=Individual.guid,
                info={'type': 'source'}
            )

            TargetSample = metadb.registerSample(
                guid=str(uuid.uuid4()),
                name=k[keysList.index('TargetSampleName')],
                individual_guid=Individual.guid,
                info={'type': 'target'}
            )

            CallSet = metadb.registerCallSet(
                guid=str(uuid.uuid4()),
                individual_guid=Individual.guid,
                source_sample_guid=SourceSample.guid,
                target_sample_guid=TargetSample.guid,
                workspace=config.TileDBSchema['workspace'],
                array_name=config.TileDBSchema['array'],
                name=k[keysList.index('CallSetName')],
                variant_set_ids=[variantSetId]
            )

            with dbquery.getSession() as query:
                row_id = query.callSetIds2TileRowId([CallSet.id],
                    config.TileDBSchema['workspace'],
                    config.TileDBSchema['array'],
                    isGUID=False)[0]

                my_sample_name = "{0}-{1}-{2}-{3}".format(
                    Individual.name,
                    SourceSample.name,
                    TargetSample.name,
                    CallSet.id)

                callset_mapping[my_sample_name] = {
                    "row_idx": long(row_id),
                    "idx_in_file": long(row_id),
                    "filename": output_file
                }

            rowIdMap["{0}:{1}:{2}" .format(SourceSample.name, 
                    k[keysList.index('CallSetName')], 'VariantName')] = row_id


def kvPairsByLocation(keys_tuple):

    (k, inTuple) = keys_tuple
    global indices, keysList, keysEndPosition
    global level2KeysList, level2KeysEndPosition, otherAttributes, rowIdMap

    SourceSampleName = k[keysList.index('SourceSampleName')]
    CallSetName = k[keysList.index('CallSetName')]

    RowID = rowIdMap["{0}:{1}:{2}".format(
        SourceSampleName, CallSetName, 'VariantName')]

    assembly = inTuple[keysEndPosition - indices['assembly'][CONST.POSITION]]
    chromosome = inTuple[keysEndPosition -
                         indices['chromosome'][CONST.POSITION]]
    start = long(inTuple[keysEndPosition - indices['start'][CONST.POSITION]])
    end = long(inTuple[keysEndPosition - indices['end'][CONST.POSITION]])

    values = [None] * (len(indices) - level2KeysEndPosition)

    for key, index in indices.items():
        if key in keysList or key in level2KeysList:
            continue
        # Store the value in the level 2 offset by getting it from the level 1
        # (keysEndPosition) offset
        values[otherAttributes.index(key)] = inTuple[
            keysEndPosition - indices[key][CONST.POSITION]]

    formattedValues = getSnapshot(values)
    return ((RowID, assembly, chromosome, start, end), tuple(formattedValues))


def getSnapshot(attributeList):
    global otherAttributes, GTMap
    snapshot = [None] * len(otherAttributes)
    for i in xrange(0, len(otherAttributes)):
        if otherAttributes[i] in CSVLine.arrayFields:
            # TODO Assume that there is not more than 1 value in the array
            # fields in MAF
            snapshot[i] = attributeList[i].split(None)
            if len(snapshot[i]) == 0:
                snapshot[i] = ['*']
            if otherAttributes[i] == 'GT':
                for j in xrange(0, len(snapshot[i])):
                    if snapshot[i][j] in GTMap.keys():
                        snapshot[i][j] = GTMap[snapshot[i][j]]

        else:
            if attributeList[i] == '':
                snapshot[i] = '*'
            else:
                snapshot[i] = attributeList[i]
    return snapshot


def combineData(combinedSnapshot, newSnapshot):
    global otherAttributes
    if 'ALT' in otherAttributes:
        indexOfALT = otherAttributes.index('ALT')
        newAllele = False
        for allele in newSnapshot[indexOfALT]:
            if allele not in combinedSnapshot[indexOfALT]:
                newAllele = True
                break
        if newAllele:
            for i in xrange(0, len(otherAttributes)):
                if otherAttributes[i] in CSVLine.arrayFields:
                    if 'GT' == otherAttributes[i]:
                        combinedSnapshot[i].append(
                            str(len(combinedSnapshot[i]) + 1))
                    else:
                        combinedSnapshot[i].extend(newSnapshot[i])
    return tuple(combinedSnapshot)


def updateRefAltPos(iter):
    """
    Since MAF represents insertions and deletions with a '-' it needs to
    be processed before adding to the CSV Line
    1. Insertions
      Ref = get_ref_from_ensembl(chr, start-1, start - 1)
      Alt = Ref + Alt # Concatenate Ref and Alt
      Chr = Chr
      Start = Start - 1
      End = Start
    2. Deletions
      NewRef = get_ref_from_ensembl(chr, start-1, start-1)
      Ref = NewRef + Ref
      Alt = NewRef
      Chr = Chr
      Start = Start - 1
      End = End
    """
    global level2KeysList, otherAttributes, DB_URI, array_id
    dbquery = DBQuery(DB_URI)
    m_csv_line_list = list()
    with dbquery.getSession() as query:
        for (location, combinedSnapshot) in iter:
            # rowid is actually the callset id, pass this information
            RowID = location[0]
            location = location[1:]
            assembly = location[level2KeysList.index('assembly')]
            chromosome = location[level2KeysList.index('chromosome')]
            start = long(location[level2KeysList.index('start')])
            end = long(location[level2KeysList.index('end')])

            alt = combinedSnapshot[otherAttributes.index('ALT')]
            ref = combinedSnapshot[otherAttributes.index('REF')]

            # Insertion
            if(ref == '-'):
                start = start - 1
                end = start

                newRef = helper.getReference(
                    assembly, chromosome, start, start)
                ref = newRef

                index = 0
                for value in alt:
                    alt[index] = ref + value
                    index += 1

            else:
                bFlag = False
                for v in alt:
                    if(v == '-'):
                        bFlag = True

                if(bFlag):
                    start = start - 1
                    newRef = helper.getReference(
                        assembly, chromosome, start, start)
                    ref = newRef + ref
                    index = 0
                    for value in alt:
                        if(value == '-'):
                            alt[index] = newRef
                        else:
                            alt[index] = newRef + value
                        index += 1

            try:
                [tileStart, tileEnd] = query.contig2Tile(
                    array_id, chromosome, [long(start), long(end)])
            except Exception as e:
                print '\n' * 2
                print e
                print '\n'

            m_csv_line = CSVLine()
            exceptionList = ['ALT', 'REF', 'PLOIDY']
            m_csv_line.set("SampleId", RowID)
            m_csv_line.set("Location", tileStart)
            m_csv_line.set("End", tileEnd)
            m_csv_line.set("REF", ref)
            m_csv_line.set("ALT", alt)
            m_csv_line.set("PLOIDY", CONST.PLOIDY)

            try:
                for i in xrange(0, len(otherAttributes)):
                    attribute = otherAttributes[i]
                    if(attribute in exceptionList):
                        continue
                    if(attribute == "GT"):
                        GTLength = len(combinedSnapshot[i])
                        if GTLength == 1:
                            m_csv_line.set(
                                attribute, [combinedSnapshot[i][0], 0])
                            continue
                        elif GTLength > CONST.PLOIDY:
                            m_csv_line.set(attribute, [-1] * CONST.PLOIDY)
                            continue
                    value = combinedSnapshot[i]
                    m_csv_line.set(attribute, value)
            except Exception as e:
                global rowIdMap
                SampleInfo = None
                for k, v in rowIdMap.items():
                    if v == RowID:
                        SampleInfo = k
                        break
                m_csv_line.invalidate("ERROR: {0}:{1}:{2}".format(
                    SampleInfo, location, combinedSnapshot))
            m_csv_line_list.append(m_csv_line)

    return m_csv_line_list


def parallelGen(config_file, inputFileList, outputDir, combinedOutputFile):
    """
    Function that spawns  Spark RDD objects to work on each of the input files
    """
    config = ConfigReader(config_file)

    global DB_URI, variantSetId, array_id
    DB_URI = config.DB_URI
    dba, vs, rs = helper.registerWithMetadb(config)
    array_id = dba.id
    variantSetId = vs.id

    baseFileName = helper.getFileName(combinedOutputFile)
    logFile = baseFileName + ".log"
    combinedOutput = outputDir + "/" + combinedOutputFile
    maf = MAF_Spark(config_file, combinedOutput, outputDir + '/' + logFile)
    maf.setupCallSetMapping(combinedOutput)
    maf.sparkConvert(inputFileList)
    print "Completed: {0} with {1} Call Sets".format(combinedOutput, len(maf.callset_mapping))

    callset_mapping = dict()
    callset_mapping["unsorted_csv_files"] = [combinedOutput]
    callset_mapping["callsets"] = dict()
    callset_mapping["callsets"].update(maf.callset_mapping)

    helper.createMappingFiles(
        outputDir, combinedOutputFile, callset_mapping, rs.id, config.DB_URI)

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Convert MAF format to Tile DB CSV")

    parser.add_argument(
        "-c", 
        "--config", 
        required=True, 
        type=str,
        help="input configuration file for MAF conversion")

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=str,
        help="Tile DB CSV output file basename to be stored in the output directory")

    parser.add_argument(
        "-d",
        "--outputdir",
        required=True,
        type=str,
        help="Output directory where the outputs need to be stored")

    parser.add_argument(
        "-i", 
        "--inputs", 
        nargs='+', 
        type=str, 
        required=True,
        help="List of input MAF files to convert")

    args = parser.parse_args()

    parallelGen(args.config, args.inputs, args.outputdir, args.output)
