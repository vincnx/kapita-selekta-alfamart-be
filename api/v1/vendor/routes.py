from flask import Blueprint, jsonify, request

from api.v1.vendor.controller import findAllVendor, findVendorById, insertVendor, removeVendor, updateVendorDetail

vendorRoutes = Blueprint('vendorRoutes', __name__, url_prefix='/v1/vendor')

@vendorRoutes.route('', methods=['GET'])
def getAllVendor():
    data, status = findAllVendor()
    return jsonify(data), status

@vendorRoutes.route('/<string:vendorId>', methods=['GET'])
def getVendorById(vendorId:str):
    data, status = findVendorById(vendorId)
    return jsonify(data), status

@vendorRoutes.route('', methods=['POST'])
def createVendor():
    data, status = insertVendor(request.json)
    return jsonify(data), status

@vendorRoutes.route('/<string:vendorId>/detail', methods=['PUT'])
def editVendor(vendorId:str):
    data, status = updateVendorDetail(vendorId, request.json)
    return jsonify(data), status

@vendorRoutes.route('/<string:vendorId>', methods=['DELETE'])
def deleteVendor(vendorId:str):
    data, status = removeVendor(vendorId)
    return jsonify(data), status