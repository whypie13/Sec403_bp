from flask import Blueprint, request, make_response, jsonify
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
import globals
import string
from bson import ObjectId 

users_bp = Blueprint("users_bp", __name__)

users = globals.db.users


@users_bp.route("/api/v1.0/users", methods=["GET"])
@jwt_required()
def show_all_users():
    page_num, page_size = 1, 100
    if request.args.get('pnum'):
        page_num = int(request.args.get('pnum'))
    if request.args.get('psize'):
        page_size = int(request.args.get('psize'))
    page_start = page_size * (page_num - 1)

    return_users = []
    for user in users.find().skip(page_start).limit(page_size):
        user['_id'] = str(user['_id'])
        user.pop('password')
        return_users.append(str(user))

    return make_response( jsonify( return_users ), 200 )
    


@users_bp.route("/api/v1.0/users/<string:id>", methods=["GET"])
@jwt_required()
def show_one_user(id):
    if len(id) != 24 or not all(c in string.hexdigits for c in id):
        return make_response( jsonify( { "Error" : "Invalid User ID"} ), 404 )
    user = users.find_one( { '_id' : ObjectId(id)} )
    if user is not None:
        user['_id'] = str( user['_id'] )
        user.pop('password')
        return make_response( jsonify( user ), 200 )
    else: 
        return make_response( jsonify( { "Error" : "Invalid User ID"} ), 404 )


@users_bp.route("/api/v1.0/register", methods=["POST"])
def register_user(): 
    data = request.get_json()

    if users.find_one({"username": data["username"]}) or users.find_one({"email": data["email"]}):
        return jsonify({"message": "Username or Email already exists"}), 409
    
    hashed_password = generate_password_hash(data["password"])

    new_user = {
            'name' : data['name'],
            'username' : data['username'],
            'password' : hashed_password,
            'email' : data['email']
        }
    
    new_user_id = users.insert_one( new_user)
    new_user_profile = "http://127.0.0.1:5000/api/v1.0/users/" + str( new_user_id.inserted_id)
    return make_response( jsonify( { "User registered successfully" : new_user_profile } ), 201)
    

@users_bp.route("/api/v1.0/users/profile", methods=["GET"])
@jwt_required()
def user_profile():
    username = get_jwt_identity() 
    user = users.find_one({"username": username})

    if user:
        return jsonify({
            "name": user.get("name"),
            "username": user.get("username"),
            "email": user.get("email")
        }), 200
    else:
        return jsonify({"message": "User not found"}), 404


@users_bp.route("/api/v1.0/users/<string:id>", methods=["DELETE"])
@jwt_required()
def delete_user(id):
    if len(id) != 24 or not all(c in string.hexdigits for c in id):
        return make_response( jsonify( { "Error" : "Invalid User ID"} ), 404 )
    result = users.delete_one( { "_id" : ObjectId(id) } )
    if result.deleted_count == 1:
        return make_response( jsonify( {} ), 200)
    else:
        return make_response( jsonify( { "Error" : "Invalid User ID"} ), 404 )