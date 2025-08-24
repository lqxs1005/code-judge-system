import datetime
import jwt
from flask import request, jsonify, g, current_app
from functools import wraps
from app.models import User
from app.extensions import db

JWT_EXP_DELTA_SECONDS = 3600 * 24  # 1天

def generate_token(user_id):
    SECRET_KEY = current_app.config.get('SECRET_KEY', 'dev-secret-key')
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXP_DELTA_SECONDS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        SECRET_KEY = current_app.config.get('SECRET_KEY', 'dev-secret-key')
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'msg': 'Missing or invalid Authorization header'}), 401
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            g.current_user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'msg': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'msg': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user_id = getattr(g, 'current_user_id', None)
        if not user_id:
            return jsonify({'msg': 'User not authenticated'}), 401
        user = db.session.get(User, user_id)
        if not user or user.role != 'admin':
            return jsonify({'msg': 'Admin privilege required'}), 403
        g.current_user = user
        return f(*args, **kwargs)
    return decorated
