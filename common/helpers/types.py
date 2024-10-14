from typing import TypedDict
from datetime import datetime

TypeSetup = TypedDict('TypeSetup', {
    'createDate': datetime,
    'createUser': str,
    'updateDate': datetime,
    'updateUser': str
})

TypeMasterBank = TypedDict('TypeMasterBank', {
    '_id': str,
    'activeStatus': bool,
    'name': str,
    'bankDesc': str,
    'setup': TypeSetup
})

TypeMasterBankInput = TypedDict('TypeMasterBankInput', {
    'name': str,
    'bankDesc': str
})