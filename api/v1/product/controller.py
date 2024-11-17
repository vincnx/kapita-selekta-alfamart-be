from datetime import datetime, UTC
from typing import Any, List
from bson import ObjectId
from flask import abort
from common.db import dbInstance
from common.helpers.types import TypeProduct, TypeProductInput
from bson.errors import InvalidId
import api.v1.vendor.controller as vendorController
from pymongo.errors import WriteError

productCollection = dbInstance.db['PRODUCT']

def findAllProduct() -> tuple[list[TypeProduct], int]:
    try:
        allProductData = list(productCollection.find())

        return {
            'data': [
                {**product, '_id': str(product['_id'])}
                for product in allProductData
            ]
        }, 200
    except Exception as e:
        abort(500, str(e))

def findProductById(productId:str)->tuple[TypeProduct, int]:
    # check if product data exists
    try:
        productData = productCollection.find_one({
            '_id': ObjectId(productId)
        })
    except InvalidId:
        abort(422, 'Invalid Product ID')
    except Exception as e:
        abort(500, str(e))
    if not productData:
        abort(404, 'Product Data Not Found')

    return {
        'data': {**productData, '_id': str(productData['_id'])}
    }, 200

def findProductsByIds(productIds: List[str]) -> tuple[list[TypeProduct], int]:
    try:
        objectIds = [ObjectId(productId) for productId in productIds]
    except InvalidId:
        abort(422, 'Invalid ProductId')
        
    try:
        products = list(productCollection.find({
            '_id': {'$in': objectIds}
        }))
    except Exception as e:
        abort(500, str(e))

    return {
        'data': [
            {**product, '_id': str(product['_id'])}
            for product in products
        ]
    }, 200

def insertProduct(productInput:TypeProductInput)->tuple[TypeProduct, int]:
    # check if product name already exists
    anotherProductData = validateUniqueField('name', productInput['name'])
    if anotherProductData:
        abort(409, 'Product Name Already Exists')

    productData = {
        'vendor': {
            'vendorName': vendorController.findVendorById(productInput['vendorId'])[0]['data']['vendorName'],
            'vendorId': productInput.pop('vendorId')
        },
        **productInput,
        'setup': {
            'createDate' : datetime.now(UTC),
            'updateDate': datetime.now(UTC),
            # TODO: change to user data
            'createUser': 'SYSTEM',
            'updateUser': 'SYSTEM'
        }
    }

    try:
        response = productCollection.insert_one(productData)
    except WriteError as e:
        error_message = e.details.get('errmsg', str(e))
        abort(422, error_message)
    except Exception as e:
        abort(500, str(e))
    
    return {**productData, '_id': str(response.inserted_id)}, 201

def updateProduct(productId:str, productInput:TypeProductInput)->tuple[TypeProduct, int]:
    # check if product data exists
    productData = findProductById(productId)[0]['data']

    # check if another product name already exists
    anotherProductData = validateUniqueField('name', productInput['name'], productId)
    if anotherProductData:
        abort(409, 'Product Name Already Exists')

    productData = {
        'vendor': {
            'vendorName': vendorController.findVendorById(productInput['vendorId'])[0]['data']['vendorName'],
            'vendorId': productInput.pop('vendorId')
        },
        **productInput,
        'setup': {
            **productData['setup'],
            'updateDate': datetime.now(UTC),
            # TODO: change to user data
            'updateUser': 'SYSTEM'
        }
    }

    try:
        productDataUpdated = productCollection.find_one_and_update({
            '_id': ObjectId(productId)
        }, {
            '$set': productData
        }, return_document=True)
    except WriteError as e:
        error_message = e.details.get('errmsg', str(e))
        abort(422, error_message)
    except Exception as e:
        abort(500, str(e))

    return {**productDataUpdated, '_id': str(productDataUpdated['_id'])}, 200

def removeProduct(productId:str)->tuple[None, int]:
    # check if product data exists
    try:
        productData = validateUniqueField('_id', ObjectId(productId))
    except InvalidId:
        abort(422, 'Invalid Vendor ID')
    if not productData:
        abort(404, 'Vendor Data Not Found')
    
    # remove product data
    try:
        productCollection.delete_one({
            '_id' : ObjectId(productId)
        })
    except Exception as e:
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

def validateRequiredField(productInput:TypeProductInput)->dict:
    try:
        validatedRequiredField = {
            'name': productInput['name'],
            'merk' : productInput['merk'],
            'condition': productInput['condition'],
            'count': productInput['count'],
            'vendor': {
                'vendorId': productInput['vendorId']
            },
            'setup': {
                'createDate': productInput.get('setup', {}).get('createDate', datetime.now(UTC)),
                'updateDate': datetime.now(UTC),
                # TODO: change to user data
                'createUser': productInput.get('setup', {}).get('createUser', 'SYSTEM'),
                'updateUser': 'SYSTEM'
            }
        }
    except KeyError as e:
        abort(422, f'Missing required field: {str(e)}')
    except Exception as e:
        abort(500, str(e))
    if validatedRequiredField['count'] <= 0:
        abort(422, 'Count must be greater than 0')

    return validatedRequiredField