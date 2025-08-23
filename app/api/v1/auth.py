from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models import User
from app.utils import generate_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'student')

    if role not in ['student', 'teacher']:
        return jsonify({'msg': 'Only student or teacher can register'}), 400

    if not username or not password:
        return jsonify({'msg': 'Username and password required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'msg': 'Username already exists'}), 400

    password_hash = generate_password_hash(password)
    user = User(username=username, password_hash=password_hash, role=role, email=f'{username}@example.com')
    db.session.add(user)
    db.session.commit()
    return jsonify({'msg': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'msg': 'Username and password required'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'msg': 'Invalid username or password'}), 401

    token = generate_token(user.id)
    return jsonify({'token': token, 'user_id': user.id, 'role': user.role}), 200
