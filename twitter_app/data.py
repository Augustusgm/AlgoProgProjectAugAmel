from . import db
from flask import Blueprint, jsonify, request

data = Blueprint('data', __name__)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24))
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))
    tweets = db.relationship("Tweet", cascade="all, delete")
    
class Tweet(db.Model):
    __tablename__ = "tweet"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(256))
    content = db.Column(db.String(2048))
    date = db.Column(db.Date)
    
@data.route("/users", methods=["GET", "POST", "DELETE"])
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
    
@data.route("/api/users/follows", methods=["GET", "POST", "DELETE"])
def follows(user_id, follows):
    if request.method == 'GET':#We will use a hashmap in the form of python sets to get fast access in average O(1)
        pass
    if request.method == 'POST':
        pass
    if request.method == 'DELETE':
        pass
    
    
    
data.route("/api/tweets", methods=["GET", "POST", "DELETE"])
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