from datetime import datetime, UTC
from bson import ObjectId
from pymongo.errors import WriteError
from common.db import dbInstance
from common.helpers.types import TypeMasterBank, TypeMasterBankInput
from flask import abort, g
from bson.errors import InvalidId
from werkzeug.exceptions import HTTPException

masterBankCollection = dbInstance.db['VMS BANK']

def findAllMasterBank() -> tuple[list[TypeMasterBank], int]:
    try:
        allMasterBankData = list(masterBankCollection.find({'activeStatus': True}))
        
        return {
            'data': [
                {**masterBank, '_id': str(masterBank['_id'])}
                for masterBank in allMasterBankData
            ]
        }, 200
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

def findMasterBankById(masterBankId:str) -> tuple[TypeMasterBank, int]:
    try:
        masterBankData = masterBankCollection.find_one({
            '_id': ObjectId(masterBankId),
            'activeStatus': True
        })
        if not masterBankData:
            abort(404, 'Master Bank Data not Found')

        return {**masterBankData, '_id': str(masterBankData['_id'])}, 200
    except InvalidId:
        abort(422, 'Invalid Master Bank Id')
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

def insertMasterBank(masterBankInput:TypeMasterBankInput) -> tuple[TypeMasterBank, int]:
    try:
        masterBankData = {
            'name': masterBankInput['name'],
            'bankDesc': masterBankInput['bankDesc'].lower(),
            'activeStatus': True,
            'setup': {
                'createDate': datetime.now(UTC),
                'updateDate': datetime.now(UTC),
                'createUser': g.user['_id'],
                'updateUser': g.user['_id']
            }
        }

        response = masterBankCollection.insert_one(masterBankData)

        return {**masterBankData, '_id':str(response.inserted_id)}, 201
    except WriteError as e:
        errorMessage = e.details.get('errmsg', str(e))
        abort(422, errorMessage)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

def updateMasterBank(masterBankId:str, masterBankInput:TypeMasterBankInput) -> tuple[TypeMasterBank, int]:
    try:
        # check if master bank data exists
        findMasterBankById(masterBankId)

        masterBankDataUpdated = masterBankCollection.find_one_and_update(
            {'_id': ObjectId(masterBankId)}, 
            {
                '$set': {
                    'name': masterBankInput['name'],
                    'bankDesc': masterBankInput['bankDesc'].lower(),
                    'setup.updateDate': datetime.now(UTC),
                    'setup.updateUser': g.user['_id']
                }
            }, 
            return_document=True
        )

        return {**masterBankDataUpdated, '_id': str(masterBankDataUpdated['_id'])}, 200
    except WriteError as e:
        errorMessage = e.details.get('errmsg', str(e))
        abort(422, errorMessage)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

def removeMasterBank(masterBankId:str) -> tuple[None, int]:
    try:
        # check if master bank data exists
        findMasterBankById(masterBankId)

        masterBankCollection.update_one(
            {'_id': ObjectId(masterBankId)}, 
            {
                '$set': {
                    'activeStatus': False,
                    'setup.updateDate': datetime.now(UTC),
                    'setup.updateUser': g.user['_id']
                }
            }
        )

        return None, 204
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))