from datetime import UTC, datetime
import redis
from common.db import dbInstance
from common.helpers.types import TypeAuthInput, TypeUser
from pymongo.errors import WriteError
import bcrypt
from flask import abort, session

userCollection = dbInstance.db['USER']
redisConnection = redis.Redis(host='localhost', port=6379, db=0)

def userRegister(regsiterInput: TypeAuthInput):
    try:
        anotherUserData: TypeUser = userCollection.find_one({
            'username': regsiterInput['username']
        })
    except Exception as e:
        abort(500, str(e))
    if anotherUserData:
        abort(409, 'Username already exists')

    salt = bcrypt.gensalt()
    hashedPassword = bcrypt.hashpw(regsiterInput['password'].encode(), salt)
    regsiterInput['password'] = hashedPassword

    userData = {
        **regsiterInput,
        'userRole': 'inventory',
        'setup': {
            'createDate': datetime.now(UTC),
            'updateDate': datetime.now(UTC),
            'createUser': 'SYSTEM',
            'updateUser': 'SYSETM'
        }
    }

    try:
        userCollection.insert_one(userData)
    except WriteError as e:
        error_message = e.details.get('errmsg', str(e))
        abort(422, error_message)
    except Exception as e:
        abort(500, str(e))

    userData.pop('password')
    print(userData)
    return {
        'data': {**userData, '_id': str(userData['_id'])}
    }, 201

def userLogin(loginInput: TypeAuthInput):
    try:
        userData: TypeUser = userCollection.find_one({
            'username': loginInput['username'],
        })
    except Exception as e:
        abort(500, str(e))
    if not userData:
        abort(401, 'Invalid Credentials')
    
    if bcrypt.checkpw(loginInput['password'].encode(), userData['password']):
        userData.pop('password')
        userData['_id'] = str(userData['_id'])
        
        session['user'] = userData
        
        return {
            'data': userData
        }, 200
    abort(401, 'Invalid Credentials')

def userLogout():
    session.clear()



