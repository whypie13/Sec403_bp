from flask import jsonify, make_response, request 
import jwt
from functools import wraps
import string
import globals


blacklist = globals.db.blacklist

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