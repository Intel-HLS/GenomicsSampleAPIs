from web.gatypes import GACall, GACallSet, GAVariant, GAVariantSet, GASVResponse, GACSResponse, GASVSetResponse, GAVariantSetMetadata
from json import loads

class TestGAtypes:

    def test_GACall(self):
        gac = GACall.GACall(callSetId = "callId", callSetName = "cname", genotype = [0,1,2], phaseset = "phase", genotypeLikelihood = [1,2,3], info = {'Test': 'True', 'Number': 5})
        res = gac.gacall_info
        tmp = loads(gac.getJSON())

        assert res['callSetId'] == "callId"
        assert res['callSetName'] == "cname"
        assert res['genotype'] == [0,1,2]
        assert res['phaseset'] == "phase"
        assert res['genotypeLikelihood'] == [1,2,3]
        assert res['info'] == {'Test': 'True', 'Number': 5}

        min_gac = GACall.GACall(callSetId = "justcallId")
        res = min_gac.gacall_info
        tmp = loads(min_gac.getJSON())

        assert res['callSetId'] == "justcallId"
        assert res['callSetName'] == None
        assert res['genotype'] == []
        assert res['phaseset'] == None
        assert res['genotypeLikelihood'] == []
        assert res['info'] == {}

    def test_GACallSet(self):
        min_gacs = GACallSet.GACallSet()
        res = min_gacs.gacallset_info
        tmp = loads(min_gacs.getJSON())

        assert res['id'] == ""
        assert res['name'] == None
        assert res['sampleId'] == ""
        assert res['variantSetIds'] == []
        assert res['created'] == None
        assert res['updated'] == None
        assert res['info'] == {}

        gacs = GACallSet.GACallSet(id = 'csid', name = 'myName', sampleId = '12', variantSetIds = [0,1,2], created = 1234, updated = 2345, info = {'Test': 'True', 'Number': 5})
        res = gacs.gacallset_info
        tmp = loads(gacs.getJSON())

        assert res['id'] == 'csid'
        assert res['name'] == 'myName'
        assert res['sampleId'] == '12'
        assert res['variantSetIds'] == [0, 1, 2]
        assert res['created'] == 1234
        assert res['updated'] == 2345
        assert res['info'] == {'Test': 'True', 'Number': 5}

    def test_GAVariant(self):
        min_gav = GAVariant.GAVariant(id='myid', variantSetId = 'myvsid', start = 1, end = 4, referenceBases = 'myref')
        res = min_gav.gavariant_info
        tmp = loads(min_gav.getJSON())

        assert res['id'] == 'myid'
        assert res['variantSetId'] == 'myvsid'
        assert res['start'] == 1
        assert res['end'] == 4
        assert res['referenceBases'] == 'myref'
        assert res['names'] == []
        assert res['created'] == None
        assert res['updated'] == None
        assert res['referenceName'] == ''
        assert res['alternateBases'] == []
        assert res['info'] == {}

        gav = GAVariant.GAVariant(id='myid', variantSetId = 'myvsid', start = 1, end = 4, referenceBases = 'myref', names = ['a', 'b'], created = 12, updated = 16, referenceName= 'myrefname', alternateBases = ['G', 'T'], info = {'Test': 'True', 'Number': 5})
        res = gav.gavariant_info
        tmp = loads(gav.getJSON())

        assert res['id'] == 'myid'
        assert res['variantSetId'] == 'myvsid'
        assert res['start'] == 1
        assert res['end'] == 4
        assert res['referenceBases'] == 'myref'
        assert res['names'] == ['a', 'b']
        assert res['created'] == 12
        assert res['updated'] == 16
        assert res['referenceName'] == 'myrefname'
        assert res['alternateBases'] == ['G', 'T']
        assert res['info'] == {'Test': 'True', 'Number': 5}

    def test_GAVariantSet(self):
        min_gavs = GAVariantSet.GAVariantSet()
        res = min_gavs.gavariantset_info
        tmp = loads(min_gavs.getJSON())

        assert res['id'] == ''
        assert res['name'] == ''
        assert res['referenceSetId'] == ''
        assert res['datasetId'] == ''
        assert res['metadata'] == []

        gavs = GAVariantSet.GAVariantSet(id = 'myid', name = 'myname', referenceSetId = 'myrefsetid', datasetId = 'mydsit', metadata = [1, 2, 3, 4])
        res = gavs.gavariantset_info
        tmp = loads(gavs.getJSON())
        assert res['id'] == 'myid'
        assert res['name'] == 'myname'
        assert res['referenceSetId'] == 'myrefsetid'
        assert res['datasetId'] == 'mydsit'
        assert res['metadata'] == [1,2,3,4]

    def test_GASVResponse(self):
        min_gav = GAVariant.GAVariant(id='myid', variantSetId = 'myvsid', start = 1, end = 4, referenceBases = 'myref')
        gav = GAVariant.GAVariant(id='myid', variantSetId = 'myvsid', start = 1, end = 4, referenceBases = 'myref', names = ['a', 'b'], created = 12, updated = 16, referenceName= 'myrefname', alternateBases = ['G', 'T'], info = {'Test': 'True', 'Number': 5})

        min_gasvr = GASVResponse.GASVResponse()
        res = min_gasvr.gavresponse_info

        assert res['variants'] == []
        assert res['nextPageToken'] == None

        gasvr = GASVResponse.GASVResponse(variants=[min_gav, gav], nextPageToken = 'testToken')
        res = gasvr.gavresponse_info

        first_var = res['variants'][0].gavariant_info
        second_var = res['variants'][1].gavariant_info

        assert res['nextPageToken'] == 'testToken'
        assert first_var['id'] == 'myid'
        assert first_var['variantSetId'] == 'myvsid'
        assert first_var['start'] == 1
        assert first_var['end'] == 4
        assert first_var['referenceBases'] == 'myref'
        assert first_var['names'] == []
        assert first_var['created'] == None
        assert first_var['updated'] == None
        assert first_var['referenceName'] == ''
        assert first_var['alternateBases'] == []
        assert first_var['info'] == {}
     
        assert second_var['id'] == 'myid'
        assert second_var['variantSetId'] == 'myvsid'
        assert second_var['start'] == 1
        assert second_var['end'] == 4
        assert second_var['referenceBases'] == 'myref'
        assert second_var['names'] == ['a', 'b']
        assert second_var['created'] == 12
        assert second_var['updated'] == 16
        assert second_var['referenceName'] == 'myrefname'
        assert second_var['alternateBases'] == ['G', 'T']
        assert second_var['info'] == {'Test': 'True', 'Number': 5}

    def test_GACSResponse(self):
        gacs = GACallSet.GACallSet(id = 'csid', name = 'myName', sampleId = '12', variantSetIds = [0,1,2], created = 1234, updated = 2345, info = {'Test': 'True', 'Number': 5})
        min_gacs = GACallSet.GACallSet()

        min_gacsr = GACSResponse.GACSResponse()
        res = min_gacsr.gacsresponse_info

        assert res['callSets'] == []
        assert res['nextPageToken'] == None

        gacsr = GACSResponse.GACSResponse(callSets=[min_gacs, gacs], nextPageToken = 'testToken')
        res = gacsr.gacsresponse_info
        first_cs = res['callSets'][0].gacallset_info
        second_cs = res['callSets'][1].gacallset_info

        assert res['nextPageToken'] == 'testToken'

        assert first_cs['id'] == ""
        assert first_cs['name'] == None
        assert first_cs['sampleId'] == ""
        assert first_cs['variantSetIds'] == []
        assert first_cs['created'] == None
        assert first_cs['updated'] == None
        assert first_cs['info'] == {}

        assert second_cs['id'] == "csid"
        assert second_cs['name'] == 'myName'
        assert second_cs['sampleId'] == "12"
        assert second_cs['variantSetIds'] == [0,1,2]
        assert second_cs['created'] == 1234
        assert second_cs['updated'] == 2345
        assert second_cs['info'] == {'Test': 'True', 'Number': 5}

    def test_GASVSetResponse(self):
        min_gavs = GAVariantSet.GAVariantSet()
        gavs = GAVariantSet.GAVariantSet(id = 'myid', name = 'myname', referenceSetId = 'myrefsetid', datasetId = 'mydsit', metadata = [1, 2, 3, 4])
        min_gasvsr = GASVSetResponse.GASVSetResponse()
        res = min_gasvsr.gavsetresponse_info
      
        assert res['variantSets'] == []
        assert res['nextPageToken'] == None

        gasvsr = GASVSetResponse.GASVSetResponse(variantSets=[min_gavs, gavs], nextPageToken = 'testToken')
        res = gasvsr.gavsetresponse_info
        first_vs = res['variantSets'][0].gavariantset_info
        second_vs = res['variantSets'][1].gavariantset_info

        assert res['nextPageToken'] == 'testToken'

        assert first_vs['id'] == ''
        assert first_vs['name'] == ''
        assert first_vs['referenceSetId'] == ''
        assert first_vs['datasetId'] == ''
        assert first_vs['metadata'] == []

        assert second_vs['id'] == 'myid'
        assert second_vs['name'] == 'myname'
        assert second_vs['referenceSetId'] == 'myrefsetid'
        assert second_vs['datasetId'] == 'mydsit'
        assert second_vs['metadata'] == [1,2,3,4]

    def test_GAVariantSetMetadata(self):
        min_gavsmd = GAVariantSetMetadata.GAVariantSetMetadata()
        gavsmd = GAVariantSetMetadata.GAVariantSetMetadata(key = 'mykey', value = 'myval', id = 'myid', type = 'mytype', number = 'mynum', description = 'mydesc', info = {'Test': 'True', 'Number': 5})
        res = min_gavsmd.gavariantsetmetadata_info
        tmp = loads(min_gavsmd.getJSON())
   
        assert res['key'] == ''
        assert res['value'] == ''
        assert res['id'] == ''
        assert res['type'] == ''
        assert res['number'] == ''
        assert res['description'] == ''
        assert res['info'] == {}


        res = gavsmd.gavariantsetmetadata_info
        tmp = loads(gavsmd.getJSON())
   
        assert res['key'] == 'mykey'
        assert res['value'] == 'myval'
        assert res['id'] == 'myid'
        assert res['type'] == 'mytype'
        assert res['number'] == 'mynum'
        assert res['description'] == 'mydesc'
        assert res['info'] == {'Test': 'True', 'Number': 5}

