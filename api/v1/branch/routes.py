from flask import Blueprint, jsonify

from api.v1.branch.controller import findAllBranch


branchRoutes = Blueprint('branchRoutes', __name__, url_prefix='/v1/branch')

@branchRoutes.route('', methods=['GET'])
def getAllBranch():
    data, status = findAllBranch()
    return jsonify(data), status
