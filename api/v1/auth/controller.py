from common.db import dbInstance
from common.helpers.types import TypeAuthInput, TypeUser
import bcrypt
from flask import abort, session
from werkzeug.exceptions import HTTPException

userCollection = dbInstance.db['USER']

def userLoggedIn():
    userData = session.get('user')
    if not userData:
        abort(401, 'Unauthorized')
    return {
        'data': userData
    }, 200

def userLogin(loginInput: TypeAuthInput):
    try:
        userData: TypeUser = userCollection.find_one({
            'username': loginInput['username'],
        })
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
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        abort(500, str(e))

def userLogout():
    session.clear()
    return None, 204



