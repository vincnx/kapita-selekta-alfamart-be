import redis
from config import Config
from werkzeug.exceptions import HTTPException
from flask import Flask, abort, g, jsonify, request, session
from flask_cors import CORS
from api.v1.swagger import swaggerui_blueprint, swagger_blueprint, swagger_url
from api.v1.auth.routes import authRoutes
from api.v1.master_bank.routes import masterBankRoutes
from api.v1.vendor.routes import vendorRoutes
from api.v1.product.routes import productRoutes
from api.v1.request.routes import requestRoutes
from api.v1.branch.routes import branchRoutes
from api.v1.user.routes import userRoutes
from flask_session import Session
from common.db import dbInstance

app = Flask(__name__)

app.config.from_object(Config)

try:
    redis_client = redis.from_url(Config.SESSION_REDIS)
    redis_client.ping()
    app.config['SESSION_REDIS'] = redis_client
    server_session = Session(app)
except (redis.ConnectionError, redis.RedisError) as e:
    print(f'Warning: Redis connection failed - {str(e)}')

CORS(app, supports_credentials=True)

@app.route('/')
def index():
    mongo_status = 'Connected'
    try:
        dbInstance.client.admin.command('ping')
    except Exception as e:
        mongo_status = f'Error: {str(e)}'

    redis_status = 'Connected'
    try:
        app.config['SESSION_REDIS'].ping()
    except Exception as e:
        redis_status = f'Error: Redis is not connected'
    
    return jsonify({
        'message': 'TA Kapita Selekta',
        'mongodb_status': mongo_status,
        'redis_status': redis_status
    })

@app.before_request
def verifySession():
    if request.method == 'OPTIONS':
        return

    if request.endpoint and (
        request.endpoint.startswith('swagger') or 
        request.endpoint == 'index' or
        request.endpoint.startswith('auth')
    ):
        return

    userData = session.get('user')
    if not userData:
        abort(401, 'Unauthorized')

    g.user = userData

# ENDPOINT /v1/auth/
app.register_blueprint(authRoutes)

# ENDPOINT /v1/master-bank/
app.register_blueprint(masterBankRoutes)

# ENDPOINT /v1/vendor/
app.register_blueprint(vendorRoutes)

# ENDPOINT /v1/product/
app.register_blueprint(productRoutes)

# ENDPOINT /v1/request/
app.register_blueprint(requestRoutes)

# ENDPOINT /v1/branch/
app.register_blueprint(branchRoutes)

# ENDPOINT /v1/user/
app.register_blueprint(userRoutes)

# ENDPOINT /swagger
app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)
app.register_blueprint(swagger_blueprint)

@app.errorhandler(HTTPException)
def handle_exception(e:HTTPException):
    return jsonify({f'message': e.description}), e.code

if __name__ == '__main__':
    app.run(debug=True, port=8080)
