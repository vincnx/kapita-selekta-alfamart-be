from typing import Literal, TypedDict, List
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

TypeVendorBranchOfficeInput = TypedDict('TypeVendorBranchOfficeInput', {
    'branchName': str,
    'address': str,
    'country': str,
    'noTelp': str,
    'website': str,
    'email': str
})

TypeVendorPicInput = TypedDict('TypeVendorPicInput', {
    'name': str,
    'email': str,
    'noTelp': str
})

TypeVendorBankInput = TypedDict('TypeVendorBankInput', {
    'bankId': str,
    'accountName': str,
    'accountNumber': str,
})

TypeProductVendor = TypedDict('TypeProductVendor', {
    'vendorId': ObjectId,
    'vendorName': str
})

TypeProduct = TypedDict('TypeProduct', {
    '_id': ObjectId,
    'name': str,
    'count': int,
    'merk': str,
    'condition': str,
    'vendor': TypeProductVendor,
    'setup': TypeSetup
})

TypeProductInput = TypedDict('TypeProductInput', {
    'name': str,
    'count': int,
    'merk': str,
    'condition': str,
    'vendorId': str
})

TypeUser = TypedDict('TypeUser', {
    '_id': ObjectId,
    'username': str,
    'password': str,
    'userRole': Literal['inventory', 'branch'],
    'setup': TypeSetup
})

TypeAuthInput = TypedDict('TypeLoginInput', {
    'username': str,
    'password': str,
})

TypeRequestProduct = TypedDict('TypeRequestProduct', {
    'productId': str,
    'name': str,
    'quantity': int
})

TypeRequest = TypedDict('TypeRequest', {
    '_id': ObjectId,
    'status': Literal['on request', 'accepted', 'draft'],
    'product': List[TypeRequestProduct],
    'totalProduct': int,
    'setup': TypeSetup,
})

TypeRequestInput = TypedDict('TypeRequestInput', {
    'product': List[TypeRequestProduct],
})