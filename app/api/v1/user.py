from flask import Blueprint, jsonify
from app.models import User
from app.schemas import UserSchema
from app.utils import token_required, admin_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@token_required
@admin_required
def get_users():
    users = User.query.all()
    return jsonify(UserSchema(many=True).dump(users))
