from flask import Blueprint, render_template, Blueprint, render_template, redirect, url_for,session, request, current_app, flash, g
from .auth import login_required
from .model import User, Tweet
from . import db
main = Blueprint('main', __name__)

@main.route('/')
def index():
    tweets = Tweet.query.order_by(Tweet.id.desc()).all()
    return render_template('index.html', tweets = tweets)

@main.route('/profile')
@login_required
def profile():
    tweets = Tweet.query.filter_by(uid = g.user.username).order_by(Tweet.id.desc()).all()
    return render_template('profile.html', name=g.user.username, tweets = tweets)@main.route('/tweet', methods=('GET', 'POST'))

@main.route('/tweet')
@login_required
def tweet():
    return render_template("tweet.html")


@main.route('/tweet', methods=('GET', 'POST'))
@login_required
def tweet_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_tweet = Tweet(title=title, content=content, uid = g.user.id )

        db.session.add(new_tweet)
        db.session.commit()
    return render_template("main.index")