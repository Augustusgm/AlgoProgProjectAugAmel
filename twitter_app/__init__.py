import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
global user_mail
user_mail = {}

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitter.sqlite'

    db.init_app(app)
    from . import model
    model.init_appp(app)
    
    with app.app_context():
        model.init_user_mail(user_mail)
        

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .model import model as model_blueprint
    app.register_blueprint(model_blueprint)

    return app
