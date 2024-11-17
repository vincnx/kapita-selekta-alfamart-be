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
from werkzeug.exceptions import HTTPException

branchCollection = dbInstance.db['VMS BRANCH']

def findAllBranch() -> tuple[dict[str, List[TypeBranch]], int]:
    try:
        allBranchData = list(branchCollection.find())
        
        return {
            'data': [
                {**branch, '_id': str(branch['_id'])}
                for branch in allBranchData
            ]
        }, 200
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

def findBranchById(branchId: str) -> tuple[dict[str, TypeBranch], int]:
    try:
        branchData = branchCollection.find_one({
            '_id': ObjectId(branchId),
        })
        if not branchData:
            abort(404, 'Branch Data Not Found')

        return {
            'data': {**branchData, '_id': str(branchData['_id'])}
        }, 200
    except InvalidId:
        abort(422, 'Invalid Branch ID')
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

@verifyRole(['branch'])
def findBranchByUser() -> tuple[dict[str, TypeBranch], int]:
    userData = g.user

    try:
        branchData = branchCollection.find_one({
            '_id': ObjectId(userData['branch']['branchId'])
        })
        if not branchData:
            abort(404, 'Branch Data Not Found')

        return {
            'data': {**branchData, '_id': str(branchData['_id'])}
        }, 200
    except InvalidId:
        abort(422, 'Invalid Branch ID')
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

@verifyRole(['branch'])
def findAllBranchProductByUser() -> tuple[dict[str, List[TypeBranchProduct]], int]:
    userData = g.user

    try:
        branchData = branchCollection.find_one({
            '_id': ObjectId(userData['branch']['branchId'])
        })
        if not branchData:
            abort(404, 'Branch Data Not Found')

        return {
            'data': branchData['product']
        }, 200
    except InvalidId:
        abort(422, 'Invalid Branch ID')
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

@verifyRole(['branch'])
def findBranchProductByIdAndUser(productId: str) -> tuple[dict[str, TypeBranchProduct], int]:
    userData = g.user

    try:
        branchData = branchCollection.find_one(
            {
                '_id': ObjectId(userData['branch']['branchId']),
                'product.productId': productId
            }, 
            {'product.$': 1}
        )
        if not branchData or not branchData.get('product'):
            abort(404, 'Product Not Found')

        return {
            'data': branchData['product'][0]
        }, 200
    except InvalidId:
        abort(422, 'Invalid Product ID')
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

@verifyRole(['branch'])
def insertBranchProductByUser(branchProductInput: TypeBranchProductInput) -> tuple[dict[str, TypeBranchProduct], int]:
    userData = g.user
    
    try:
        # check if product already exist
        anotherBranchProductData = branchCollection.find_one({
            '_id': ObjectId(userData['branch']['branchId']),
            'product.productId': branchProductInput['productId']
        })
        if anotherBranchProductData:
            abort(422, 'Product already exists in this branch')

        # get product data from BE
        productData = findProductById(branchProductInput['productId'])[0]['data']
        productData['productId'] = productData['_id']
        productData.pop('_id')

        branchDataUpdated = branchCollection.find_one_and_update(
            {'_id': ObjectId(userData['branch']['branchId'])}, 
            {
                '$push': {
                    'product': {
                        **productData,
                        'count': branchProductInput['count'],
                        'setup': {
                            'createDate': datetime.now(UTC),
                            'updateDate': datetime.now(UTC),
                            'createUser': userData['_id'],
                            'updateUser': userData['_id']
                        }
                    }
                },
                '$set': {
                    'setup.updateDate': datetime.now(UTC),
                    'setup.updateUser': userData['_id']
                }
            },
            return_document=True
        )

        return {**branchDataUpdated, '_id': str(branchDataUpdated['_id'])}, 200
    except WriteError as e:
        errorMessage = e.details.get('errmsg', str(e))
        abort(422, errorMessage)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

@verifyRole(['branch'])
def updateBranchProductByIdAndUser(productId: str, branchProductInput: TypeBranchProductInput) -> tuple[dict[str, TypeBranchProduct], int]:
    userData = g.user
    
    try:
        # check if branch product exist
        findBranchProductByIdAndUser(productId)
        
        branchDataUpdated = branchCollection.find_one_and_update(
            {
                '_id': ObjectId(userData['branch']['branchId']),
                'product.productId': productId
            }, 
            {
                '$set': {
                    'product.$.count': branchProductInput['count'],
                    'product.$.setup.updateDate': datetime.now(UTC),
                    'product.$.setup.updateUser': userData['_id'],
                    'setup.updateDate': datetime.now(UTC),
                    'setup.updateUser': userData['_id']
                }
            }, 
            return_document=True
        )

        return {**branchDataUpdated, '_id': str(branchDataUpdated['_id'])}, 200
    except WriteError as e:
        errorMessage = e.details.get('errmsg', str(e))
        abort(422, errorMessage)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))