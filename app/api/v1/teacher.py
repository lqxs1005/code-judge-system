from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import User
from app.schemas import UserSchema
import csv
import io

teacher_bp = Blueprint('teacher', __name__)

def teacher_or_admin_required():
    user_id = getattr(g, 'current_user_id', None)
    if not user_id:
        return False
    user = db.session.get(User, user_id)
    if not user or user.role not in ('teacher', 'admin'):
        return False
    g.current_user = user
    return True

@teacher_bp.route('/teachers/students', methods=['GET'])
@token_required
def get_students():
    if not teacher_or_admin_required():
        return jsonify({'msg': 'Teacher or admin privilege required'}), 403
    students = User.query.filter_by(role='student').all()
    return jsonify(UserSchema(many=True).dump(students)), 200

@teacher_bp.route('/teachers/students/import', methods=['POST'])
@token_required
def import_students():
    if not teacher_or_admin_required():
        return jsonify({'msg': 'Teacher or admin privilege required'}), 403

    if 'file' not in request.files:
        return jsonify({'msg': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'msg': 'No selected file'}), 400

    try:
        stream = io.StringIO(file.stream.read().decode('utf-8'))
        reader = csv.DictReader(stream, fieldnames=['username', 'password', 'email'])
        students = []
        db.session.begin(subtransactions=True)
        for row in reader:
            username = row.get('username')
            password = row.get('password')
            email = row.get('email')
            if not username or not password or not email:
                db.session.rollback()
                return jsonify({'msg': f'Invalid row: {row}'}), 400
            password_hash = generate_password_hash(password)
            user = User(username=username, password_hash=password_hash, email=email, role='student')
            db.session.add(user)
            students.append(user)
        db.session.commit()
        return jsonify({'msg': 'Students imported successfully', 'count': len(students)}), 201
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({'msg': 'Integrity error during import (possible duplicate username or email)', 'detail': str(e.orig)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Failed to import students', 'detail': str(e)}), 400
