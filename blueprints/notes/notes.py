from flask import Blueprint, request, make_response, jsonify 
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
import globals 
import string

notes_bp = Blueprint("notes_bp", __name__)

notes = globals.db.note

@notes_bp.route("/api/v1.0/notes", methods=["GET"])
def show_all_notes():
    page_num, page_size = 1, 100
    if request.args.get('pn'):
        page_num = int(request.args.get('pn'))
    if request.args.get('ps'):
        page_size = int(request.args.get('ps'))
    page_start = page_size * (page_num - 1)

    data_return = []
    for note in notes.find().skip(page_start).limit(page_size):
        note['_id'] = str(note['_id'])
        if 'notesubs' in note and isinstance(note['notesubs'], list):
            for notesub in note['notesubs']:
                notesub['_id'] = str(notesub['_id'])
        else:
            note['notesubs'] = []
        data_return.append(note)
    return make_response( jsonify( data_return ), 200 )


@notes_bp.route("/api/v1.0/notes/<string:id>", methods=["GET"])
def show_one_note(id):
    if len(id) != 24 or not all(c in string.hexdigits for c in id):
        return make_response( jsonify( { "Error" : "Invalid note ID"} ), 404 )
    note = notes.find_one( { '_id' : ObjectId(id)} )
    if note is not None:
        note['_id'] = str(note['_id'])  # Convert main _id

        # Convert each notesub _id if notesubs exist
        if 'notesubs' in note and isinstance(note['notesubs'], list):
            for notesub in note['notesubs']:
                notesub['_id'] = str(notesub['_id'])
        else:
            note['notesubs'] = []  # Ensure it's always a list

        return make_response(jsonify(note), 200)

    else: 
        return make_response( jsonify( { "Error" : "Invalid note ID"} ), 404 )
    

@notes_bp.route("/api/v1.0/notes", methods=["POST"])
def add_note(): 
    if 'title' in request.form and 'category' in request.form:
        new_note = {
            'title' : request.form['title'],
            'category' : request.form['category']
        }
        new_note_id = notes.insert_one( new_note)
        new_note_link = "http://127.0.0.1:5000/api/v1.0/notes/" + str( new_note_id.inserted_id)
        return make_response( jsonify( { "url" : new_note_link } ), 201)
    else:
        return make_response( jsonify( { "Error" : "Missing Form Data"} ), 404 )


@notes_bp.route("/api/v1.0/notes/<string:id>", methods=["PUT"])
def edit_note(id):
    if 'title' in request.form and 'category' in request.form:
        result = notes.update_one( { '_id' : ObjectId(id) }, {
                "$set" : {
                    "title" : request.form['title'],
                    "category" : request.form['category'],
                }
        })
        if result.matched_count == 1:
            edited_note_link = "http://127.0.0.1:5000/api/v1.0/notes/" + id 
            return make_response( jsonify( { "url" : edited_note_link } ), 200)
        else:
            return make_response( jsonify( { "error" : "Invalid note ID" } ), 404)
    else:
            return make_response( jsonify( { "Error" : "Missing Form Data"} ), 404 )


@notes_bp.route("/api/v1.0/notes/<string:id>", methods=["DELETE"])
@jwt_required()
def delete_note(id):
    if len(id) != 24 or not all(c in string.hexdigits for c in id):
        return make_response( jsonify( { "Error" : "Invalid note ID"} ), 404 )
    result = notes.delete_one( { "_id" : ObjectId(id) } )
    if result.deleted_count == 1:
        return make_response( jsonify( {} ), 200)
    else:
        return make_response( jsonify( { "Error" : "Invalid note ID"} ), 404 )