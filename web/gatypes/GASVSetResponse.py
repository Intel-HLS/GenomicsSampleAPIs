import GAVariantSet
import json


class GASVSetResponse(object):
    """Variant Set responses"""
    def __init__(self, variantSets = [], nextPageToken = None):
        self.gavsetresponse_info = {'variantSets' : variantSets, 'nextPageToken' : nextPageToken}
