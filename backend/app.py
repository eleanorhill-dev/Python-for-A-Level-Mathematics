from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from extensions import db
from routes import register_routes
from flask_bcrypt import Bcrypt
import os

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = "bdgforagj"

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'Learning_Platform_DB.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    bcrypt = Bcrypt(app)
    db.init_app(app)
    migrate = Migrate(app,db)
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

    register_routes(app, db, bcrypt)

    if not os.path.exists(os.path.join(basedir, 'instance')):
        os.makedirs(os.path.join(basedir, 'instance'))

    with app.app_context():
        db.create_all()

    return app

