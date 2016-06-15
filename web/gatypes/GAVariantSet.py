import json


class GAVariantSet(object):
    """Variant Set"""

    def __init__(self, id="", name="", referenceSetId="", datasetId="", metadata=[]):

        id = str(id)
        datasetId = str(datasetId)
        name = str(name)
        str(referenceSetId)

        self.gavariantset_info = {
            'id': id, 'name': name, 'referenceSetId': referenceSetId, 'datasetId': datasetId, 'metadata': metadata}

    def getJSON(self):
        return json.dumps(self.gavariantset_info)
