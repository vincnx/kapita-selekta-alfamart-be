from werkzeug.exceptions import HTTPException
from flask import Flask, jsonify
from flask_cors import CORS
from api.v1.swagger import swaggerui_blueprint, swagger_blueprint, swagger_url
from api.v1.master_bank.routes import masterBankRoutes
from api.v1.vendor.routes import vendorRoutes
from api.v1.product.routes import productRoutes

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return 'TA Kapita Selekta'

# ENDPOINT /v1/master-bank/
app.register_blueprint(masterBankRoutes)

# ENDPOINT /v1/vendor/
app.register_blueprint(vendorRoutes)

# ENDPOINT /v1/product/
app.register_blueprint(productRoutes)

# ENDPOINT /swagger
app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)
app.register_blueprint(swagger_blueprint)

@app.errorhandler(HTTPException)
def handle_exception(e:HTTPException):
    return jsonify({f'message': e.description}), e.code

if __name__ == '__main__':
    app.run(debug=True, port=8080)
