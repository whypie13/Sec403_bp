from flask import jsonify, make_response, request 
import jwt
from functools import wraps
import string
import globals


blacklist = globals.db.blacklist


def jwt_required(func):
    @wraps(func)
    def jwt_required_wrapper(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return make_response( jsonify( { 'message' : 'Token is Missing'} ), 401 )
        try:
            data = jwt.decode( token, globals.secret.key, algorithms='HS256' )
        except: 
            return make_response(jsonify( { 'messsage': 'Please Login'} ), 401 )
        bl_token = blacklist.find_one( { 'token' : token} )
        if bl_token is not None:
            return make_response(jsonify( { 'messsage': 'Token has been Cancelled'} ), 401 )
        return func(*args, **kwargs)
    return jwt_required_wrapper


def admin_required(func):
    @wraps(func)
    def admin_required_wrapper(*args, **kwargs):
        token = request.headers['x-access-token']
        data = jwt.decode( token, globals.secret.key, algorithms='HS256')
        if data['admin']:
            return func(*args, **kwargs)
        else:
            return make_response(jsonify( { 'message' : 'Admin Required'} ), 401)
    return admin_required_wrapper 