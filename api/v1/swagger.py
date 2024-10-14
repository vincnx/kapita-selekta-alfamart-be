from flask import Blueprint, send_file
from flask_swagger_ui import get_swaggerui_blueprint

swagger_url = '/swagger'
api_url = '/api/v1/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    swagger_url,
    api_url,
    config={
        'app_name': "TA Kapita Selekta Swagger",
    }
)

swagger_blueprint = Blueprint('swagger', __name__)

@swagger_blueprint.route('/api/v1/swagger.json')
def swagger_json():
    return send_file('api/v1/swagger.json')
