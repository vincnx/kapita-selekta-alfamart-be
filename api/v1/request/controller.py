from datetime import UTC, datetime
from typing import List
from bson import ObjectId
from flask import abort, g
from api.v1.middlewares.verifyRole import verifyRole
from common.db import dbInstance
from common.helpers.types import TypeRequest, TypeRequestInput
from bson.errors import InvalidId
from pymongo.errors import WriteError

requestCollection = dbInstance.db['REQUEST']

def findAllRequest() -> tuple[dict[str, List[TypeRequest]], int]:
    try:
        allRequestData = list(requestCollection.find())
    except Exception as e:
        abort(500, str(e))

    return {
        'data': [
            {**request, '_id': str(request['_id'])}
            for request in allRequestData
        ]
    }, 200

def findRequestById(requestId: str) -> tuple[dict[str, TypeRequest], int]:
    try:
        requestData = requestCollection.find_one({
            '_id': ObjectId(requestId),
        })
    except InvalidId:
        abort(422, 'Invalid Request ID')
    except Exception as e:
        abort(500, str(e))
    if not requestData:
        abort(404, 'Request Data Not Found')

    return {
        'data': {**requestData, '_id': str(requestData['_id'])}
    }, 200

@verifyRole(['branch'])
def insertRequest(requestInput: TypeRequestInput) -> tuple[dict[str, TypeRequest], int]:
    requestData = {
        **requestInput,
        'status': 'on request',
        'branch': g.user['branch'],
        'totalProduct': len(requestInput),
        'setup': {
            'createDate': datetime.now(UTC),
            'updateDate': datetime.now(UTC),
            'createUser': g.user['_id'],
            'updateUser': g.user['_id']
        }
    }
    
    try:
        response = requestCollection.insert_one(requestData)
    except WriteError as e:
        error_message = e.details.get('errmsg', str(e))
        abort(422, error_message)
    except Exception as e:
        abort(500, str(e))

    return {
        'data': {**requestData, '_id': str(response.inserted_id)}
    }, 201

@verifyRole(['branch'])
def acceptRequest(requestId: str):
    # check if request data exists
    requestData = findRequestById(requestId)[0]['data']
    requestData.pop('_id')

    requestData = {
        **requestData, 
        'status': 'accepted',
        'setup': {
            **requestData['setup'],
            'updateDate': datetime.now(UTC),
            'updateUser': g.user['_id']
        }
    }
    print(requestData)

    try:
        requestAccepted = requestCollection.find_one_and_update({
            '_id': ObjectId(requestId)
        }, {
            '$set': requestData
        }, return_document=True)
    except WriteError as e:
        error_message = e.details.get('errmsg', str(e))
        abort(422, error_message)
    except Exception as e:
        abort(500, str(e))

    return {**requestAccepted, '_id': str(requestAccepted['_id'])}, 200
