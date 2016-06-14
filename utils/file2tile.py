import csvline
from utils.configuration import ConfigReader
from metadb.api.query import DBQuery

class IDX:
    """
    Class that defines the constants
    """
    # Test and use type tuples
    FLAG          = 0
    VALUE         = 1
    VARIANTLOOKUP = 2
    VARIANTCONFIG = 3
    LOOKUPIDX     = 4

    # Position Indices
    START = 0
    END = 1

    # ChromosomePosition Indices
    CHR_ASSEMBLY = 0
    CHR_CHR = 1
    CHR_START = 2
    CHR_END = 3

class File2Tile(object):

    def __init__(self, config_file):
        self.config = ConfigReader(config_file)
        # Sample ID header name in the input
        self.IndividualId = None
        self.SourceSampleId = None
        self.TargetSampleId = None

        # CallSetId is a list of length 2 where the first element says whether the
        # CallSetId is a constant for the input file or based on a field in the input
        self.CallSetIdMap = None

        self.VariantSetName = None

        # CallSetName for current sample
        self.CallSetName = None

        # Defines which fields define the position
        self.PositionMap = None

        # ChromosomePosition is a list [assemblyName, chromosome, start, end]
        self.ChromosomePosition = None

        # TileDBPosition is a list of len 2 that stores the start and end position
        # values in tile db position format
        self.TileDBPosition = None

        # Mapping from Input data set to TileDB fields
        self.TileDBMap = None

        # TileDBValues is a dictionary of TileDB values derived from the input line
        # based on TileDBMap
        self.TileDBValues = None

        # Seperators in the input file
        # Required to have "line" as one of the entires in the map
        # List fields can have their own seperators and they are defined in this map
        self.SeperatorMap = None

        # File Name without the extension
        self.FileName = None

        # File Pointer to the input file
        self.inFile = None

        # File Pointer to the output CSV
        self.outFile = None

        # Header is the list that maps a name to the value coming from the line
        self.header = None

        # Values is the list of values from the input file
        self.values = None

        self.IndividualIdMap   = self.config.IndividualIdMap
        self.SourceSampleIdMap = self.config.SourceSampleIdMap
        self.TargetSampleIdMap = self.config.TargetSampleIdMap
        self.CallSetIdMap      = self.config.CallSetIdMap
        self.PositionMap       = self.config.PositionMap
        self.TileDBMap         = self.config.TileDBMap
        self.SeperatorMap      = self.config.SeperatorMap
        self.VariantNameMap    = self.config.VariantNameMap

        self.dbquery = DBQuery(self.config.DB_URI)
        # Save array_idx since it is used multiple times
        with self.dbquery.getSession() as query:
            self.array_idx = query.tileNames2ArrayIdx(self.config.TileDBSchema['workspace'],
                                                      self.config.TileDBSchema['array'])

    def generateCSV(self, inputFile, outFile):
        """
        Takes the input data and generates a CSV File
        Should be implemented by the SubClass
        """
        pass

    def initFilePointers(self, inputFile, outFile):
        """
        This is the first function that should be called by generateCSV to populate
        the inFile and outFile pointers.
        """
        self.inFile = inputFile
        self.outFile = outFile

    def closeFilePointers(self):
        self.inFile.close()
        self.outFile.close()

    def getHeader(self):
        """
        Populates the header object
        This function also checks if the fields maps to the header from input
        """
        # self.header = self.inFile.readline().strip().split(self.SeperatorMap["line"])
        line = '#'
        while line.startswith('#'):
            line = self.inFile.readline().strip()
        self.header = line.split(self.SeperatorMap["line"])

        if( self.SourceSampleIdMap not in self.header ):
            raise ValueError(self.SourceSampleIdMap + " is not a valid field in input file's header")
        if( self.TargetSampleIdMap not in self.header ):
            raise ValueError(self.TargetSampleIdMap + " is not a valid field in input file's header")

        if( self.CallSetIdMap[IDX.FLAG] and self.CallSetIdMap[IDX.VALUE] not in self.header ):
            raise ValueError(self.CallSetIdMap[IDX.VALUE] + " is not a valid field in input file's header")

        for key in self.PositionMap.keys() :
            if( key == "assembly" and self.PositionMap[key][IDX.FLAG] and
                self.PositionMap[key][IDX.VALUE] not in self.header):
                raise ValueError(self.PositionMap[key][IDX.VALUE] + " is not a valid field in input file's header")

            if( key != "assembly" and self.PositionMap[key] not in self.header ):
                raise ValueError(self.PositionMap[key] + " is not a valid field in input file's header")

        for value in self.TileDBMap.values() :
            if( value not in self.header ):
                raise ValueError(value + " is not a valid field in input file's header")

    def parseNextLine(self):
        """
        reads next line from the file and populates the values, and other fields
        """
        if( self.header == None ):
            self.getHeader()

        self.values = self.inFile.readline().strip().split(self.SeperatorMap["line"])
        # If we reach the end of file then return False
        if( len(self.values) == 1 ):
            return False

        self.SourceSampleId = self.getValue(self.SourceSampleIdMap)
        self.TargetSampleId = self.getValue(self.TargetSampleIdMap)
        if self.IndividualIdMap == None:
            # work around incase indiviudal is not defined
            # assumes one normal sample per individual
            self.IndividualId = 'Individual_'+self.SourceSampleId
        else:
            self.IndividualId = self.getValue(self.IndividualIdMap)
        self.updatePosition()
        self.updateCallSet()
        self.updateVariantName()
        self.updateTileDBValues()

        return True

    def getValue(self, name):
        """
        getValue gets the value given a name of the column (stored in header)
        """
        index = self.header.index(name)
        if( index < len(self.values) ):
            return self.values[index]
        else:
            return ""

    def updatePosition(self):
        """
        updatePosition is called after the input line is read into the values object
        This function populates the TileDBPosition object based on the input data
        """
        assembly = self.PositionMap["assembly"]
        assemblyName = None
        if( assembly[IDX.FLAG] ):
            assemblyName = self.getValue(assembly[IDX.VALUE])
        else:
            assemblyName = assembly[IDX.VALUE]

        chromosome = self.getValue(self.PositionMap["chromosome"])
        Location = long(self.getValue(self.PositionMap["Location"]))
        End = long(self.getValue(self.PositionMap["End"]))

        self.ChromosomePosition = [assemblyName, chromosome, Location, End]
        with self.dbquery.getSession() as query:
            self.TileDBPosition = query.contig2Tile(self.array_idx, chromosome, [Location, End])

    def updateCallSet(self):
        """
        updateCallSet is called after the input line is read into the values object
        updates the CallSetName object
        """
        # If call set is static for the file then populate the CallSetName field and return
        # Else, pull from the values object
        if( self.CallSetIdMap[IDX.FLAG] ):
            self.CallSetName = self.getValue(self.CallSetIdMap[IDX.VALUE])
        else:
            if( self.CallSetName != None ):
                return
            else:
                self.CallSetName = self.CallSetIdMap[IDX.VALUE]

    def updateVariantName(self):
        """
        updateVariant is called after the input line is read into the values object
        updates the VariantName object
        """
        # If call set is static for the file then populate the VariantName field and return
        # Else, pull from the values object
        if( self.VariantNameMap[IDX.FLAG] ):
            if self.VariantNameMap[IDX.VARIANTLOOKUP]:
                VariantConfig = self.VariantNameMap[IDX.VARIANTCONFIG]
                valueFromFile = self.getValue(self.VariantNameMap[IDX.VALUE])
                self.VariantSetName = VariantConfig[valueFromFile][self.VariantNameMap[IDX.LOOKUPIDX]]
            else:
                self.VariantSetName = self.getValue(self.VariantNameMap[IDX.VALUE])
        else:
            if( self.VariantSetName != None ):
                return
            else:
                self.VariantSetName = self.VariantNameMap[IDX.VALUE]

    def updateTileDBValues(self):
        """
        updateTileDBValues is called after the input line is read into the values object
        updates the TileDBValues array
        """
        self.TileDBValues = dict()
        for key, token in self.TileDBMap.items():
            value = self.getValue(token)
            if( key in csvline.CSVLine.arrayFields ):
                value = value.split(self.SeperatorMap.get(key, None))
                if len(value) == 0:
                    value = [csvline.EMPTYCHAR]
                if key == 'GT' :
                    for j in xrange(0, len(value)):
                        if value[j] in self.config.GTMap.keys():
                            value[j] = self.config.GTMap[value[j]]
            self.TileDBValues[key] = value
