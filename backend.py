from datetime import datetime
from sqlite3 import Connection as SQLite3Connection

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///twitter.sqlite"
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
    '''followers = db.Column(db.Set)'''
    tweets = db.relationship("Tweet", cascade="all, delete")
    
'''class Followers(db.Model):
    __tablename__ = "followers"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    follows = db.relationship("User", cascade="all, delete")
    #a bloom filter would answer very fast if a user follows another one.'''

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
                'password':user.password, 
                'followers':user.followers
                }
        user = all_users_ll[user_id]
        return jsonify(user), 200
    #alternative data structure: hashmap gives complexity average in O(1            )
    if request.method == 'POST':
        data = request.get_json()
        new_user = User(
                name = data['username'],
                email = data['email'],
                password = data['password'],
                follows= {}
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created"}), 200
    if request.method == 'DELETE':
        user = User.query.filter_by(id = user_id),first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({}), 200
    
@app.route("/api/users/follows", methods=["GET", "POST", "DELETE"])
def follows(user_id, follows):
    if request.method == 'GET':#We will use a hashmap in the form of python sets to get fast access in average O(1)
        pass
    if request.method == 'POST':
        pass
    if request.method == 'DELETE':
        pass

@app.route("/api/tweets", methods=["GET", "POST", "DELETE"])
def tweets(tweet_id = 0):
    if request.method == 'GET':
        tweets = Tweet.query.all()
        all_tweets = []*len(tweets) #autre data structure?
        for tweet in tweets:
            all_tweets[tweet.id] = {
                'id':tweet.id,
                'uid':tweet.uid, 
                'title':tweet.title,
                'content':tweet.content,
                'date':tweet.date
                }
        tweet = tweets[tweet_id]
        return jsonify(tweet), 200
    #alternative data structure: hashmap gives complexity average in O(1            )
    if request.method == 'POST':
        data = request.get_json()
        new_tweet = Tweet(
                title = data['title'],
                content = data['content'],
                uid = data['user']
        )
        db.session.add(new_tweet)
        db.session.commit()
        return jsonify({"message": "Tweet posted"}), 200
    if request.method == 'DELETE':
        tweet = Tweet.query.filter_by(id = tweet_id),first()
        db.session.delete(tweet)
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
    
    
def create_app():
    # existing code omitted
    from . import db
    db.init_app(app)
    from . import relie
    app.register_blueprint(relie.bp)

    return app