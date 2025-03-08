from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from blueprints.notes.notes import notes_bp
from blueprints.auth.auth import auth_bp
from blueprints.users.users import users_bp
from blueprints.notesubs.notesubs import notesubs_bp


app = Flask(__name__)
CORS(app)

app.register_blueprint(notes_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(notesubs_bp)



if __name__ == "__main__":
    app.run(host='127.0.0.1', debug = True)