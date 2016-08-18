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

import json


class ConfigReader:
    """
    Specialized config reader for a MAF importing.
    """

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
        self.TileDBSchema['workspace'] = self.TileDBSchema[
            'workspace'].rstrip('/')

        self.HeaderStartsWith = getDictValue(jsonMap, "HeaderStartsWith")

        # Individual defaults to None
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
        self.VariantNameMap = [bDynamic, VariantName,
                               bVariantLookup, VariantConfig, LookupIdx]

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
    if(returnObject is None):
        raise ValueError(inString + " is a required field")
    return returnObject
