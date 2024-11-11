from flask import Blueprint, jsonify, request
from api.v1.auth.controller import userLoggedIn, userLogin, userLogout, userRegister

authRoutes = Blueprint('authRoutes', __name__, url_prefix='/v1/auth')

@authRoutes.route('/user', methods=['GET'])
def getUserLoggedIn():
    data, status = userLoggedIn()
    return jsonify(data), status

@authRoutes.route('/register', methods=['POST'])
def register():
    data, status = userRegister(request.json)
    return jsonify(data), status

@authRoutes.route('/login', methods=['POST'])
def login():
    data, status = userLogin(request.json)
    return jsonify(data), status

@authRoutes.route('/logout', methods=['POST'])
def logout():
    data, status = userLogout()
    return jsonify(data), status