from flask import Blueprint, jsonify, request

from api.v1.request.controller import acceptRequest, findAllRequest, findRequestById, insertRequest


requestRoutes = Blueprint('requestRoutes', __name__, url_prefix='/v1/request')

@requestRoutes.route('', methods=['GET'])
def getAllRequest():
    data, status = findAllRequest()
    return jsonify(data), status

@requestRoutes.route('/<string:requestId>', methods=['GET'])
def getRequestById(requestId: str):
    data, status = findRequestById(requestId)
    return jsonify(data), status

@requestRoutes.route('', methods=['POST'])
def createRequest():
    data, status = insertRequest(request.json)
    return jsonify(data), status

@requestRoutes.route('/<string:requestId>/accept', methods=['POST'])
def acceptBranchRequest(requestId: str):
    data, status = acceptRequest(requestId)
    return jsonify(data), status