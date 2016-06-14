import json

class ConfigReader:
    def __init__(self, config_file):
        with open(config_file, "r") as fp:
            jsonMap = json.load(fp)

        self.DB_URI = getDictValue(jsonMap, "DB_URI")
        self.TileDBAssembly = getDictValue(jsonMap, "TileDBAssembly")
        self.TileDBSchema = getDictValue(jsonMap, "TileDBSchema")
        getDictValue(self.TileDBSchema, "workspace")
        getDictValue(self.TileDBSchema, "array")


        getDictValue(self.TileDBSchema, "fields_list")
        getDictValue(self.TileDBSchema, "ftypes_list")

        # if the name ends with a / then remove it from the name.
        # This is done only for consistency in workspace name
        # since users could have / or not for the workspace.
        self.TileDBSchema['workspace'] = self.TileDBSchema['workspace'].rstrip('/')

        self.HeaderStartsWith = getDictValue(jsonMap, "HeaderStartsWith")

        #Individual defaults to None
        self.IndividualIdMap = jsonMap.get("IndividualId", None)
        self.SourceSampleIdMap = getDictValue(jsonMap, "SourceSampleId")
        self.TargetSampleIdMap = getDictValue(jsonMap, "TargetSampleId")

        # Setup CallSetIdMap
        self.CallSetIdMap = getDictValue(jsonMap, "CallSetId")
        bDynamic = self.CallSetIdMap.get("Dynamic", False)
        CallSetName = getDictValue(self.CallSetIdMap, "CallSetName")
        self.CallSetIdMap = [bDynamic, CallSetName]

        # Setup CallSetIdMap
        self.VariantNameMap = getDictValue(jsonMap, "VariantSetMap")
        bDynamic = self.VariantNameMap.get("Dynamic", False)
        VariantName = getDictValue(self.VariantNameMap, "VariantSet")

        bVariantLookup = self.VariantNameMap.get("VariantLookup", False)
        VariantConfig = self.VariantNameMap.get("VariantConfig", None)
        LookupIdx = self.VariantNameMap.get("LookupIdx", None)
        if bVariantLookup:
            fp = open(VariantConfig, 'r')
            VariantConfig = json.load(fp)
            fp.close()
        self.VariantNameMap = [bDynamic, VariantName, bVariantLookup, VariantConfig, LookupIdx]

        # Setup PositionMap
        self.PositionMap = getDictValue(jsonMap, "Position")
        assembly = getDictValue(self.PositionMap, "assembly")
        bDynamic = assembly.get("Dynamic", False)
        assemblyName = getDictValue(assembly, "assemblyName")
        self.PositionMap["assembly"] = [bDynamic, assemblyName]

        # Verify other required fields in PositionMap are present so that we
        # can avoid checks each time we access these fields
        getDictValue(self.PositionMap, "chromosome")
        getDictValue(self.PositionMap, "Location")
        getDictValue(self.PositionMap, "End")

        self.TileDBMap = getDictValue(jsonMap, "TileDBMapping")
        # Verify other required fields in TileDBMap are present so that we
        # can avoid checks each time we access these fields
        getDictValue(self.TileDBMap, "ALT")

        if 'GT' in self.TileDBMap.keys():
            self.GTMap = getDictValue(jsonMap, 'GTMapping')

        self.SeperatorMap = getDictValue(jsonMap, "Seperators")
        # Verify other required fields in SeperatorMap are present so that we
        # can avoid checks each time we access these fields
        getDictValue(self.SeperatorMap, "line")

        self.Constants = getDictValue(jsonMap, 'Constants')
        getDictValue(self.Constants, 'PLOIDY')

def getDictValue(inDictionary, inString):
    """
    Takes a dictionary object and looks for inString in the dictionary
    If it is not available, an exception is raised.
    Else, the object is returned
    """
    returnObject = inDictionary.get(inString, None)
    if( returnObject == None ):
        raise ValueError(inString + " is a required field")
    return returnObject
