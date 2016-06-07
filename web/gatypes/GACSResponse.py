import GACallSet
import json


class GACSResponse(object):
    """Call Set responses"""
    def __init__(self, callSets = [], nextPageToken = None):


        if nextPageToken:
            nextPageToken = str(nextPageToken)

        self.gacsresponse_info = {'callSets' : callSets, 'nextPageToken' : nextPageToken}

