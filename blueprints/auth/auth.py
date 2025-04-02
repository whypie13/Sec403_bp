from flask import Blueprint, request, make_response, jsonify
from decorators import jwt_required
import globals
import jwt
import datetime
import bcrypt
import globals

auth_bp = Blueprint("auth_bp", __name__)

blacklist = globals.db.blacklist 
users = globals.db.users

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    users = globals.db.users

    if users.find_one({"username": data["username"]}) or users.find_one({"email": data["email"]}):
        return jsonify({"message": "Username or Email already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    new_user = {
        "username": data["username"],
        "email": data["email"],
        "password": hashed_password,
    }

    users.insert_one(new_user)
    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/api/v1.0/login", methods=["GET"])
def login():
    auth = request.authorization
    if auth:
        user = users.find_one( { 'username' : auth.username} )
        if user is not None:
            if bcrypt.checkpw( bytes( auth.password, 'UTF-8'), user['password'] ):
                token = jwt.encode( {
                    'user' : auth.username,
                    'admin' : user['admin'],
                    'exp' : datetime.datetime.now( datetime.UTC ) + datetime.timedelta( minutes=30 )
                }, globals.secret_key, algorithm='HS256' )
                return make_response( jsonify( { 'token' : token } ), 200)
            else:
                return make_response(jsonify( { 'message' : 'Password Incorrect'} ), 401 )
        else:
            return make_response(jsonify( {'message' : 'Username Incorrect'} ), 401 )
    return make_response(jsonify( { 'message' : 'Authentication Required'} ), 401 )


@auth_bp.route("/api/v1.0/logout", methods=["GET"])
@jwt_required
def logout():
    token = request.headers['x-access-token']
    blacklist.insert_one( { 'token' : token} )
    return make_response( jsonify( { 'message' : 'Logout Successful' } ), 200 )