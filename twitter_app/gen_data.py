from essential_generators import DocumentGenerator
from flask import Blueprint, render_template, Blueprint, render_template, redirect, url_for,session, request, current_app, flash, g
from os.path import exists
from . import db, user_by_name,user_by_id,follows, model
from .model import User,Tweet, Follow
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from sqlalchemy.orm import load_only

gen_data = Blueprint('gen_data', __name__)

@gen_data.route('/generate')
def generate():
    isUser = False
    if g.user:
        isUser = True
    return render_template('generate.html', isUser = isUser) 
 
@gen_data.route('/generate_post', methods=['POST'])
def generate_post():
    nb = int(request.form['research'])
    if request.form['action'] == 'Users':
        generate_people(nb)
    elif request.form['action'] == 'Tweets':
        generate_tweets(nb)
    elif request.form['action'] == 'Follows':
        generate_follows(nb)
    elif request.form['action'] == 'Likes':
        generate_likes(nb)
    return redirect(url_for('gen_data.generate'))


def generate_people(n):
    gen = DocumentGenerator()
    template = {'name': 'name', 'email':'email'}
    gen.set_template(template)
    documents = gen.documents(n)
    for i in range(n):
        new_user = User(
                username = documents[i]['name'],
                email = documents[i]['email'],
                password = generate_password_hash(documents[i]['name'], method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        model.update_user_by_name(new_user.username, new_user)
        model.update_user_by_id(new_user.id, new_user)
        
def get_random_user():
    return User.query.order_by(func.random()).first()

def get_random_tweet():
    return Tweet.query.order_by(func.random()).first()
    
def generate_tweets(n):
    gen = DocumentGenerator()
    template = {'title': 'word', 'content':'sentence'}
    gen.set_template(template)
    documents = gen.documents(n)
    for i in range(n):
        uid = get_random_user().id
        new_tweet = Tweet(
                uid = uid,
                title = documents[i]['title'],
                content = documents[i]['content'])
        db.session.add(new_tweet)
        db.session.commit()
        model.update_tweet_find(new_tweet)
        
def generate_follows(n):
    for i in range(n):
        uid1 = get_random_user().id
        uid2 = get_random_user().id
        if uid1 != uid2:
            if not Follow.query.filter_by(uid1 = uid1).filter_by(uid2 = uid2).first():
                new_follow = Follow(uid1 = uid1, uid2 = uid2)
                db.session.add(new_follow)
                db.session.commit()
                model.update_follow_graph( uid1, uid2)
                
                
def generate_likes(n):
    for _ in range(n):
        uid = get_random_user().id
        tid = get_random_tweet().id
        model.update_like_tweet( uid, tid)