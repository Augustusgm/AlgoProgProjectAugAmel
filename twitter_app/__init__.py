import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
import networkx as nx
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlite3 import Connection as SQLite3Connection

# configure sqlite3 to enforce foreign key contraints
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


db = SQLAlchemy()
global user_by_name
user_by_name = {}
global follows
follows = nx.DiGraph()
global user_by_id
user_by_id = {}
global tweet_find
tweet_find = {}
global tweet_likes
tweet_likes = {}

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///twitter.sqlite'

    db.init_app(app)
    from . import model
    model.init_appp(app)
    
    with app.app_context():
        model.init_user_by_name()
    
    with app.app_context():
        model.init_user_by_id()   

    with app.app_context():
        model.init_follow_graph()
        
    with app.app_context():
        model.init_tweet_find()
    
    with app.app_context():
        model.init_like_tweet()  
           
    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from .model import model as model_blueprint
    app.register_blueprint(model_blueprint)

    from .gen_data import gen_data as gen_data_blueprint
    app.register_blueprint(gen_data_blueprint)
    
    return app
