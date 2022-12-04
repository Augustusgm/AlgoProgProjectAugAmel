from flask import Blueprint, jsonify, request, current_app, g
import click
from flask_sqlalchemy import SQLAlchemy
from . import db, user_by_name,user_by_id,follows, tweet_find, tweet_likes
import networkx as nx
from os.path import exists
from collections import deque
import pickle


model = Blueprint('model', __name__)



class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    tweets = db.relationship("Tweet", cascade="all, delete")
    
class Tweet(db.Model):
    __tablename__ = "tweet"
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(256))
    content = db.Column(db.String(2048))
    date = db.Column(db.Date)
    
class Follow(db.Model):
    uid1 = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, primary_key=True)
    uid2 = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, primary_key=True)
    
   
def get_db():
    if 'db' not in g:
        g.db = db

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.session.close()
        
def init_db():
    db = get_db()
    with current_app.app_context():
        db.create_all()
    

def init_appp(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    
def init_user_by_name():
    if exists('instance/twitter.sqlite') :
        user = User.query.all()
        for u in user:
            user_by_name[u.username] =  {
                'id':u.id,
                'username':u.username,
                'email':u.email
                }
            
def update_user_by_name( username, user):
        user_by_name[username] =  {
                'id':user.id,
                'username':user.username,
                'email':user.email
                }
        
def del_user_by_name(name):
        user_by_name.pop(name,None)
        
def init_user_by_id():
    if exists('instance/twitter.sqlite') :
        user = User.query.all()
        for u in user:
            user_by_id[u.id] =  {
                'id':u.id,
                'username':u.username,
                'email':u.email
                }
            
def update_user_by_id(id, user):
        user_by_id[id] =  {
                'id':user.id,
                'username':user.username,
                'email':user.email
                }
        
def del_user_by_id(id):
        user_by_id.pop(id,None)
        
def init_tweet_find():
    if exists('instance/twitter.sqlite') :
        tweets = Tweet.query.all()
        for tweet in tweets:
            sentence = tweet.title + ' ' + tweet.content
            l_sentence = sentence.lower().split()
            for l in l_sentence:
                if l in tweet_find:
                    tweet_find[l].appendleft(tweet.id)
                else:
                    tweet_find[l] = deque([tweet.id], maxlen=100)
            
def update_tweet_find(tweet):
        sentence = tweet.title + ' ' + tweet.content
        l_sentence = sentence.lower().split()
        for l in l_sentence:
            if l in tweet_find:
                tweet_find[l].appendleft(tweet.id)
            else:
                tweet_find[l] = deque([tweet.id], maxlen=100)
        
def init_follow_graph():
    if exists('instance/twitter.sqlite') :
        fol = Follow.query.with_entities(Follow.uid1,Follow.uid2).all()
        for f in fol:
            follows.add_edge(f.uid1,f.uid2)
        #graph.add_edges_from(fol)
    
    
def update_follow_graph(uid1, uid2):
    follows.add_edge(uid1,uid2)
    
def del_follow_graph(uid1, uid2):
    follows.remove_edge(uid1,uid2)
    
def del_user_follow_graph(uid):
    try:
        follows.remove_node(uid)
    except:
        pass
    
def init_like_tweet():
    if exists('instance/like_tweets') :
        f = open('instance/like_tweets', 'rb')
        tweet_likes.update(pickle.load(f))
        f.close
    
def close_like_tweet():
    f = open('instance/like_tweets', 'wb')
    pickle.dump(tweet_likes, f)
    f.close
    

def update_like_tweet(uid, tid):
    tid = int(tid)
    if tid not in tweet_likes:
        tweet_likes[tid] = [uid]
    else:
        tweet_likes[tid].append(uid)
    
def del_like_tweet(uid, tid):
    tid = int(tid)
    tweet_likes[tid].remove(uid)
    if len(tweet_likes[tid]):
        tweet_likes.pop(tid)
        
def del_tweet_like_tweet(tid):
    tid = int(tid)
    tweet_likes.pop(tid, None)
    
def del_user_like_tweet(uid):
    for tid in tweet_likes:
        try:
            tweet_likes[tid].remove(uid)
        except ValueError:
            pass
    
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
    
           
 
""" THIS SECTION IS NOT USED 
@model.route("/users", methods=["GET", "POST", "DELETE"])
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
        data = request.get_json(force=True)
        print('data :', data)
        new_user = User(
                name = data['username'],
                email = data['email'],
                password = data['password']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created"}), 200
    if request.method == 'DELETE':
        user = User.query.filter_by(id = user_id).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({}), 200
    
    
@model.route("/api/tweets", methods=["GET", "POST", "DELETE"])
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
        tweet = Tweet.query.filter_by(id = tweet_id).first()
        db.session.delete(tweet)
        db.session.commit()
        return jsonify({}), 200
"""