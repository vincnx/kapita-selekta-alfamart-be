from flask import Blueprint, jsonify, request

from api.v1.vendor.controller import findAllVendor, findVendorById, insertVendor, insertVendorBankAccount, insertVendorBranchOffice, insertVendorPic, removeVendor, updateVendorDetail

vendorRoutes = Blueprint('vendorRoutes', __name__, url_prefix='/v1/vendor')

@vendorRoutes.route('', methods=['GET'])
def getAllVendor():
    params = request.args
    data, status = findAllVendor(params)
    return jsonify(data), status

@vendorRoutes.route('/<string:vendorId>', methods=['GET'])
def getVendorById(vendorId:str):
    data, status = findVendorById(vendorId)
    return jsonify(data), status

@vendorRoutes.route('', methods=['POST'])
def createVendor():
    data, status = insertVendor(request.json)
    return jsonify(data), status

@vendorRoutes.route('/<string:vendorId>/branch-office', methods=['POST'])
def createVendorBranchOffice(vendorId:str):
    data, status = insertVendorBranchOffice(vendorId, request.json)
    return jsonify(data), status

@vendorRoutes.route('/<string:vendorId>/pic', methods=['POST'])
def createVendorPic(vendorId:str):
    data, status = insertVendorPic(vendorId, request.json)
    return jsonify(data), status

@vendorRoutes.route('/<string:vendorId>/bank-account', methods=['POST'])
def createVendorBankAccount(vendorId:str):
    data, status = insertVendorBankAccount(vendorId, request.json)
    return jsonify(data), status

@vendorRoutes.route('/<string:vendorId>/detail', methods=['PUT'])
def editVendor(vendorId:str):
    data, status = updateVendorDetail(vendorId, request.json)
    return jsonify(data), status

@vendorRoutes.route('/<string:vendorId>', methods=['DELETE'])
def deleteVendor(vendorId:str):
    data, status = removeVendor(vendorId)
    return jsonify(data), status