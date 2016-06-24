from flask import Blueprint
from flask import Flask
from flask import Response
from flask import current_app
from flask import json
from flask import jsonify
from flask import request
from ga4gh import tileSearch
from ga4gh import create_app

ga4gh = Blueprint('ga4gh', __name__)


def makeGAException(message, ecode, rcode):
    error = {
        'message': message,
        'error_code': ecode
    }
    GAException = json.jsonify(error)
    GAException.status_code = rcode
    return GAException


@ga4gh.errorhandler(405)
def bad_method(e):
    return jsonify(error=405, text=str(e)), 405


@ga4gh.route('/variants/search', methods=['POST'])
def variants_search():
    tileSearch.LoadConfig(current_app.config)
    if not request.json:
        return makeGAException(
            message='Bad Content Type, please send application/json',
            ecode=-1,
            rcode=415)

    try:
        # making empty variantSetId valid - consistent with old
        # documented version of the ga4gh api
        # variantSetId = request.json['variantSetId']
        variantSetIds = request.json.get('variantSetIds', None)
        referenceName = request.json.get('referenceName')
        startWindow = request.json['start']
        endWindow = request.json['end']

    except:
        return makeGAException(
            message='Required field missing: '
                    'variantSetIds, referenceName, start, and end are required',
            ecode=- 1,
            rcode=400)

    if not (referenceName and startWindow and endWindow):
        return makeGAException(
            message='Required field missing: '
                    'variantSetIds, referenceName, start, and end are required',
            ecode=- 1,
            rcode=400)

    callSetIds = request.json.get('callSetIds', None)
    pageSize = request.json.get('pageSize', None)
    pageToken = request.json.get('pageToken', None)
    if pageToken:
        pageToken = str(pageToken)

    try:
        search_lib = tileSearch.connectSearchLib(
            current_app.config['SEARCHLIB'])
        garesp = tileSearch.searchVariants(
            workspace=current_app.config['WORKSPACE'],
            arrayName=current_app.config['ARRAYNAME'],
            variantSetIds=variantSetIds,
            referenceName=referenceName,
            start=startWindow,
            end=endWindow,
            callSetIds=callSetIds,
            pageSize=pageSize,
            pageToken=pageToken,
            attrList=current_app.config['FIELDS'],
            searchLib=search_lib)

    except Exception as e:
        print e
        return makeGAException(message=e.message, ecode=500, rcode=500)

    return jsonify(garesp.gavresponse_info)


@ga4gh.route('/callsets/search', methods=['POST'])
def callset_search():
    if not request.json:
        return makeGAException(
            message='Bad Content Type, please send application/json',
            ecode=-1,
            rcode=415)

    vs_ids = request.json.get('variantSetIds', [])
    name = request.json.get('name', None)
    request.json.get('pageSize', None)
    request.json.get('pageToken', None)

    try:
        search_lib = tileSearch.connectSearchLib(
            current_app.config['SEARCHLIB'])
        garesp = tileSearch.searchCallSets(
            workspace=current_app.config['WORKSPACE'],
            arrayName=current_app.config['ARRAYNAME'],
            name=name,
            searchLib=search_lib)

    except:
        return makeGAException(
            message='search command exited abnormally', ecode=500, rcode=500)

    return jsonify(garesp.gacsresponse_info)


@ga4gh.route('/variantsets/search', methods=['POST'])
def variantset_search():
    if not request.json:
        return makeGAException(
            message='Bad Content Type, please send application/json',
            ecode=-1,
            rcode=415)
    datasetId = request.json.get('datasetId', "")
    pageSize = request.json.get('pageSize', None)
    pageToken = request.json.get('pageToken', None)

    try:
        garesp = tileSearch.searchVariantSets(
            datasetId=datasetId, pageSize=pageSize, pageToken=pageToken)

    except:
        return makeGAException(
            message='search command exited abnormally', ecode=500, rcode=500)

    return jsonify(garesp.gavsetresponse_info)
