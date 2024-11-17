from datetime import UTC, datetime
from api.v1.branch.controller import findBranchById
from common.helpers.types import TypeUserInput
from common.db import dbInstance
import bcrypt
from flask import abort, g
from werkzeug.exceptions import HTTPException
from pymongo.errors import WriteError

userCollection = dbInstance.db['USER']
def insertUser(userInput: TypeUserInput):
    try:
        # check if username already exists
        anotherUserData = userCollection.find_one({
            'username': userInput['username']
        })
        if anotherUserData:
            abort(409, 'Username already exists')

        salt = bcrypt.gensalt()
        hashedPassword = bcrypt.hashpw(userInput['password'].encode(), salt)
        userInput['password'] = hashedPassword

        userData = {
            **userInput,
            'setup': {
                'createDate': datetime.now(UTC),
                'updateDate': datetime.now(UTC),
                'createUser': g.user['_id'],
                'updateUser': g.user['_id']
            }
        }

        # if user role is branch, get branch data and add to user data
        if userInput['userRole'] == 'branch':
            branchData = findBranchById(userInput['branchId'])[0]['data']
            userData['branch'] = {
                'branchName': branchData['branchName'],
                'branchId': branchData['_id']
            }

        response = userCollection.insert_one(userData)
        userData.pop('password')

        return {
            'data': {**userData, '_id': str(response.inserted_id)}
        }, 201
    except WriteError as e:
        error_message = e.details.get('errmsg', str(e))
        abort(422, error_message)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))