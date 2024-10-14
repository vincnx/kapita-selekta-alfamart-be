from datetime import datetime, UTC
from typing import Any
from bson import ObjectId
from common.db import dbInstance
from bson.errors import InvalidId
from common.helpers.types import TypeVendor, TypeVendorInput
from flask import abort

vendorCollection = dbInstance.db['VMS VENDOR']

def findAllVendor()->tuple[list[TypeVendor], int]:
    # get all vendor data
    try:
        allVendorData = list(vendorCollection.find({
            'activeStatus': True
        }, {
            'setup': 0}
        ))
    except Exception as e:
        abort(500, str(e))
    
    return [
        {**vendor, '_id': str(vendor['_id'])}
        for vendor in allVendorData
    ], 200

def findVendorById(vendorId:str)->tuple[TypeVendor, int]:
    # check if vendor data exists
    try:
        vendorData = vendorCollection.find_one({
            '_id': ObjectId(vendorId),
            'activeStatus': True
        })
    except InvalidId:
        abort(422, 'Invalid Vendor ID')
    except Exception as e:
        abort(500, str(e))
    if not vendorData:
        abort(404, 'Vendor Data Not Found')

    return {**vendorData, '_id': str(vendorData['_id'])}, 200

def insertVendor(vendorInput:TypeVendorInput)->tuple[TypeVendor, int]:
    # check if vendor name already exists
    anotherVendorData = validateUniqueField('vendorName', vendorInput['vendorName'].lower())
    if anotherVendorData:
        abort(409, 'Vendor Name Already Exists')

    # validate required field
    vendorData = vaildateRequiredField(vendorInput)

    # insert vendor data
    try:
        response = vendorCollection.insert_one(vendorData)
    except Exception as e:
        abort(500, str(e))
    
    return {**vendorData, '_id': str(response.inserted_id)}, 201

def updateVendor(vendorId:str, vendorInput:TypeVendorInput)->tuple[TypeVendor, int]:
    # check if vendor data exists
    try:
        vendorData = validateUniqueField('_id', ObjectId(vendorId))
    except InvalidId:
        abort(422, 'Invalid Vendor ID')
    if not vendorData:
        abort(404, 'Vendor Data Not Found')
    
    # check if vendor name already exists
    anotherVendorData = validateUniqueField('vendorName', vendorInput['vendorName'].lower(), vendorId)
    if anotherVendorData:
        abort(409, 'Vendor Name Already Exists')

    # validate required field
    vendorData = vaildateRequiredField({**vendorInput, 'setup': vendorData['setup']}) # TODO: change to user data

    # update vendor data
    try:
        vendorDataUpdated = vendorCollection.find_one_and_update({
            '_id': ObjectId(vendorId)
        }, {
            '$set': vendorData
        }, return_document=True)
    except Exception as e:
        abort(500, str(e))

    return {**vendorDataUpdated, '_id': str(vendorDataUpdated['_id'])}, 200

def removeVendor(vendorId:str)->tuple[None, int]:
    # check if vendor data exists
    try:
        vendorData = validateUniqueField('_id', ObjectId(vendorId))
    except InvalidId:
        abort(422, 'Invalid Vendor ID')
    if not vendorData:
        abort(404, 'Vendor Data Not Found')
    
    # remove vendor data
    try:
        vendorCollection.update_one({
            '_id': ObjectId(vendorId)
        }, {
            '$set': {
                'activeStatus': False,
                'setup': {
                    **vendorData['setup'],
                    'updateDate': datetime.now(UTC),
                    # TODO: change to user data
                    'updateUser': 'SYSTEM'
                }
            }
        })
    except Exception as e:
        abort(500, str(e))

    return None, 204

# helper function
def validateUniqueField(fieldToValidate:str, valueToValidate:Any, excludeId:str = None)->TypeVendor:
    query ={
        fieldToValidate : valueToValidate,
        'activeStatus': True
    }
    if excludeId:
        query['_id'] = {'$ne': ObjectId(excludeId)}

    try:
        vendorData = vendorCollection.find_one(query)
    except Exception as e:
        abort(500, str(e))

    return vendorData

def vaildateRequiredField(vendorInput:TypeVendorInput)->dict:
    try:
        validatedRequiredField = {
            'vendorName': vendorInput['vendorName'].lower(),
            'unitUsaha': vendorInput['unitUsaha'],
            'address': vendorInput['address'],
            'country': vendorInput['country'],
            'province': vendorInput['province'],
            'noTelp': vendorInput['noTelp'],
            'emailCompany': vendorInput['emailCompany'],
            'website': vendorInput['website'],
            'noNPWP': vendorInput['noNPWP'],
            'activeStatus': True,
            'branchOffice': [{
                'branchName': branchOffice['branchName'],
                'address': branchOffice['address'],
                'country': branchOffice['country'],
                'noTelp': branchOffice['noTelp'],
                'website': branchOffice['website'],
                'email': branchOffice['email']
            } for branchOffice in vendorInput.get('branchOffice', [])],
            'pic': [{
                'username': pic['username'],
                'name': pic['name'],
                'email': pic['email'],
                'noTelp': pic['noTelp']
            } for pic in vendorInput.get('pic', [])],
            'accountBank': [{
                'bankId': accountBank['bankId'],
                'bankName': accountBank['bankName'],
                'accountNumber': accountBank['accountNumber'],
                'accountName': accountBank['accountName']
            } for accountBank in vendorInput.get('accountBank', [])],
            'setup': {
                'createDate': vendorInput.get('setup', {}).get('createDate', datetime.now(UTC)),
                'updateDate': datetime.now(UTC),
                # TODO: change to user data
                'createUser': vendorInput.get('setup', {}).get('createUser', 'SYSTEM'),
                'updateUser': 'SYSTEM'
            }
        }
    except KeyError as e:
        abort(422, f'Missing required field: {str(e)}')
    except Exception as e:
        abort(500, str(e))

    return validatedRequiredField
