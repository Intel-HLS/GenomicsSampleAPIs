import GACall
import json


class GAVariant(object):
    """GAVariant representation for ga4gh responses"""
    def __init__(self, id, variantSetId, start, end, referenceBases, names = [], created = None, updated = None, referenceName = '', alternateBases = [], info = {}, calls = []):

        start = long(start)
        end= long(end)

        if referenceBases:
            referenceBases = str(referenceBases)

        if created:
            created = long(created)

        if updated:
            updated= long(updated)

        self.gavariant_info = {'id' : id, 'variantSetId' : variantSetId, 'names' : names, 'created' : created, 'updated' : updated, 'referenceName' : referenceName, 'start' : start, 'end' : end, 'referenceBases' : referenceBases, 'alternateBases' : alternateBases, 'info' : info, 'calls' :calls}

    def getJSON(self):
        return json.dumps(self.gavariant_info)
