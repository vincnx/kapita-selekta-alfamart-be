from datetime import datetime, UTC
from pymongo.errors import DuplicateKeyError
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
    try:
        masterBankData = masterBankCollection.find_one({
            '_id': masterBankId,
            'activeStatus': True
        })
    except Exception as e:
        abort(500, str(e))
    if not masterBankData:
        abort(404, 'Master Bank Data not Found')
    
    return {**masterBankData, '_id': str(masterBankData['_id'])}, 200

def insertMasterBank(masterBankInput:TypeMasterBankInput)->tuple[TypeMasterBank, int]:
    # validate required field
    try: 
        masterBankData = {
            '_id': masterBankInput['name'].lower(),
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
    except KeyError as e:
        abort(422, f'Missing required field: {str(e)}')
    except Exception as e:
        abort(500, str(e))

    # insert master bank data
    try:
        masterBankCollection.insert_one(masterBankData)
    except DuplicateKeyError as e:
        abort(409, str(e))
    except Exception as e:
        abort(500, str(e))

    return masterBankData, 201

def updateMasterBank(masterBankId:str, masterBankInput:TypeMasterBankInput)->tuple[TypeMasterBank, int]:
    # check if master bank data exists
    try:
        masterBankData = masterBankCollection.find_one({
            '_id': masterBankId,
            'activeStatus': True
        })
    except Exception as e:
        abort(500, str(e))
    if not masterBankData:
        abort(404, 'Master Bank Data not Found')

    # prepare data to update
    try:
        masterBankDataUpdated = {
            **masterBankData,
            '_id': masterBankId,
            'name': masterBankInput['name'],
            'bankDesc': masterBankInput['bankDesc'].lower(),
            'setup': {
                **masterBankData['setup'],
                'updateDate': datetime.now(UTC),
                # TODO: change to user data
                'updateUser': 'SYSTEM'
            }
        }
    except KeyError as e:
        abort(422, f'Missing required field: {str(e)}')
    except Exception as e:
        abort(500, str(e))

    # update master bank data
    try:
        masterBankCollection.update_one({
            '_id': masterBankId
        }, {
            '$set': masterBankDataUpdated
        })
    except Exception as e:
        abort(500, str(e))

    return masterBankDataUpdated, 200

def removeMasterBank(masterBankId:str)->tuple[None, int]:
    # check if master bank data exists
    try:
        masterBankData = masterBankCollection.find_one({
            '_id': masterBankId,
            'activeStatus': True
        })
    except Exception as e:
        abort(500, str(e))
    if not masterBankData:
        abort(404, 'Master Bank Data not Found')

    # update master bank data
    try:
        masterBankCollection.update_one({
            '_id': masterBankId
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