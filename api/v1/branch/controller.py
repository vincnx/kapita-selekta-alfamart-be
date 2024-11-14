from datetime import datetime, UTC
from typing import List
from bson import ObjectId
from flask import abort, g
from api.v1.middlewares.verifyRole import verifyRole
from api.v1.product.controller import findProductById
from common.db import dbInstance
from common.helpers.types import TypeBranch, TypeBranchProduct, TypeBranchProductInput
from bson.errors import InvalidId
from pymongo.errors import WriteError

branchCollection = dbInstance.db['VMS BRANCH']

def findAllBranch() -> tuple[dict[str, List[TypeBranch]], int]:
    try:
        allBranchData = list(branchCollection.find())
    except Exception as e:
        abort(500, str(e))

    return {
        'data': [
            {**branch, '_id': str(branch['_id'])}
            for branch in allBranchData
        ]
    }, 200

def findBranchById(branchId: str) -> tuple[dict[str, TypeBranch], int]:
    try:
        branchData = branchCollection.find_one({
            '_id': ObjectId(branchId),
        })
    except InvalidId:
        abort(422, 'Invalid Branch ID')
    except Exception as e:
        abort(500, str(e))
    if not branchData:
        abort(404, 'Branch Data Not Found')

    return {
        'data': {**branchData, '_id': str(branchData['_id'])}
    }, 200

@verifyRole(['branch'])
def findBranchByUser() -> tuple[dict[str, TypeBranch], int]:
    userData = g.user

    try:
        branchData = branchCollection.find_one({
            '_id': ObjectId(userData['branch']['branchId'])
        })
    except InvalidId:
        abort(422, 'Invalid Branch ID')
    except Exception as e:
        abort(500, str(e))
    if not branchData:
        abort(404, 'Branch Data Not Found')

    return {
        'data': {**branchData, '_id': str(branchData['_id'])}
    }, 200

@verifyRole(['branch'])
def findAllBranchProductByUser() -> tuple[dict[str, List[TypeBranchProduct]], int]:
    userData = g.user

    try:
        branchData = branchCollection.find_one({
            '_id': ObjectId(userData['branch']['branchId'])
        })
    except InvalidId:
        abort(422, 'Invalid Branch ID')
    except Exception as e:
        abort(500, str(e))
    if not branchData:
        abort(404, 'Branch Data Not Found')

    return {
        'data': branchData['product']
    }, 200

@verifyRole(['branch'])
def findBranchProductByIdAndUser(productId: str) -> tuple[dict[str, TypeBranchProduct], int]:
    userData = g.user

    try:
        branchData = branchCollection.find_one({
            '_id': ObjectId(userData['branch']['branchId']),
            'product._id': productId
        }, 
        {'product.$': 1})
    except InvalidId:
        abort(422, 'Invalid Product ID')
    except Exception as e:
        abort(500, str(e))
    
    if not branchData or not branchData.get('product'):
        abort(404, 'Product Not Found')

    return {
        'data': branchData['product'][0]
    }, 200

@verifyRole(['branch'])
def insertBranchProductByUser(branchProductInput: TypeBranchProductInput) -> tuple[dict[str, TypeBranchProduct], int]:
    branchData = findBranchByUser()[0]['data']
    branchData.pop('_id')
    
    # check if product already exist
    existing_product = branchCollection.find_one({
        '_id': ObjectId(g.user['branch']['branchId']),
        'product.productId': branchProductInput['productId']
    })
    if existing_product:
        abort(422, 'Product already exists in this branch')

    # get product data
    productData = findProductById(branchProductInput['productId'])[0]['data']
    productData['productId'] = productData['_id']
    productData.pop('_id')

    branchData = {
        **branchData,
        'product': branchData['product'] + [{
            **productData,
            'count': branchProductInput['count'],
            'setup': {
                'createDate': datetime.now(UTC),
                'updateDate': datetime.now(UTC),
                'createUser': g.user['_id'],
                'updateUser': g.user['_id']
            }
        }]
    }

    try:
        branchDataUpdated = branchCollection.find_one_and_update({
            '_id': ObjectId(g.user['branch']['branchId'])
        }, {
            '$set': branchData
        }, return_document=True)
    except WriteError as e:
        errorMessage = e.details.get('errmsg', str(e))
        abort(422, errorMessage)
    except Exception as e:
        abort(500, str(e))

    return {**branchDataUpdated, '_id': str(branchDataUpdated['_id'])}, 200