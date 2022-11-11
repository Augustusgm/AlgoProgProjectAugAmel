from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlite3 import Connection as SQLite3Connection
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.engine import Engine

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///twitter.file"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = 0

@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
        
db = SQLAlchemy(app)
now = datetime.now()
print(amelie)


class Tweet(db.Model):
    __tablename__ = "tweet"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(256))
    content = db.Column(db.String(2048))
    date = db.Column(db.Date)
    
    
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    tweets = db.relationship("Tweet", cascade="all, delete")


#......
@app.route("/api/users", methods=["GET", "POST", "DELETE"])
def users():
   

 
@app.route("/")
def home():
    #print(db.sesion)
    return "<h1>API Running</h1>"


if __name__ == "__main__":
   
    with app.app_context():
        db.create_all()
    app.run(debug=True, host = "localhost", port = int("5000"))

