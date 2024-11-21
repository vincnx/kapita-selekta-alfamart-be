from datetime import datetime, UTC
from typing import Any, List
from bson import ObjectId
from flask import abort, g
from api.v1.middlewares.verifyRole import verifyRole
from common.db import dbInstance
from common.helpers.types import TypeProduct, TypeProductInput
from bson.errors import InvalidId
import api.v1.vendor.controller as vendorController
from pymongo.errors import WriteError
from werkzeug.exceptions import HTTPException

productCollection = dbInstance.db['PRODUCT']

def findAllProduct(params:dict[str, Any]) -> tuple[list[TypeProduct], int]:
    active = params.get('active', False)
    query = {}

    if active == 'true':
        query['activeStatus'] = True
    elif active == 'false':
        query['activeStatus'] = False

    try:
        allProductData = list(productCollection.find(query))

        return {
            'data': [
                {**product, '_id': str(product['_id'])}
                for product in allProductData
            ]
        }, 200
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

def findProductById(productId:str) -> tuple[TypeProduct, int]:
    try:
        productData = productCollection.find_one({
            '_id': ObjectId(productId)
        })
        if not productData:
            abort(404, 'Product Data Not Found')

        return {
            'data': {**productData, '_id': str(productData['_id'])}
        }, 200
    except InvalidId:
        abort(422, 'Invalid Product ID')
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

def findProductsByIds(productIds: List[str]) -> tuple[list[TypeProduct], int]:
    try:
        objectIds = [ObjectId(productId) for productId in productIds]
        
        products = list(productCollection.find(
            {'_id': {'$in': objectIds}}
        ))

        return {
            'data': [
                {**product, '_id': str(product['_id'])}
                for product in products
            ]
        }, 200
    except InvalidId:
        abort(422, 'Invalid Product ID')
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

@verifyRole(['inventory'])
def insertProduct(productInput:TypeProductInput) -> tuple[TypeProduct, int]:
    try:
        # check if product name already exists
        anotherProductData = validateUniqueField('name', productInput['name'])
        if anotherProductData:
            abort(409, 'Product Name Already Exists')

        # validate vendor data with BE
        vendorData = vendorController.findVendorById(productInput['vendorId'])[0]['data']

        productData = {
            'vendor': {
                'vendorName': vendorData['vendorName'],
                'vendorId': vendorData['_id']
            },
            'activeStatus': True,
            **productInput,
            'setup': {
                'createDate' : datetime.now(UTC),
                'updateDate': datetime.now(UTC),
                'createUser': g.user['_id'],
                'updateUser': g.user['_id']
            }
        }
        response = productCollection.insert_one(productData)

        return {**productData, '_id': str(response.inserted_id)}, 201
    except WriteError as e:
        error_message = e.details.get('errmsg', str(e))
        abort(422, error_message)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

@verifyRole(['inventory'])
def updateProduct(productId:str, productInput:TypeProductInput) -> tuple[TypeProduct, int]:
    try:
        # check if product data exists
        findProductById(productId)

        # check if another product name already exists
        anotherProductData = validateUniqueField('name', productInput['name'], productId)
        if anotherProductData:
            abort(409, 'Product Name Already Exists')
        
        # validate vendor data with BE
        vendorData = vendorController.findVendorById(productInput['vendorId'])[0]['data']

        productDataUpdated = productCollection.find_one_and_update(
            {'_id': ObjectId(productId)},
            {
                '$set': {
                    **productInput,
                    'vendor.vendorName': vendorData['vendorName'],
                    'vendor.vendorId': vendorData['_id'],
                    'setup.updateDate': datetime.now(UTC),
                    'setup.updateUser': g.user['_id']
                }
            }, 
            return_document=True
        )

        return {**productDataUpdated, '_id': str(productDataUpdated['_id'])}, 200
    except WriteError as e:
        errorMessage = e.details.get('errmsg', str(e))
        abort(422, errorMessage)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

@verifyRole(['inventory'])
def removeProduct(productId:str)->tuple[None, int]:
    try:
        # check if product data exists
        findProductById(productId)
    
        productCollection.update_one({
            '_id' : ObjectId(productId)
        }, {
            '$set': {
                'activeStatus': False
            }
        })
    except InvalidId:
        abort(422, 'Invalid Vendor ID')
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

    return None, 204

def validateUniqueField(fieldToValidate:str, valueToValidate:Any, excludeId:str = None)->TypeProduct:
    query = {
        fieldToValidate: valueToValidate,
    }
    if excludeId:
        query['_id'] = {'$ne': ObjectId(excludeId)}
        
    try:
        productData = productCollection.find_one(query)
    except Exception as e:
        abort(500, str(e))

    return productData