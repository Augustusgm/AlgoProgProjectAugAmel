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
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))
    tweets = db.relationship("Tweet", cascade="all, delete")

@app.route("/api/users", methods=["GET", "POST", "DELETE"])
def users(user_id = 0):
    if request.method == 'GET':
        users = User.query.all()
        all_users_ll = []*len(users) #autre data structure?
        for user in users:
            all_users_ll[user.id] = {
                'id':user.id,
                'username':user.username,
                'email':user.email,
                'password':user.password
                }
        user = all_users_ll[user_id]
        return jsonify(user), 200
    #alternative data structure: hashmap gives complexity average in O(1            )
    if request.method == 'POST':
        data = request.get_json()
        new_user = User(
                name = data['username'],
                email = data['email'],
                password = data['password']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created"}), 200
    if request.method == 'DELETE':
        user = User.query.filter_by(id = user_id),first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({}), 200

 
@app.route("/")
def home():
    #print(db.sesion)
    return "<h1>API Running</h1>"


if __name__ == "__main__":
   
    with app.app_context():
        db.create_all()
    app.run(debug=True, host = "localhost", port = int("5000"))