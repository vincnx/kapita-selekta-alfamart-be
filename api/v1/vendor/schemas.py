from datetime import UTC, datetime
from marshmallow import Schema, fields, validate

class SetupSchema(Schema):
    createDate = fields.DateTime(missing=lambda: datetime.now(UTC))
    updateDate = fields.DateTime(dump_default=lambda: datetime.now(UTC))
    createUser = fields.Str(missing='SYSTEM')  # TODO: change to user data
    updateUser = fields.Str(dump_default='SYSTEM')  # TODO: change to user data

class BranchOfficeSchema(Schema):
    branchName = fields.Str(required=True)
    address = fields.Str(required=True)
    country = fields.Str(required=True)
    noTelp = fields.Str(required=True)
    website = fields.Str(required=True)
    email = fields.Email(required=True)

class PICSchema(Schema):
    username = fields.Str(required=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    noTelp = fields.Str(required=True)

class AccountBankSchema(Schema):
    bankId = fields.Str(required=True)
    bankName = fields.Str(required=True)
    accountNumber = fields.Str(required=True)
    accountName = fields.Str(required=True)

class VendorSchema(Schema):
    vendorName = fields.Str(required=True)
    unitUsaha = fields.Str(required=True)
    address = fields.Str(required=True)
    country = fields.Str(required=True)
    province = fields.Str(required=True)
    noTelp = fields.Str(required=True)
    emailCompany = fields.Email(required=True)
    website = fields.Str(required=True)
    noNPWP = fields.Str(required=True)
    activeStatus = fields.Boolean(dump_default=True)
    branchOffice = fields.List(fields.Nested(BranchOfficeSchema()), missing=[])
    pic = fields.List(fields.Nested(PICSchema()), missing=[])
    accountBank = fields.List(fields.Nested(AccountBankSchema()), missing=[])
    setup = fields.Nested(SetupSchema())

class VendorDetailInputSchema(Schema):
    vendorName = fields.Str(required=True, validate=[validate.Length(min=1)])
    unitUsaha = fields.Str(required=True, validate=[validate.Length(min=1)])
    address = fields.Str(required=True, validate=[validate.Length(min=1)])
    country = fields.Str(required=True, validate=[validate.Length(min=1)])
    province = fields.Str(required=True, validate=[validate.Length(min=1)])
    noTelp = fields.Str(required=True, validate=[validate.Length(min=1)])
    emailCompany = fields.Email(required=True)
    website = fields.Str(required=True, validate=[validate.Length(min=1)])
    noNPWP = fields.Str(required=True, validate=[validate.Length(min=1)])
    activeStatus = fields.Boolean(dump_default=True)
