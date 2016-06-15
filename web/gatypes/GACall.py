import json


class GACall(object):
    """Base GACall representation for ga4gh responses"""

    def __init__(self, callSetId="", callSetName=None, genotype=[],
                 phaseset=None, genotypeLikelihood=[], info={}):

        if callSetName:
            callSetName = str(callSetName)

        if phaseset:
            phaseset = str(phaseset)

        self.gacall_info = {'callSetId': str(callSetId), 'callSetName': callSetName, 'genotype': genotype,
                            'phaseset': phaseset, 'genotypeLikelihood': genotypeLikelihood, 'info': info}

    def getJSON(self):
        return json.dumps(self.gacall_info)
