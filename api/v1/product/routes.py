from flask import Flask, Blueprint, jsonify, request

from api.v1.product.controller import findAllProduct, findProductById, insertProduct, removeProduct, updateProduct

productRoutes = Blueprint('ProductRoutes', __name__, url_prefix='/v1/product')

@productRoutes.route('/', methods=['GET'])
def getAllProduct():
    data, status = findAllProduct()
    return jsonify(data), status

@productRoutes.route('/<productId>', methods=['GET'])
def getProductById(productId:str):
    data, status = findProductById(productId)
    return jsonify(data), status

@productRoutes.route('/', methods=['POST'])
def createProduct():
    data, status = insertProduct(request.json)
    return jsonify(data), status

@productRoutes.route('/<productId>', methods=['PUT'])
def editProduct(productId:str):
    data, status = updateProduct(productId, request.json)
    return jsonify(data), status

@productRoutes.route('/<string:productId>', methods=['DELETE'])
def deleteProduct(productId:str):
    data, status = removeProduct(productId)
    return jsonify(data), status