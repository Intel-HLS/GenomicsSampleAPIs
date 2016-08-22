"""
  The MIT License (MIT)
  Copyright (c) 2016 Intel Corporation

  Permission is hereby granted, free of charge, to any person obtaining a copy of 
  this software and associated documentation files (the "Software"), to deal in 
  the Software without restriction, including without limitation the rights to 
  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
  the Software, and to permit persons to whom the Software is furnished to do so, 
  subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all 
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import web.config as config
import sys
import os
import json
import unittest

from flask import current_app
from flask.ext.cors import CORS
from flask.ext.cors import cross_origin

ga4ghPath = "./web/"
sys.path.append("./web/")

config.initConfig(os.path.join(ga4ghPath, "ga4gh_test.conf"))

from web.ga4gh import create_app
from web.ga4gh.views import ga4gh

payload = {
    "end": 75908600,
    "pageToken": None,
    "start": 1,
    "callSetIds": None,
    "referenceName": "1",
    "variantSetIds": ["testing"]}
content_payload = {
    "end": 249250621,
    "pageToken": None,
    "start": 1,
    "callSetIds": None,
    "referenceName": "1",
    "variantSetIds": ["testing"]}
content_res = {'nextPageToken': None,
               'variants': [{'alternateBases': ['A'],
                             'calls': [{'callSetId': 'f4e59886-325f-4427-91ff-9e9be6635e20',
                                        'callSetName': 'SNVMix2',
                                        'genotype': [1,
                                                     0],
                                        'genotypeLikelihood': [],
                                        'info': {},
                                        'phaseset': None}],
                             'created': None,
                             'end': 115060271,
                             'id': 1,
                             'info': {},
                             'names': [],
                             'referenceBases': 'C',
                             'referenceName': '1',
                             'start': 115060271,
                             'updated': None,
                             'variantSetId': u'0b8a597e-90ae-40d3-b834-8d4ff108e28e'}]}

empty_vs = {"nextPageToken": None, "variants": []}


class TestViews(unittest.TestCase):

    def setUp(self):
        self.application = create_app('config.LoadedConfig')
        self.ctx = self.application.app_context()
        self.ctx.push()
        current_app.config.from_object(config.LoadedConfig)
        current_app.register_blueprint(ga4gh)
        current_app.testing = True
        self.tester = current_app.test_client()

    def test_variant_search(self):
        myPayload = json.dumps(payload)
        myDataPayload = json.dumps(content_payload)
        empty_res = json.loads(json.dumps(empty_vs))
        dataGold = json.loads(json.dumps(content_res))

        response = self.tester.post(
            '/variants/search',
            data=myPayload,
            content_type='application/json')
        my_res = json.loads(response.data)
        assert my_res == empty_res

        badData = json.dumps({"end": 75908600,
                              "pageToken": None,
                              "start": 1,
                              "referenceName": "1",
                              "variantSetIds": ["testing"]})
        response = self.tester.post(
            '/variants/search', data=badData, content_type='application/json')
        my_res = json.loads(response.data)
        assert my_res == empty_res

        badData = json.dumps({"pageToken": None,
                              "start": 1,
                              "callSetIds": None,
                              "referenceName": "1",
                              "variantSetIds": ["testing"]})
        response = self.tester.post(
            '/variants/search', data=badData, content_type='application/json')
        my_res = json.loads(response.data)
        assert my_res['error_code'] == -1
        assert my_res[
            'message'] == 'Required field missing: variantSetIds, referenceName, start, and end are required'

        badData = json.dumps({"end": 75908600,
                              "pageToken": None,
                              "callSetIds": None,
                              "referenceName": "1",
                              "variantSetIds": ["testing"]})
        response = self.tester.post(
            '/variants/search', data=badData, content_type='application/json')
        my_res = json.loads(response.data)
        assert my_res['error_code'] == -1
        assert my_res[
            'message'] == 'Required field missing: variantSetIds, referenceName, start, and end are required'

        badData = json.dumps({"end": 75908600,
                              "pageToken": None,
                              "start": 1,
                              "callSetIds": None,
                              "variantSetIds": ["testing"]})
        response = self.tester.post(
            '/variants/search', data=badData, content_type='application/json')
        my_res = json.loads(response.data)
        assert my_res['error_code'] == -1
        assert my_res[
            'message'] == 'Required field missing: variantSetIds, referenceName, start, and end are required'

        response = self.tester.post(
            '/variants/search',
            data=myDataPayload,
            content_type='application/json')
        my_res = json.loads(response.data)
        assert my_res == dataGold

        content_payload['variantSetIds'] = None
        myDataPayload = json.dumps(content_payload)
        response = self.tester.post(
            '/variants/search',
            data=myDataPayload,
            content_type='application/json')
        my_res = json.loads(response.data)
        assert my_res == dataGold

        content_payload['pageSize'] = -2
        myDataPayload = json.dumps(content_payload)
        response = self.tester.post(
            '/variants/search',
            data=myDataPayload,
            content_type='application/json')
        my_res = json.loads(response.data)
        assert my_res == dataGold

        content_payload['pageSize'] = -1
        myDataPayload = json.dumps(content_payload)
        response = self.tester.post(
            '/variants/search',
            data=myDataPayload,
            content_type='application/json')
        my_res = json.loads(response.data)
        assert my_res == dataGold

        content_payload['pageSize'] = 0
        myDataPayload = json.dumps(content_payload)
        response = self.tester.post(
            '/variants/search',
            data=myDataPayload,
            content_type='application/json')
        my_res = json.loads(response.data)
        assert my_res == dataGold

        content_payload['pageSize'] = 4
        myDataPayload = json.dumps(content_payload)
        response = self.tester.post(
            '/variants/search',
            data=myDataPayload,
            content_type='application/json')
        my_res = json.loads(response.data)
        assert my_res == dataGold

        content_res['nextPageToken'] = 'test_1_115060270_1'
        dataGold = json.loads(json.dumps(content_res))
        content_payload['pageSize'] = 1
        myDataPayload = json.dumps(content_payload)
        response = self.tester.post(
            '/variants/search',
            data=myDataPayload,
            content_type='application/json')
        my_res = json.loads(response.data)
        assert my_res == dataGold

    def tearDown(self):
        self.ctx.pop()
