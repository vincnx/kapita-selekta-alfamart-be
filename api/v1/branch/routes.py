from flask import Blueprint, jsonify, request

from api.v1.branch.controller import findAllBranch, findAllBranchProductByUser, findBranchById, findBranchByUser, findBranchProductByIdAndUser, insertBranchProductByUser, updateBranchProductByIdAndUser


branchRoutes = Blueprint('branchRoutes', __name__, url_prefix='/v1/branch')

@branchRoutes.route('', methods=['GET'])
def getAllBranch():
    data, status = findAllBranch()
    return jsonify(data), status

@branchRoutes.route('/<string:branchId>', methods=['GET'])
def getBranchById(branchId: str):
    data, status = findBranchById(branchId)
    return jsonify(data), status

@branchRoutes.route('/user', methods=['GET'])
def getBranchByUser():
    data, status = findBranchByUser()
    return jsonify(data), status

@branchRoutes.route('/user/product', methods=['GET'])
def getAllBranchProductByUser():
    data, status = findAllBranchProductByUser()
    return jsonify(data), status

@branchRoutes.route('/user/product', methods=['POST'])
def createBranchProductByUser():
    data, status = insertBranchProductByUser(request.json)
    return jsonify(data), status

@branchRoutes.route('/user/product/<string:productId>', methods=['GET'])
def getBranchProductByIdAndUser(productId: str):
    data, status = findBranchProductByIdAndUser(productId)
    return jsonify(data), status

@branchRoutes.route('/user/product/<string:productId>', methods=['PUT'])
def editBranchProductByIdAndUser(productId: str):
    data, status = updateBranchProductByIdAndUser(productId, request.json)
    return jsonify(data), status