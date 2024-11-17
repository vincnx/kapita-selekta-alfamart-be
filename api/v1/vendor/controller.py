from datetime import datetime, UTC
from typing import Any
from bson import ObjectId
from api.v1.master_bank.controller import findMasterBankById
from api.v1.middlewares.verifyRole import verifyRole
from common.db import dbInstance
from bson.errors import InvalidId
from common.helpers.types import TypeVendor, TypeVendorBankInput, TypeVendorBranchOfficeInput, TypeVendorInput, TypeVendorPicInput
from flask import abort, g
from pymongo.errors import WriteError

vendorCollection = dbInstance.db['VMS VENDOR']

def findAllVendor() -> tuple[dict[str, TypeVendor], int]:
    try:
        allVendorData = list(vendorCollection.find({
            'activeStatus': True
        }))
    
        return {
            'data' : [
                {**vendor, '_id': str(vendor['_id'])}
                for vendor in allVendorData
            ]
        }, 200
    except Exception as e:
        abort(500, str(e))

def findVendorById(vendorId: str) -> tuple[dict[str, TypeVendor], int]:
    try:
        vendorData = vendorCollection.find_one({
            '_id': ObjectId(vendorId),
            'activeStatus': True
        })
        if not vendorData:
            return {
                'message': 'Vendor Data Not Found'
            }, 404

        return {
            'data': {**vendorData, '_id': str(vendorData['_id'])}
        }, 200
    except InvalidId:
        abort(422, 'Invalid Vendor ID')
    except Exception as e:
        abort(500, str(e))

def insertVendor(vendorInput:TypeVendorInput)->tuple[TypeVendor, int]:
    try:
        # check if vendor name already exists
        anotherVendorData = validateUniqueField('vendorName', vendorInput['vendorName'].lower())
        if anotherVendorData:
            return {
                'message': 'Vendor Name Already Exists'
            }, 409

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
                'createUser': g.user['_id'],
                'updateUser': g.user['_id']
            }
        }

        response = vendorCollection.insert_one(vendorData)
    except WriteError as e:
        errorMessage = e.details.get('errmsg', str(e))
        abort(422, errorMessage)
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

@verifyRole(['inventory'])
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

@verifyRole(['inventory'])
def insertVendorBankAccount(vendorId:str, vendorBankAccountInput:TypeVendorBankInput)->tuple[TypeVendor, int]:
    try:
        # check if vendor data exists
        vendorData = validateUniqueField('_id', ObjectId(vendorId))
        if not vendorData:
            return {
                'message': 'Vendor Data Not Found'
            }, 404

        # validate bank data with BE
        bankData = findMasterBankById(vendorBankAccountInput['bankId'])[0]

        vendorDataUpdated = vendorCollection.find_one_and_update(
            {'_id': ObjectId(vendorId)}, 
            {
                '$push': {
                    'accountBank': {
                        **vendorBankAccountInput,
                        'bankName': bankData['name']
                    }
                },
                '$set': {
                    'setup.updateDate': datetime.now(UTC),
                    'setup.updateUser': g.user['_id']
                }
            }, 
            return_document=True
        )

        return {**vendorDataUpdated, '_id': str(vendorDataUpdated['_id'])}, 200
    
    except InvalidId:
        abort(422, 'Invalid Vendor ID')
    except WriteError as e:
        errorMessage = e.details.get('errmsg', str(e))
        abort(422, errorMessage)
    except Exception as e:
        abort(500, str(e))

@verifyRole(['inventory'])
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

@verifyRole(['inventory'])
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