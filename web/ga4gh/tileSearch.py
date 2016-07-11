from ctypes import *
from string import join

from flask import json
from flask import jsonify
from sqlalchemy import and_

from gatypes import GACSResponse
from gatypes import GACall
from gatypes import GACallSet
from gatypes import GASVResponse
from gatypes import GASVSetResponse
from gatypes import GAVariant
from gatypes import GAVariantSet
from gatypes import GAVariantSetMetadata
from metadb.api import DBQuery
from metadb.models import VariantSet
from __builtin__ import list


class dbqWrapper():
    dbquery = None


def LoadConfig(config_object):
    dbqWrapper.dbquery = DBQuery(config_object['SQLALCHEMY_DATABASE_URI'])


class GTInt(Structure):
    _fields_ = [("name", c_char_p), ("count", c_ulonglong),
                ("data", (POINTER(c_int)))]


class GTUInt(Structure):
    _fields_ = [("name", c_char_p), ("count", c_ulonglong),
                ("data", (POINTER(c_uint)))]


class GTLong(Structure):
    _fields_ = [("name", c_char_p), ("count", c_ulonglong),
                ("data", (POINTER(c_long)))]


class GTULong(Structure):
    _fields_ = [("name", c_char_p), ("count", c_ulonglong),
                ("data", (POINTER(c_ulong)))]


class GTLongLong(Structure):
    _fields_ = [("name", c_char_p), ("count", c_ulonglong),
                ("data", (POINTER(c_longlong)))]


class GTULongLong(Structure):
    _fields_ = [("name", c_char_p), ("count", c_ulonglong),
                ("data", (POINTER(c_ulonglong)))]


class GTFloat(Structure):
    _fields_ = [("name", c_char_p), ("count", c_ulonglong),
                ("data", (POINTER(c_float)))]


class GTDouble(Structure):
    _fields_ = [("name", c_char_p), ("count", c_ulonglong),
                ("data", (POINTER(c_double)))]


class GTString(Structure):
    _fields_ = [("name", c_char_p), ("count", c_ulonglong),
                ("data", (POINTER(c_char_p)))]


class GTCall (Structure):
    _fields_ = [("id", c_ulonglong), ("int_count", c_ulonglong), ("longlong_count", c_ulonglong),
                ("unsigned_count", c_ulonglong), ("unsigned_longlong_count", c_ulonglong),
                ("float_count", c_ulonglong), ("double_count",
                                               c_ulonglong), ("string_count", c_ulonglong),
                ("int_arr", POINTER(POINTER(GTInt))
                 ), ("longlong_arr", POINTER(POINTER(GTLongLong))),
                ("unsigned", POINTER(POINTER(GTUInt))
                 ), ("unsigned_longlong", POINTER(POINTER(GTULongLong))),
                ("float_arr", POINTER(POINTER(GTFloat))
                 ), ("double_arr", POINTER(POINTER(GTDouble))),
                ("string_arr", POINTER(POINTER(GTString)))]


class GTCallArray (Structure):
    _fields_ = [('callcount', c_ulonglong), ('start', c_ulonglong),
                ('end', c_ulonglong), ('CallArray', POINTER(POINTER(GTCall)))]

    def __init__(self, callcnt):
        elems = (GTCall * callcnt)()
        self.CallArray = cast(elems, POINTER(POINTER(GTCall)))
        self.callcount = callcnt


class GTQuery (Structure):
    _fields_ = [('varcount', c_ulonglong), ('nextPageToken', c_char_p),
                ('VariantArray', POINTER(POINTER(GTCallArray)))]

    def __init__(self, varcnt):
        elems = (GTCallArray * varcnt)()
        self.VariantArray = cast(elems, POINTER(POINTER(GTCol)))
        self.varcount = varcnt


def connectSearchLib(search_so):
    search_lib = cdll.LoadLibrary(search_so)
    search_lib.query_column.restype = POINTER(GTQuery)
    return search_lib


def gtDecode(count, gtarray):
    all_elems = dict()
    for i in range(0, count):
        gthold = gtarray[i].contents
        data_count = gthold.count
        data_name = gthold.name
        elems = list()
        for i in range(0, data_count):
            elems.append(gthold.data[i])

        all_elems[data_name] = elems
    return all_elems

def getRow2CallSet(array_idx, variants, nVariants, metadb):
    """
    Returns a dictionary that maps the row ids to the tuple (call set Id, call
    set GUID, call set name)
    """
    tile_rows = list()
    for i in range(0, nVariants):
        callcount = variants[i].contents.callcount
        CallArray = variants[i].contents.CallArray
        for j in range(0, callcount):
            tile_rows.append(long(CallArray[j].contents.id))
    
    if len(tile_rows) == 0:
      return dict()
    # Fetch info from meta DBQuery
    results = metadb.tileRow2CallSet(array_idx, tile_rows)
    
    resultDict = dict()
    for r in results:
        resultDict[r[0]] = r[1:]
    del tile_rows
    del results
    return resultDict

def searchVariants(
        workspace,
        arrayName,
        referenceName,
        start,
        end,
        searchLib,
        variantSetIds,
        callSetIds = None,
        attrList = [
            'GT',
            'REF',
            'ALT',
            'PL',
            'AF',
            'AN',
            'AC'],
        pageSize = -1,
        pageToken = None):
    gavlist = list()
    attrs = join(attrList, ',')
    if not pageSize:
        pageSize = -1

    getToken = searchLib.getToken
    getToken.restype = c_ulonglong
    token = getToken()

    searchLib.setup_attributes(attrs, token)
    with dbqWrapper.dbquery.getSession() as metadb:

        # set row query restriction
        if ((callSetIds is not None) and callSetIds):
            rowIds = metadb.callSetIds2TileRowId(
                callSetIds, workspace, arrayName)
            rowIds = ",".join(rowIds)
            searchLib.filter_rows(rowIds, token)

        if variantSetIds is not None and len(variantSetIds) > 0:
            variantSetId = variantSetIds[0]
            variantSetIdx, variantSetGuid = metadb.variantSetGUID2Id(
                variantSetId)
        else:
            variantSetIdx, variantSetGuid = metadb.variantSetGUID2Id('empty')

        array_idx = metadb.tileNames2ArrayIdx(workspace, arrayName)
        tileStart, tileEnd = metadb.contig2Tile(
            array_idx, referenceName, [start, end])
        qresp = searchLib.query_column(
            workspace,
            arrayName,
            c_ulonglong(tileStart),
            c_ulonglong(tileEnd),
            c_ulonglong(token),
            c_longlong(pageSize),
            pageToken)
        nextPageToken = qresp.contents.nextPageToken
        varcount = qresp.contents.varcount
        vArray = qresp.contents.VariantArray

        row2callset = getRow2CallSet(array_idx, vArray, varcount, metadb)

        for i in range(0, varcount):
            callcount = vArray[i].contents.callcount
            CallArray = vArray[i].contents.CallArray
            # Once we get the position, translate back to the chromosome
            # positions before returning data
            startp = vArray[i].contents.start
            endp = vArray[i].contents.end
            chromosome, [startp, endp] = metadb.tile2Contig(
                array_idx, [startp, endp])
            # Since the query was to a chromosome, the results will not be outside the
            # chromosome. So just pick chromosome at index 0 for reference name
            referenceName = chromosome[0]
            gaclist = list()

    # if an empty callSetIds list is sent, do not get calls
    # this will need to be fixed for the new library, so ignoring it for now
            for j in range(0, callcount):
                int_count = CallArray[j].contents.int_count
                float_count = CallArray[j].contents.float_count
                double_count = CallArray[j].contents.double_count
                longlong_count = CallArray[j].contents.longlong_count
                unsigned_count = CallArray[j].contents.unsigned_count
                unsigned_longlong_count = CallArray[
                    j].contents.unsigned_longlong_count
                string_count = CallArray[j].contents.string_count
                # tile row assignment right now is assuming that callsetid =
                # tilerowid
                (CallSetIdx, callId, cname) = row2callset[CallArray[j].contents.id] 

                callData = dict()

                if(int_count > 0):
                    int_arr = CallArray[j].contents.int_arr
                    int_elems = gtDecode(int_count, int_arr)
                    callData.update(int_elems)

                if(float_count > 0):
                    float_arr = CallArray[j].contents.float_arr
                    float_elems = gtDecode(float_count, float_arr)
                    callData.update(float_elems)

                if(double_count > 0):
                    double_arr = CallArray[j].contents.double_arr
                    double_elems = gtDecode(double_count, double_arr)
                    callData.update(double_elems)

                if(longlong_count > 0):
                    longlong_arr = CallArray[j].contents.longlong_arr
                    longlong_elems = gtDecode(longlong_count, longlong_arr)
                    callData.update(longlong_elems)

                if(unsigned_count > 0):
                    unsigned_arr = CallArray[j].contents.unsigned_arr
                    unsigned_elems = gtDecode(unsigned_count, unsigned_arr)
                    callData.update(unsigned_elems)

                if(unsigned_longlong_count > 0):
                    unsigned_longlong_arr = CallArray[
                        j].contents.unsigned_longlong_arr
                    unsigned_longlong_elems = gtDecode(
                        unsigned_longlong_count, unsigned_longlong_arr)
                    callData.update(unsigned_longlong_elems)

                if(string_count > 0):
                    string_arr = CallArray[j].contents.string_arr
                    string_elems = gtDecode(string_count, string_arr)
                    callData.update(string_elems)

                plist = callData['PL']
                altlist = callData['ALT']
                reflist = callData['REF'][0]
                gtlist = callData['GT']
                callInfo = {}
                for iname in callData.keys():
                    if iname not in ['REF', 'ALT', 'PL', 'GT']:
                        if(len(callData[iname]) == 0):
                            continue
                        callInfo[iname] = callData[iname]
                        index = 0
                        for value in callInfo[iname]:
                            callInfo[iname][index] = str(value)
                            index += 1
                gac = GACall.GACall(
                    callSetId = callId,
                    callSetName = cname,
                    genotype = gtlist,
                    genotypeLikelihood = plist,
                    info = callInfo)

                callMatch = True

                if(callMatch):
                    gaclist.append(gac.gacall_info)

            # determine if variant should be returned
            if len(gaclist) > 0:
                variantValid = True
            else:
                variantValid = False

            if(not((callSetIds) or (callSetIds is None))):
                gaclist = []

            # if variant is valid and meets the variantSetId filter
            if(variantValid):
                gavlist.append(
                    (GAVariant.GAVariant(
                        id = variantSetIdx,
                        variantSetId = variantSetGuid,
                        referenceName = referenceName,
                        start = startp,
                        end = endp,
                        referenceBases = reflist,
                        alternateBases = altlist,
                        calls = gaclist)).gavariant_info)
        # Cleanup the dictionary since it is no longer needed
        del row2callset
    searchLib.cleanup(token)
    return (GASVResponse.GASVResponse(
        variants = gavlist, nextPageToken = nextPageToken))


def searchCallSets(workspace, arrayName, searchLib, variantSetIds = [
], name = None, pageSize = None, pageToken = None):

    cslist = list()
    callSet = GACallSet.GACallSet().gacallset_info
    nextPageToken = None
    cslist.append(callSet)

    return (GACSResponse.GACSResponse(
        callSets = cslist, nextPageToken = nextPageToken))


def searchVariantSets(datasetId = "", pageSize = None, pageToken = None):

    with dbqWrapper.dbquery.getSession() as metadb:

        nextPageToken = None

        vslist = list()
        for vs in metadb.datasetId2VariantSets(datasetId):

            referenceSetId = metadb.referenceSetIdx2ReferenceSetGUID(
                vs.reference_set_id)

            variantSet = GAVariantSet .GAVariantSet(
                id = vs.guid,
                name = vs.name,
                referenceSetId = referenceSetId,
                datasetId = vs.dataset_id,
                metadata = vs.variant_set_metadata) .gavariantset_info
            vslist.append(variantSet)

    return (GASVSetResponse.GASVSetResponse(
        variantSets = vslist, nextPageToken = nextPageToken))
