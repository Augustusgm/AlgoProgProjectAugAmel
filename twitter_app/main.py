from flask import Blueprint, render_template, Blueprint, render_template, redirect, url_for,session, request, current_app, flash, g
from .auth import login_required
from . import model
from . import db
main = Blueprint('main', __name__)

@main.route('/')
def index():
    tweets = model.Tweet.query.all.desc()
    return render_template('index.html', tweets = tweets)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=g.user.username)

@main.route('/tweet')
def tweet():
    # login code goes here
    return render_template('tweet.html')