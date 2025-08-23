from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import User
from app.utils import token_required, admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/teachers', methods=['POST'])
@token_required
@admin_required
def create_teacher():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({'msg': 'username, password, and email are required'}), 400

    password_hash = generate_password_hash(password)
    user = User(username=username, password_hash=password_hash, email=email, role='teacher')
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if 'uk_username' in str(e.orig):
            return jsonify({'msg': 'Username already exists'}), 400
        elif 'uk_email' in str(e.orig):
            return jsonify({'msg': 'Email already exists'}), 400
        else:
            return jsonify({'msg': 'Integrity error', 'detail': str(e.orig)}), 400
    return jsonify({'msg': 'Teacher created successfully', 'user_id': user.id}), 201
