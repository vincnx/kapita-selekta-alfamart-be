from datetime import datetime, UTC
from bson import ObjectId
from pymongo.errors import WriteError
from common.db import dbInstance
from common.helpers.types import TypeMasterBank, TypeMasterBankInput
from flask import abort

masterBankCollection = dbInstance.db['VMS BANK']

def findAllMasterBank()->tuple[list[TypeMasterBank], int]:
    # get all master bank data
    try:
        allMasterBankData = list(masterBankCollection.find({'activeStatus': True}))
    except Exception as e:
        abort(500, str(e))
    
    return [
        {**masterBank, '_id': str(masterBank['_id'])}
        for masterBank in allMasterBankData
    ], 200

def findMasterBankById(masterBankId:str)->tuple[TypeMasterBank, int]:
    # check if master bank data exists
    print(masterBankId)
    try:
        masterBankData = masterBankCollection.find_one({
            '_id': ObjectId(masterBankId),
            'activeStatus': True
        })
    except Exception as e:
        abort(500, str(e))
    if not masterBankData:
        abort(404, 'Master Bank Data not Found')
    
    return {**masterBankData, '_id': str(masterBankData['_id'])}, 200

def insertMasterBank(masterBankInput:TypeMasterBankInput)->tuple[TypeMasterBank, int]:
    masterBankData = {
        'name': masterBankInput['name'],
        'bankDesc': masterBankInput['bankDesc'].lower(),
        'activeStatus': True,
        'setup': {
            'createDate': datetime.now(UTC),
            'updateDate': datetime.now(UTC),
            # TODO: change to user data
            'createUser': 'SYSTEM',
            'updateUser': 'SYSTEM'
        }
    }

    # insert master bank data
    try:
        response = masterBankCollection.insert_one(masterBankData)
    except WriteError as e:
        error_message = e.details.get('errmsg', str(e))
        abort(422, error_message)
    except Exception as e:
        abort(500, str(e))

    return {**masterBankData, '_id':str(response.inserted_id)}, 201

def updateMasterBank(masterBankId:str, masterBankInput:TypeMasterBankInput)->tuple[TypeMasterBank, int]:
    # check if master bank data exists
    try:
        masterBankData = masterBankCollection.find_one({
            '_id': ObjectId(masterBankId),
            'activeStatus': True
        })
    except Exception as e:
        abort(500, str(e))
    if not masterBankData:
        abort(404, 'Master Bank Data not Found')

    # prepare data to update
    masterBankData = {
        **masterBankData,
        'name': masterBankInput['name'],
        'bankDesc': masterBankInput['bankDesc'].lower(),
        'setup': {
            **masterBankData['setup'],
            'updateDate': datetime.now(UTC),
            # TODO: change to user data
            'updateUser': 'SYSTEM'
        }
    }

    # update master bank data
    try:
        masterBankDataUpdated = masterBankCollection.find_one_and_update({
            '_id': ObjectId(masterBankId)
        }, {
            '$set': masterBankData
        }, return_document=True)
    except Exception as e:
        abort(500, str(e))

    return {**masterBankDataUpdated, '_id': str(masterBankDataUpdated['_id'])}, 200

def removeMasterBank(masterBankId:str)->tuple[None, int]:
    # check if master bank data exists
    try:
        masterBankData = masterBankCollection.find_one({
            '_id': ObjectId(masterBankId),
            'activeStatus': True
        })
    except Exception as e:
        abort(500, str(e))
    if not masterBankData:
        abort(404, 'Master Bank Data not Found')

    # update master bank data
    try:
        masterBankCollection.update_one({
            '_id': ObjectId(masterBankId)
        }, {
            '$set': {
                'activeStatus': False,
                'setup': {
                    **masterBankData['setup'],
                    'updateDate': datetime.now(UTC),
                    # TODO: change to user data
                    'updateUser': 'SYSTEM'
                }
            }
        })
    except Exception as e:
        abort(500, str(e))

    return None, 204