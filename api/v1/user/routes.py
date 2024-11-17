from flask import Blueprint, jsonify, request
from api.v1.user.controller import insertUser

userRoutes = Blueprint('userRoutes', __name__, url_prefix='/v1/user')

@userRoutes.route('', methods=['POST'])
def createUser():
    data, status = insertUser(request.json)
    return jsonify(data), status