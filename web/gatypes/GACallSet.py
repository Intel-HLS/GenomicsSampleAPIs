import json


class GACallSet(object):
    """Base GACallSet representation for ga4gh responses"""

    def __init__(self, id="", name=None, sampleId="",
                 variantSetIds=[], created=None, updated=None, info={}):

        id = str(id)
        sampleId = str(sampleId)

        if name:
            name = str(name)

        if created:
            created = long(created)

        if updated:
            updated = long(updated)

        self.gacallset_info = {
            'id': id,
            'name': name,
            'sampleId': sampleId,
            'variantSetIds': variantSetIds,
            'created': created,
            'updated': updated,
            'info': info}

    def getJSON(self):
        return json.dumps(self.gacallset_info)
