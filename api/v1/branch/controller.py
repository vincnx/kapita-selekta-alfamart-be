from typing import List
from bson import ObjectId
from flask import abort
from common.db import dbInstance
from common.helpers.types import TypeBranch
from bson.errors import InvalidId

branchCollection = dbInstance.db['VMS BRANCH']

def findAllBranch() -> tuple[dict[str, List[TypeBranch]], int]:
    try:
        allBranchData = list(branchCollection.find())
    except Exception as e:
        abort(500, str(e))

    return {
        'data': [
            {**branch, '_id': str(branch['_id'])}
            for branch in allBranchData
        ]
    }, 200

def findBranchById(branchId: str) -> tuple[dict[str, TypeBranch], int]:
    try:
        branchData = branchCollection.find_one({
            '_id': ObjectId(branchId),
        })
    except InvalidId:
        abort(422, 'Invalid Branch ID')
    except Exception as e:
        abort(500, str(e))
    if not branchData:
        abort(404, 'Branch Data Not Found')

    return {
        'data': {**branchData, '_id': str(branchData['_id'])}
    }, 200