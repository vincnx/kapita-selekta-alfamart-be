from flask import Blueprint, jsonify, request
from api.v1.master_bank.controller import findAllMasterBank, findMasterBankById, insertMasterBank, removeMasterBank, updateMasterBank

masterBankRoutes = Blueprint('masterBankRoutes', __name__, url_prefix='/v1/master-bank')

@masterBankRoutes.route('/', methods=['GET'])
def getAllMasterBank():
    data, status = findAllMasterBank()
    return jsonify(data), status

@masterBankRoutes.route('/<string:masterBankId>', methods=['GET'])
def getMasterBankById(masterBankId:str):
    data, status = findMasterBankById(masterBankId)
    return jsonify(data), status

@masterBankRoutes.route('/', methods=['POST'])
def createMasterBank():
    masterBankData = request.json
    data, status = insertMasterBank(masterBankData)
    return jsonify(data), status

@masterBankRoutes.route('/<string:masterBankId>', methods=['PUT'])
def editMasterBank(masterBankId:str):
    masterBankData = request.json
    data, status = updateMasterBank(masterBankId, masterBankData)
    return jsonify(data), status

@masterBankRoutes.route('/<string:masterBankId>', methods=['DELETE'])
def deleteMasterBank(masterBankId:str):
    data, status = removeMasterBank(masterBankId)
    return jsonify(data), status