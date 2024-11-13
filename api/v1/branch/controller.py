from typing import List
from flask import abort
from common.db import dbInstance
from common.helpers.types import TypeBranch

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

