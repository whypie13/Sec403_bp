import datetime
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin
from blueprints.notes.notes import notes_bp
from blueprints.auth.auth import auth_bp
from blueprints.users.users import users_bp
from blueprints.notesubs.notesubs import notesubs_bp
from blueprints.rssfeeds.rss import rss_bp 
from blueprints.apilist.api import api_bp
from blueprints.rssfeeds.rss2 import rss2_bp
from blueprints.rssfeeds.rss3 import rss3_bp



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=30)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


app.register_blueprint(notes_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(notesubs_bp)
app.register_blueprint(rss_bp)
app.register_blueprint(api_bp)
app.register_blueprint(rss2_bp)
app.register_blueprint(rss3_bp)



if __name__ == "__main__":
    app.run(host='127.0.0.1', debug = True)