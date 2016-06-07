import GAVariant
import json


class GASVResponse(object):
    """Variant responses"""
    def __init__(self, variants = [], nextPageToken = None):

        if nextPageToken:
            nextPageToken = str(nextPageToken)

        self.gavresponse_info = {'variants' : variants, 'nextPageToken' : nextPageToken}

