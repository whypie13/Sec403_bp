from flask import Blueprint, request, make_response, jsonify
from decorators import jwt_required, admin_required
from bson import ObjectId 
import globals 
import string


notesubs_bp = Blueprint("notesubs_bp", __name__)

notes = globals.db.note

@notesubs_bp.route("/api/v1.0/notes/<string:id>/notesubs", methods=["POST"])
def add_new_notesub(id): 
    if 'username' in request.form and 'comment' in request.form and 'riskscore' in request.form and 'source' in request.form:
        new_notesub = {
            '_id' : ObjectId(),
            'username' : request.form['username'],
            'comment' : request.form['comment'], 
            'riskscore' : request.form['riskscore'],
            'source' : request.form['source']
        }
        notes.update_one( { "_id" : ObjectId(id) }, {
            "$push" : { "notesubs" : new_notesub }
        })
        new_notesub_link = "http://127.0.0.1:5000/api/v1.0/notes/" + id + "/notesubs/" + str( new_notesub['_id'] )
        return make_response( jsonify( { "url" : new_notesub_link} ), 201) 
    else:
        return make_response( jsonify( { "Error" : "Missing Form Data"} ), 404 )



@notesubs_bp.route("/api/v1.0/notes/<string:id>/notesubs", methods=["GET"])
def fetch_all_notesubs(id): 
    data_to_return = []
    note = notes.find_one( {"_id" : ObjectId(id) }, {"notesubs" : 1, "_id" : 0 } )
    if note and 'notesubs' in note and isinstance(note['notesubs'], list):
        for notesub in note['notesubs']:
            notesub['_id'] = str(notesub['_id'])
            data_to_return.append(notesub)
    return make_response( jsonify( data_to_return), 200)


@notesubs_bp.route("/api/v1.0/notes/<string:b_id>/notesubs/<string:n_id>", methods=["GET"])
def fetch_one_notesub(b_id, n_id): 
    if len(n_id) != 24 or not all(c in string.hexdigits for c in n_id):
        return make_response( jsonify( { "Error" : "Invalid Note ID"} ), 404 )
    note = notes.find_one( { "notesubs._id" : ObjectId(n_id) }, {
                             "_id" : 0, "notesubs.$" : 1
    })
    if note is None:
        return make_response( jsonify( { "error" : "Invalid Note ID or notesub ID"} ), 404)
    note['notesubs'][0]['_id'] = str( note['notesubs'][0]['_id'] )
    return make_response( jsonify( note['notesubs'][0] ), 200)


@notesubs_bp.route("/api/v1.0/notes/<string:b_id>/notesubs/<string:r_id>", methods=["PUT"])
@jwt_required
def edit_notesub(b_id, n_id):
    altered_notesub = {
        "notesubs.$.username" : request.form['username'],
        "notesubs.$.comment" : request.form['comment'],
        "notesubs.$.riskscore" : request.form['riskscore'],
        "notesubs.$.source" : request.form['source']
    }
    notes.update_one( {
        "notesubs._id" : ObjectId(n_id)
    }, {
        "$set" : altered_notesub
    })
    altered_notesub_url = "http://127.0.0.1:5000/api/v1.0/notes/" + b_id + "/notesubs/" + n_id
    return make_response( jsonify( {"url" : altered_notesub_url} ), 200)


@notesubs_bp.route("/api/v1.0/notes/<string:b_id>/notesubs/<string:n_id>", methods=["DELETE"])
def delete_notesub(b_id, n_id):
    if len(n_id) != 24 or not all(c in string.hexdigits for c in n_id):
        return make_response( jsonify( { "Error" : "Invalid Note ID"} ), 404 )
    notes.update_one( {
        "_id" : ObjectId(b_id)
    }, {
        "$pull" : {"notesubs" : { "_id" : ObjectId(n_id)} }
    })
    return make_response( jsonify( {} ), 200)