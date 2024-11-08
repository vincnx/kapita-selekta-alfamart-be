from datetime import datetime, UTC
from typing import Any
from bson import ObjectId
from api.v1.master_bank.controller import findMasterBankById
from common.db import dbInstance
from bson.errors import InvalidId
from common.helpers.types import TypeVendor, TypeVendorBankInput, TypeVendorBranchOfficeInput, TypeVendorInput, TypeVendorPicInput
from flask import abort
from pymongo.errors import WriteError

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
    
    return {
        'data' : [
            {**vendor, '_id': str(vendor['_id'])}
            for vendor in allVendorData
        ]
    }, 200

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

    return {
        'data': {**vendorData, '_id': str(vendorData['_id'])}
    }, 200

def insertVendor(vendorInput:TypeVendorInput)->tuple[TypeVendor, int]:
    # check if vendor name already exists
    anotherVendorData = validateUniqueField('vendorName', vendorInput['vendorName'].lower())
    if anotherVendorData:
        abort(409, 'Vendor Name Already Exists')

    vendorData = {
        **vendorInput,
        'accountBank': [],
        'activeStatus': [],
        'branchOffice': [],
        'pic': [],
        'activeStatus': True,
        'setup': {
            'createDate' : datetime.now(UTC),
            'updateDate': datetime.now(UTC),
            # TODO: change to user data
            'createUser': 'SYSTEM',
            'updateUser': 'SYSTEM'
        }
    }

    # insert vendor data
    try:
        response = vendorCollection.insert_one(vendorData)
    except WriteError as e:
        error_message = e.details.get('errmsg', str(e))
        abort(422, error_message)
    except Exception as e:
        abort(500, str(e))
    
    return {**vendorData, '_id': str(response.inserted_id)}, 201

def insertVendorBranchOffice(vendorId:str, vendorBranchOfficeInput:TypeVendorBranchOfficeInput)->tuple[TypeVendor, int]:
    # check if vendor data exists
    try:
        vendorData = validateUniqueField('_id', ObjectId(vendorId))
    except InvalidId:
        abort(422, 'Invalid Vendor ID')
    if not vendorData:
        abort(404, 'Vendor Data Not Found')

    vendorData = {
        **vendorData,
        'setup': {
            **vendorData['setup'],
            'updateDate': datetime.now(UTC),
            # TODO: change to user data
            'updateUser': 'SYSTEM'
        },
        'branchOffice': vendorData['branchOffice'] + [vendorBranchOfficeInput]
    }

    # update vendor data
    try:
        vendorDataUpdated = vendorCollection.find_one_and_update({
            '_id': ObjectId(vendorId)
        }, {
            '$set': vendorData
        }, return_document=True)
    except WriteError as e:
        errorMessage = e.details.get('errmsg', str(e))
        abort(422, errorMessage)
    except Exception as e:
        abort(500, str(e))

    return {**vendorDataUpdated, '_id': str(vendorDataUpdated['_id'])}, 200

def insertVendorPic(vendorId:str, vendorPicInput:TypeVendorPicInput):
    # check if vendor data exists
    try:
        vendorData = validateUniqueField('_id', ObjectId(vendorId))
    except InvalidId:
        abort(422, 'Invalid Vendor ID')
    if not vendorData:
        abort(404, 'Vendor Data Not Found')

    vendorData = {
        **vendorData,
        'setup': {
            **vendorData['setup'],
            'updateDate': datetime.now(UTC),
            # TODO: change to user data
            'updateUser': 'SYSTEM'
        },
        'pic': vendorData['pic'] + [vendorPicInput]
    }

    # update vendor data
    try:
        vendorDataUpdated = vendorCollection.find_one_and_update({
            '_id': ObjectId(vendorId)
        }, {
            '$set': vendorData
        }, return_document=True)
    except WriteError as e:
        errorMessage = e.details.get('errmsg', str(e))
        abort(422, errorMessage)
    except Exception as e:
        abort(500, str(e))

    return {**vendorDataUpdated, '_id': str(vendorDataUpdated['_id'])}, 200

def insertVendorBankAccount(vendorId:str, vendorBankAccountInput:TypeVendorBankInput)->tuple[TypeVendor, int]:
    # check if vendor data exists
    try:
        vendorData = validateUniqueField('_id', ObjectId(vendorId))
    except InvalidId:
        abort(422, 'Invalid Vendor ID')
    if not vendorData:
        abort(404, 'Vendor Data Not Found')

    # get bank data
    bankData = findMasterBankById(vendorBankAccountInput['bankId'])[0]

    vendorData = {
        **vendorData,
        'setup': {
            **vendorData['setup'],
            'updateDate': datetime.now(UTC),
            # TODO: change to user data
            'updateUser': 'SYSTEM'
        },
        'accountBank': vendorData['accountBank'] + [{
            **vendorBankAccountInput,
            'bankName': bankData['name']
        }]
    }

    # update vendor data
    try:
        vendorDataUpdated = vendorCollection.find_one_and_update({
            '_id': ObjectId(vendorId)
        }, {
            '$set': vendorData
        }, return_document=True)
    except WriteError as e:
        errorMessage = e.details.get('errmsg', str(e))
        abort(422, errorMessage)
    except Exception as e:
        abort(500, str(e))

    return {**vendorDataUpdated, '_id': str(vendorDataUpdated['_id'])}, 200

def updateVendorDetail(vendorId:str, vendorInput:TypeVendorInput)->tuple[TypeVendor, int]:
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

    vendorData = {
        **vendorInput,
        'branchOffice': vendorData['branchOffice'],
        'pic': vendorData['pic'],
        'accountBank': vendorData['accountBank'],
        'setup': {
            **vendorData['setup'],
            'updateDate': datetime.now(UTC),
            # TODO: change to user data
            'updateUser': 'SYSTEM'
        }
    }

    # update vendor data
    try:
        vendorDataUpdated = vendorCollection.find_one_and_update({
            '_id': ObjectId(vendorId)
        }, {
            '$set': vendorData
        }, return_document=True)
    except WriteError as e:
        error_message = e.details.get('errmsg', str(e))
        abort(422, error_message)
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