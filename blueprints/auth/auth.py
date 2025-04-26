from flask import Blueprint, request, make_response, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, get_jwt
)
import datetime
import globals

auth_bp = Blueprint("auth_bp", __name__)

blacklist = globals.db.blacklist
users = globals.db.users


@auth_bp.route("/api/v1.0/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("username") or not data.get("password"):
        return jsonify({ 'message': 'Username and password required' }), 400

    user = users.find_one({ 'username': data['username'] })

    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({ 'message': 'Invalid username or password' }), 401

    access_token = create_access_token(
        identity=user['username'],  
        expires_delta=datetime.timedelta(minutes=30),
        additional_claims={     
            "admin": user.get('admin', False),
            "email": user.get('email'),
            "name": user.get('name')
        }
    )

    return jsonify({ "token": access_token }), 200


@auth_bp.route("/api/v1.0/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # unique identifier for JWT
    blacklist.insert_one({ "jti": jti })
    return jsonify({ "message": "Logout successful" }), 200
