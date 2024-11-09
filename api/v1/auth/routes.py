from flask import Blueprint, jsonify, request
from api.v1.auth.controller import userLogin, userRegister

authRoutes = Blueprint('authRoutes', __name__, url_prefix='/v1/auth')

@authRoutes.route('/register', methods=['POST'])
def register():
    data, status = userRegister(request.json)
    return jsonify(data), status

@authRoutes.route('/login', methods=['POST'])
def login():
    data, status = userLogin(request.json)
    return jsonify(data), status