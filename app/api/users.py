from flask import Blueprint, jsonify
from app.models import User
from app.extensions import db, ma

users_bp = Blueprint('users', __name__)

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True

@users_bp.route('/', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify(UserSchema(many=True).dump(users))
