import json


class GAVariantSetMetadata(object):
    """GAVariantSet Metadata representation for ga4gh responses"""

    def __init__(self, key='', value='', id='', type='', number='', description='', info={}):

        if key:
            key = str(key)

        if value:
            value = str(value)

        if id:
            id = str(id)

        if type:
            type = str(type)

        if number:
            number = str(number)

        if description:
            description = str(description)

        self.gavariantsetmetadata_info = {'key': key, 'value': value, 'id': id,
                                          'type': type, 'number': number, 'description': description, 'info': info}

    def getJSON(self):
        return json.dumps(self.gavariantsetmetadata_info)
