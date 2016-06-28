"""
Contains the key methods and type checks required 
to generate a csv file that tiledb can load.
"""
from ast import literal_eval

EMPTYCHAR = '*'
NUM_SB = 4


class CSVLine:
    """
    Holds data required to build a CSV Line.
    Tests the length and types required by tile db csv.
    """
    # Number of versions
    num_versions = 1

    # Fields in Tile DB CSV
    # It is a 2D array, and each element is an array represents the fields of
    # a version
    fieldNames = [["SampleId", "Location", "End", "REF", "ALT",
                   "QUAL", "numFilter", "FilterId", "BaseQRankSum",
                   "ClippingRankSum", "MQRankSum", "ReadPosRankSum",
                   "MQ", "MQ0", "AF", "AN", "AC", "DP", "DP_FMT", "MIN_DP",
                   "GQ", "SB", "AD", "PL", "PLOIDY", "GT", "PS"]]

    arrayFields = ["ALT", "FilterId", "SB", "AD", "PL", "GT", "AF", "AC"]

    def __init__(self, version=1):
        if version > self.num_versions:
            self.version = self.num_versions
        else:
            self.version = version
        self.reinit()

    def reinit(self):
        """
        Called to clear the data structure in preparation for next line
        Will be called by getCSVLine after creating the csv line unless specified
        """
        self.fields = list()
        self.numALT = self.numAD = self.numPL = 0
        self.ploidy = 0
        self.isValid = True
        self.error = None

        # Init fields based on the version
        for i in range(0, self.version):
            self.fields.extend(self.fieldNames[i])

        # Init the values array based on the len of fields
        self.values = [EMPTYCHAR] * len(self.fields)

        # Special Handling for SB value since it always is an array of 4
        self.set("SB", [EMPTYCHAR] * NUM_SB)

        # Set numFilter to 0 to begin with
        self.set("FilterId", [])

    def set(self, attr, value):
        """
        set is used to populate the CSV Line.
        It performs basic checks before adding the data into the CSV Line.
        """
        if(attr in self.fields):
            index = self.fields.index(attr)
            if(attr == "PLOIDY"):
                self.ploidy = value
                self.values[self.fields.index("GT")] = [EMPTYCHAR] * value
            elif(attr in self.arrayFields):
                if(isinstance(value, list)):
                    if(attr == "SB"):
                        if(len(value) != NUM_SB):
                            raise ValueError(
                                "SB must have {0} entries".format(NUM_SB))
                    elif(attr == "FilterId"):
                        self.values[self.fields.index(
                            "numFilter")] = len(value)
                    elif(attr == "ALT"):
                        self.numALT = len(value)
                        self.numAD = self.numALT + 1
                        self.numPL = ((self.numALT + 1) *
                                      (self.numALT + 2)) / 2

                        # Init PL values to nulls
                        self.values[self.fields.index("PL")] = [
                            EMPTYCHAR] * self.numPL
                        # Init AD values to nulls EMPTYCHAR
                        self.values[self.fields.index("AD")] = [
                            EMPTYCHAR] * self.numAD
                        self.values[self.fields.index("AF")] = [
                            EMPTYCHAR] * self.numALT
                        self.values[self.fields.index("AC")] = [
                            EMPTYCHAR] * self.numALT
                    elif(attr == "AD"):
                        if(self.numALT == 0):
                            raise SyntaxError(
                                "ALT must be set before calling set AD")
                        elif(len(value) != self.numAD):
                            raise ValueError(
                                "AD[] must be of length {0} but given {1}".format(
                                    (str)(
                                        self.numAD), value))
                    elif(attr == "AF"):
                        if(self.numALT == 0):
                            raise SyntaxError(
                                "ALT must be set before calling set AF")
                        elif(len(value) != self.numALT):
                            raise ValueError(
                                "AF[] must be of length {0} but given {1} ".format(
                                    (str)(
                                        self.numALT), value))
                    elif(attr == "AC"):
                        if(self.numALT == 0):
                            raise SyntaxError(
                                "ALT must be set before calling set AC")
                        elif(len(value) != self.numALT):
                            raise ValueError(
                                "AC[] must be of length {0} but given {1}".format(
                                    (str)(
                                        self.numALT), value))
                    elif(attr == "PL"):
                        if(self.numALT == 0):
                            raise SyntaxError(
                                "ALT must be set before calling set PL")
                        elif(len(value) != self.numPL):
                            raise ValueError(
                                "PL[] must be of length {0} but given {1}".format(
                                    (str)(
                                        self.numPL), value))
                    elif(attr == "GT"):
                        if(self.ploidy == 0):
                            raise SyntaxError(
                                "PLOIDY must be set before calling set GT")
                        elif(len(value) != self.ploidy):
                            raise ValueError(
                                "GT[] must be of length {0} but given {1}".format(
                                    (str)(
                                        self.ploidy), value))
                    else:
                        # Will never reach here
                        raise ValueError("Logic Error in name matching")
                else:
                    raise TypeError(attr + " takes a list as input")
            self.values[index] = value
        else:
            raise ValueError(attr + " is not a valid attribute")

    def get(self, attr):
        """
        Gets the value that is currently stored
        """
        if(attr in self.fields):
            index = self.fields.index(attr)
            return self.values[index]
        return None

    def checkValidLong(self, attr):
        """
        Helper function for runChecks that fails on < 0
        Also returns the value that was fetched
        """
        bReturn = True
        value = self.get(attr)
        if(value == EMPTYCHAR or long(value) < 0):
            bReturn = False

        return (bReturn, value)

    def runChecks(self):
        """
        Performs the checks that need to be satisfied before the CSV Line is created.
        """
        bPass = True
        returnString = ""
        # Sample Id should be valid
        (bIsValid, SampleId) = self.checkValidLong("SampleId")
        if(not bIsValid):
            returnString += "SampleId :" + str(SampleId) + " is invalid\n"
            bPass = False

        # Start Location should be valid
        (bIsValid, Location) = self.checkValidLong("Location")
        if(not bIsValid):
            returnString += "Location :" + str(Location) + " is invalid\n"
            bPass = False

        # End should be valid and = start
        (bIsValid, End) = self.checkValidLong("End")
        if(not bIsValid):
            returnString += "End :" + str(End) + " is invalid\n"
            bPass = False
        elif(long(End) < long(Location)):
            returnString += "End :" + \
                str(End) + " < Start :" + str(Location) + "\n"
            bPass = False

        # numALT cannot be 0
        if(self.numALT == 0):
            returnString += "ALT must be set\n"
            bPass = False

        if(not bPass):
            returnString = "Following checks failed: \n" + returnString

        return (bPass, returnString)

    def getCSVLine(self, clear=True):
        """
        Runs checks and combines all the data into a CSV that can be used by the
        loader in TileDB to create the DB
        """
        # Run the checker to make sure the minimal conditions are met
        (bPass, errorString) = self.runChecks()
        if(not bPass):
            return errorString

        # FilterId field needs to be skipped if it is an empty field
        numFilter = self.get("numFilter")
        bSkipFilterId = (numFilter == EMPTYCHAR or int(numFilter) == 0)
        FilterIdIndex = self.fields.index("FilterId")

        self.fields.index('GT')

        outCSVLine = ""
        for index in range(0, len(self.fields)):
            # Special handling for FilterId
            if(FilterIdIndex == index and bSkipFilterId):
                continue
            # Handling for GT field
            if self.fields[index] == 'GT' and self.ploidy == 0:
                continue

            value = self.values[index]
            if self.fields[index] == 'PLOIDY' and self.ploidy == 0:
                value = EMPTYCHAR
            if(self.fields[index] in self.arrayFields and isinstance(value, list)):
                # ALT is read as 1 string that is separated by |
                if self.fields[index] == 'ALT':
                    outCSVLine += '|'.join(value)
                    outCSVLine += ','
                    continue
                # Variable length fields need to have the # elements prefixed
                elif self.fields[index] == 'AD':
                    if self.numAD > 0:
                        countEmpty = 0
                        for c in value:
                            if c == EMPTYCHAR:
                                countEmpty += 1
                        if countEmpty == self.numAD:
                            outCSVLine += '0,'
                            continue
                    outCSVLine += str(self.numAD) + ','
                elif self.fields[index] == 'AF':
                    if self.numALT > 0:
                        countEmpty = 0
                        for c in value:
                            if c == EMPTYCHAR:
                                countEmpty += 1
                        if countEmpty == self.numALT:
                            outCSVLine += '0,'
                            continue
                    outCSVLine += str(self.numALT) + ','
                elif self.fields[index] == 'AC':
                    if self.numALT > 0:
                        countEmpty = 0
                        for c in value:
                            if c == EMPTYCHAR:
                                countEmpty += 1
                        if countEmpty == self.numALT:
                            outCSVLine += '0,'
                            continue
                    outCSVLine += str(self.numALT) + ','
                elif self.fields[index] == 'PL':
                    if self.numPL > 0:
                        countEmpty = 0
                        for c in value:
                            if c == EMPTYCHAR:
                                countEmpty += 1
                        if countEmpty == self.numPL:
                            outCSVLine += '0,'
                            continue
                    outCSVLine += str(self.numPL) + ','

                for v in value:
                    outCSVLine += str(v) + ","
            else:
                outCSVLine += str(value) + ","

        if(clear):
            self.reinit()

        # remove the last , and return
        return outCSVLine.rstrip(",")

    def invalidate(self, errorString):
        self.isValid = False
        self.error = errorString

    # def loadCSV(self, inString):
    def loadCSV(self, values):
        index = 0
        numFilter = 0
        index_history = list()
        for attribute in self.fields:
            index_history.append(index)
            if attribute == 'ALT':
                values[index] = values[index].split('|')
            elif attribute == 'numFilter':
                numFilter = int(values[index])
            elif attribute == 'PLOIDY':
                if values[index] == EMPTYCHAR:
                    self.set(attribute, 0)
                else:
                    self.set(attribute, int(values[index]))
                index += 1
                # Continue so that GT is handled automatically
                continue
            elif attribute in self.arrayFields:
                if attribute == 'SB':
                    num_values = NUM_SB
                    index -= 1
                elif attribute == 'FilterId':
                    num_values = numFilter
                    index -= 1
                elif attribute in ['AD', 'PL', 'AF', 'AC']:
                    num_values = int(values[index])
                elif attribute == 'GT':
                    num_values = self.ploidy
                    index -= 1
                else:
                    num_values = int(values[index])
                if num_values > 0:
                    retValues = self.getRange(values, index + 1, num_values)
                    self.set(attribute, retValues)
                    index += (num_values + 1)
                    continue
                else:
                    index += 1
                    continue
            self.set(attribute, values[index])
            index += 1

    def getRange(self, values, start, size):
        output = [None] * size
        for i in xrange(0, size):
            output[i] = values[start + i]
        return output
