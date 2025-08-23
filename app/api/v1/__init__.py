from flask import Blueprint
from app.api.v1.auth import auth_bp
from app.api.v1.user import user_bp
from app.api.v1.admin import admin_bp
from app.api.v1.teacher import teacher_bp
from app.api.v1.ai import ai_bp

api_v1 = Blueprint('api_v1', __name__)

# 注册各模块蓝本
api_v1.register_blueprint(auth_bp, url_prefix='/auth')
api_v1.register_blueprint(user_bp)
api_v1.register_blueprint(admin_bp)
api_v1.register_blueprint(teacher_bp)
api_v1.register_blueprint(ai_bp)
