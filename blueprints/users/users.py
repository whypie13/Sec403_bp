from flask import Blueprint, request, make_response, jsonify
from decorators import jwt_required, admin_required
import globals
import string
from bson import ObjectId 

users_bp = Blueprint("users_bp", __name__)

users = globals.db.users


@users_bp.route("/api/v1.0/users", methods=["GET"])
@jwt_required
@admin_required
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
@jwt_required
@admin_required
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


@users_bp.route("/api/v1.0/users", methods=["POST"])
def add_user(): 
    if 'name' in request.form and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'admin' in request.form:
        new_user = {
            'name' : request.form['name'],
            'username' : request.form['username'],
            'password' : request.form['password'],
            'email' : request.form['email'],
            'admin' : request.form['admin']
        }
        new_user_id = users.insert_one( new_user)
        new_user_profile = "http://127.0.0.1:5000/api/v1.0/users/" + str( new_user_id.inserted_id)
        return make_response( jsonify( { "url" : new_user_profile } ), 201)
    else:
        return make_response( jsonify( { "Error" : "Missing Form Data"} ), 404 )
    

@users_bp.route("/api/v1.0/users/<string:id>", methods=["DELETE"])
@jwt_required
@admin_required
def delete_user(id):
    if len(id) != 24 or not all(c in string.hexdigits for c in id):
        return make_response( jsonify( { "Error" : "Invalid User ID"} ), 404 )
    result = users.delete_one( { "_id" : ObjectId(id) } )
    if result.deleted_count == 1:
        return make_response( jsonify( {} ), 200)
    else:
        return make_response( jsonify( { "Error" : "Invalid User ID"} ), 404 )