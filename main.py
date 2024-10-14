from werkzeug.exceptions import HTTPException
from flask import Flask, jsonify
from api.v1.swagger import swaggerui_blueprint, swagger_blueprint, swagger_url
from api.v1.master_bank.routes import masterBankRoutes

app = Flask(__name__)

@app.route('/')
def index():
    return 'TA Kapita Selekta'

# ENDPOINT /v1/master-bank/
app.register_blueprint(masterBankRoutes)

# ENDPOINT /swagger
app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)
app.register_blueprint(swagger_blueprint)

@app.errorhandler(HTTPException)
def handle_exception(e:HTTPException):
    return jsonify({f'message': e.description}), e.code


if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
