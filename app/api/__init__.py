from flask import Blueprint
from app.api.v1.user import api_v1

api_v1 = Blueprint('api_v1', __name__)

# 注册各模块蓝本
api_v1.register_blueprint(users_bp, url_prefix='/users')
