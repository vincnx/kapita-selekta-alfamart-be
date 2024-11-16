from datetime import UTC, datetime
from typing import List
from bson import ObjectId
from flask import abort, g
from api.v1.middlewares.verifyRole import verifyRole
from common.db import dbInstance
from common.helpers.types import TypeRequest, TypeRequestInput
from bson.errors import InvalidId
from pymongo.errors import WriteError
from pymongo import UpdateOne

requestCollection = dbInstance.db['REQUEST']
productCollection = dbInstance.db['PRODUCT']
branchCollection = dbInstance.db['VMS BRANCH']

def findAllRequest() -> tuple[dict[str, List[TypeRequest]], int]:
    try:
        userData = g.user
        if userData['userRole'] == 'inventory':
            allRequestData = list(requestCollection.find().sort([
                ('status', -1),
                ('setup.createDate', -1)
            ]))

        elif userData['userRole'] == 'branch':
            allRequestData = list(requestCollection.find({
                'branch.branchId': userData['branch']['branchId']
            }).sort([
                ('status', -1),
                ('setup.createDate', -1)
            ]))

        return {
            'data': [
                {**request, '_id': str(request['_id'])}
                for request in allRequestData
            ]
        }, 200
    except Exception as e:
        abort(500, str(e))

def findRequestById(requestId: str) -> tuple[dict[str, TypeRequest], int]:
    try:
        requestData = requestCollection.find_one({
            '_id': ObjectId(requestId),
        })
        if not requestData:
            return {
                'message': 'Request Data Not Found'
            }, 404

        return {
            'data': {**requestData, '_id': str(requestData['_id'])}
        }, 200
    except InvalidId:
        abort(422, 'Invalid Request ID')
    except Exception as e:
        abort(500, str(e))

@verifyRole(['branch'])
def insertRequest(requestInput: TypeRequestInput) -> tuple[dict[str, TypeRequest], int]:
    requestInputProductIds = [ObjectId(product['productId']) for product in requestInput['product']]
    try:
        # validate data with BE
        productData = list(productCollection.find({
            '_id': {'$in': requestInputProductIds}
        }, {'_id': 1, 'name': 1}))
        if len(productData) != len(requestInputProductIds):
            return {
                'message': 'One or more product not found'
            }, 422

        productData = [{
            'productId': str(product['_id']),
            'name': product['name'],
            'quantity': next(
                input_product['quantity'] 
                for input_product in requestInput['product'] 
                if str(product['_id']) == input_product['productId']
            )
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
        
        response = requestCollection.insert_one(requestData)

        return {
            'data': {**requestData, '_id': str(response.inserted_id)}
        }, 201
    except WriteError as e:
        errorMessage = e.details.get('errmsg', str(e))
        abort(422, errorMessage)
    except Exception as e:
        abort(500, str(e))

@verifyRole(['inventory'])
def acceptRequest(requestId: str) -> tuple[dict, int]:
    try:
        # get request data
        requestData = findRequestById(requestId)[0]['data']
        requestData.pop('_id')

        # get products from product collection
        productIds = [ObjectId(product['productId']) for product in requestData['product']]
        inventoryProducts = {
            str(product['_id']): product
            for product in productCollection.find(
                {'_id': {'$in': productIds}},
                {
                    '_id': 1, 
                    'count': 1,
                    'vendor': 1,
                    'merk': 1,
                    'condition': 1,
                    'name': 1
                }
            )
        }

        # check if products stock is enough for request
        for requestProduct in requestData['product']:
            currentProduct = inventoryProducts.get(requestProduct['productId'])
            if not currentProduct or currentProduct['count'] < requestProduct['quantity']:
                return {
                    'message': f'Insufficient quantity for product {requestProduct["name"]}'
                }, 400

        # Decrease main product inventory using bulk write
        decreaseInventoryQueries = [
            UpdateOne(
                {'_id': ObjectId(requestProduct['productId'])},
                {
                    '$inc': {'count': -requestProduct['quantity']},
                    '$set': {
                        'setup.updateDate': datetime.now(UTC),
                        'setup.updateUser': g.user['_id']
                    }
                }
            ) for requestProduct in requestData['product']
        ]
        productCollection.bulk_write(decreaseInventoryQueries)

        # check product in branch
        branchId = ObjectId(requestData['branch']['branchId'])
        branchProductIds = branchCollection.find_one({'_id': branchId}, {'_id': 0, 'product.productId': 1})
        branchProductIds = [product['productId'] for product in branchProductIds['product']]
        # filter product that already in branch
        newProductIds = [product['productId'] for product in requestData['product'] if product['productId'] not in branchProductIds]

        # insert new products to branch
        createBranchProductQueries = [
            UpdateOne(
                {'_id': branchId},
                {
                    '$push': {
                        'product': {
                            'productId': newProductId,
                            'name': inventoryProducts[newProductId]['name'],
                            'count': next(
                                request['quantity'] 
                                for request in requestData['product'] 
                                if request['productId'] == newProductId
                            ),
                            'vendor': inventoryProducts[newProductId]['vendor'],
                            'merk': inventoryProducts[newProductId]['merk'],
                            'condition': inventoryProducts[newProductId]['condition'],
                            'setup': {
                                'createDate': datetime.now(UTC),
                                'updateDate': datetime.now(UTC),
                                'createUser': g.user['_id'],
                                'updateUser': g.user['_id']
                            }
                        }
                    }
                }
            ) for newProductId in newProductIds
        ]
        if createBranchProductQueries:
            branchCollection.bulk_write(createBranchProductQueries)

        # update product in branch
        updateBranchProductQueries = [
            UpdateOne(
                {'_id': branchId, 'product.productId': requestProduct['productId']},
                {
                    '$inc': {'product.$.count': requestProduct['quantity']},
                    '$set': {
                        'product.$.setup.updateDate': datetime.now(UTC),
                        'product.$.setup.updateUser': g.user['_id']
                    }
                }
            ) for requestProduct in requestData['product'] if requestProduct['productId'] not in newProductIds
        ]
        if updateBranchProductQueries:
            branchCollection.bulk_write(updateBranchProductQueries)

        # update request data
        requestAccepted = requestCollection.find_one_and_update({
            '_id': ObjectId(requestId)
        }, {
            '$set': {
                'status': 'accepted',
                'setup.updateDate': datetime.now(UTC),
                'setup.updateUser': g.user['_id']
            }
        }, return_document=True)

        return {
            'data': {**requestAccepted, '_id': str(requestAccepted['_id'])}
        }, 200

    except WriteError as e:
        errorMessage = e.details.get('errmsg', str(e))
        abort(422, errorMessage)
    except Exception as e:
        print(e)
        abort(500, str(e))