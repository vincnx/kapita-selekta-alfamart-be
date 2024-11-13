from flask import Blueprint, jsonify

from api.v1.branch.controller import findAllBranch, findBranchById, findBranchByUser


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