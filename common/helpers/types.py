from typing import TypedDict, List
from datetime import datetime
from bson import ObjectId

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

TypeBranchOffice = TypedDict('TypeBranchOffice', {
    'branchName': str,
    'address': str,
    'country': str,
    'noTelp': str,
    'website': str,
    'email': str
})

TypePIC = TypedDict('TypePIC', {
    'username': str,
    'name': str,
    'email': str,
    'noTelp': str
})

TypeAccountBank = TypedDict('TypeAccountBank', {
    'bankId': str,
    'bankName': str,
    'accountNumber': str,
    'accountName': str
})

TypeVendor = TypedDict('TypeVendor', {
    '_id': ObjectId,
    'vendorName': str,
    'unitUsaha': str,
    'address': str,
    'country': str,
    'province': str,
    'noTelp': str,
    'emailCompany': str,
    'website': str,
    'noNPWP': str,
    'activeStatus': str,
    'branchOffice': List[TypeBranchOffice],
    'pic': List[TypePIC],
    'accountBank': List[TypeAccountBank],
    'setup': TypeSetup
})

TypeVendorInput = TypedDict('TypeVendorInput', {
    'vendorName': str,
    'unitUsaha': str,
    'address': str,
    'country': str,
    'province': str,
    'noTelp': str,
    'emailCompany': str,
    'website': str,
    'noNPWP': str,
    'branchOffice': List[TypeBranchOffice],
    'pic': List[TypePIC],
    'accountBank': List[TypeAccountBank]
})