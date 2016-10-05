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

from flask import current_app
from flask.ext.cors import CORS
from flask.ext.cors import cross_origin

ga4ghPath = "./web/"
sys.path.append("./web/")

config.initConfig(os.path.join(ga4ghPath, "ga4gh_test.conf"))

from web.ga4gh import create_app
application = create_app('config.LoadedConfig')
from web.ga4gh import views

ts = views.tileSearch
ctx = application.app_context()
ctx.push()

current_app.config.from_object(config.LoadedConfig)
ts.LoadConfig(current_app.config)
test_search = ts.connectSearchLib(current_app.config['SEARCHLIB'])


def test_searchVariants():
    gold_res = {'nextPageToken': None,
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
    nocall_res = {'nextPageToken': None,
                  'variants': [{'alternateBases': ['A'],
                                'calls': [],
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
    page_res = {'nextPageToken': 'test_1_115060270_1',
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
    empty_cs_res = {'nextPageToken': None,
                    'variants': [{'alternateBases': ['A'],
                                  'calls': [],
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
    empty_res = {'nextPageToken': None, 'variants': []}

    res = ts.searchVariants(
        workspace=current_app.config['WORKSPACE'],
        arrayName=current_app.config['ARRAYNAME'],
        referenceName="1",
        start=1,
        end=249250621,
        variantSetIds=["testing"],
        searchLib=test_search,
        attrList=current_app.config['FIELDS'])
    tmp = res.gavresponse_info
    assert tmp == gold_res

    res = ts.searchVariants(
        workspace=current_app.config['WORKSPACE'],
        arrayName=current_app.config['ARRAYNAME'],
        referenceName="1",
        start=1,
        end=249250621,
        variantSetIds=[],
        searchLib=test_search,
        attrList=current_app.config['FIELDS'])
    tmp = res.gavresponse_info
    assert tmp == gold_res

    res = ts.searchVariants(
        workspace=current_app.config['WORKSPACE'],
        arrayName=current_app.config['ARRAYNAME'],
        referenceName="1",
        start=1,
        end=249250621,
        variantSetIds=["0b8a597e-90ae-40d3-b834-8d4ff108e28e"],
        searchLib=test_search,
        attrList=current_app.config['FIELDS'])
    tmp = res.gavresponse_info
    assert tmp == gold_res

    res = ts.searchVariants(
        workspace=current_app.config['WORKSPACE'],
        arrayName=current_app.config['ARRAYNAME'],
        referenceName="1",
        start=1,
        end=249250621,
        variantSetIds=["testing"],
        searchLib=test_search,
        attrList=current_app.config['FIELDS'],
        pageSize=-2)
    tmp = res.gavresponse_info
    assert tmp == gold_res

    res = ts.searchVariants(
        workspace=current_app.config['WORKSPACE'],
        arrayName=current_app.config['ARRAYNAME'],
        referenceName="1",
        start=1,
        end=249250621,
        variantSetIds=["testing"],
        searchLib=test_search,
        attrList=current_app.config['FIELDS'],
        pageSize=0)
    tmp = res.gavresponse_info
    assert tmp == gold_res

    res = ts.searchVariants(
        workspace=current_app.config['WORKSPACE'],
        arrayName=current_app.config['ARRAYNAME'],
        referenceName="1",
        start=1,
        end=249250621,
        variantSetIds=["testing"],
        searchLib=test_search,
        attrList=current_app.config['FIELDS'],
        pageSize=1)
    tmp = res.gavresponse_info
    assert tmp == page_res

    res = ts.searchVariants(
        workspace=current_app.config['WORKSPACE'],
        arrayName=current_app.config['ARRAYNAME'],
        referenceName="1",
        start=1,
        end=249250621,
        variantSetIds=["testing"],
        searchLib=test_search,
        attrList=current_app.config['FIELDS'],
        pageSize=2)
    tmp = res.gavresponse_info
    assert tmp == gold_res

    res = ts.searchVariants(
        workspace=current_app.config['WORKSPACE'],
        arrayName=current_app.config['ARRAYNAME'],
        referenceName="1",
        start=1,
        end=249250621,
        variantSetIds=["testing"],
        searchLib=test_search,
        attrList=current_app.config['FIELDS'],
        pageToken='test_1_115060270_1',
        pageSize=1)
    tmp = res.gavresponse_info
    assert tmp == empty_res

    min_res = ts.searchVariants(
        workspace=current_app.config['WORKSPACE'],
        arrayName=current_app.config['ARRAYNAME'],
        referenceName="1",
        start=1,
        end=249250621,
        searchLib=test_search,
        variantSetIds=["testing"])
    tmp = min_res.gavresponse_info
    assert tmp == gold_res

    res = ts.searchVariants(
        workspace=current_app.config['WORKSPACE'],
        arrayName=current_app.config['ARRAYNAME'],
        referenceName="1",
        start=1,
        end=249250621,
        variantSetIds=["testing"],
        searchLib=test_search,
        attrList=current_app.config['FIELDS'],
        callSetIds=['f4e59886-325f-4427-91ff-9e9be6635e20'])
    tmp = res.gavresponse_info
    assert tmp == gold_res

    res = ts.searchVariants(
        workspace=current_app.config['WORKSPACE'],
        arrayName=current_app.config['ARRAYNAME'],
        referenceName="1",
        start=1,
        end=249250621,
        variantSetIds=["testing"],
        searchLib=test_search,
        attrList=current_app.config['FIELDS'],
        callSetIds=[])
    tmp = res.gavresponse_info
    assert tmp == nocall_res

    res = ts.searchVariants(
        workspace=current_app.config['WORKSPACE'],
        arrayName=current_app.config['ARRAYNAME'],
        referenceName="1",
        start=1,
        end=249250621,
        variantSetIds=["testing"],
        searchLib=test_search,
        attrList=current_app.config['FIELDS'],
        callSetIds=[])
    tmp = res.gavresponse_info
    assert tmp == empty_cs_res

    res = ts.searchVariants(
        workspace=current_app.config['WORKSPACE'],
        arrayName=current_app.config['ARRAYNAME'],
        referenceName="1",
        start=1,
        end=249250621,
        variantSetIds=["testing"],
        searchLib=test_search,
        attrList=current_app.config['FIELDS'],
        callSetIds=['f4e59886-325f-4427-91ff-9e9be6635e29'])
    tmp = res.gavresponse_info
    assert tmp == empty_res
