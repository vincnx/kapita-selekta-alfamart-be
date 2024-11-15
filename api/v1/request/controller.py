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
productCollection = dbInstance.db['PRODUCT']

def findAllRequest() -> tuple[dict[str, List[TypeRequest]], int]:
    userData = g.user
    if userData['userRole'] == 'inventory':
        try:
            allRequestData = list(requestCollection.find())
        except Exception as e:
            abort(500, str(e))
    elif userData['userRole'] == 'branch':
        try:
            allRequestData = list(requestCollection.find({
                'branch.branchId': userData['branch']['branchId']
            }))
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
    
    requestInputProductId = [ObjectId(product['productId']) for product in requestInput['product']]
    
    try:
        # validate data with BE
        productData = list(productCollection.find({
            '_id': {'$in': requestInputProductId}
        }, {'_id': 1, 'name': 1}))
    except InvalidId:
        abort(422, 'Invalid ProductId')
    except Exception as e:
        abort(500, str(e))
    
    productData = [{
        'productId': str(product['_id']),
        'name': product['name']
    } for product in productData]

    requestData = {
        'product': productData,
        'status': 'on request',
        'branch': g.user['branch'],
        'totalProduct': len(productData),
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

@verifyRole(['inventory'])
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
