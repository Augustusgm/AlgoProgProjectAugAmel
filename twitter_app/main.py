from flask import Blueprint, render_template, Blueprint, render_template, redirect, url_for,session, request, current_app, flash, g
from .auth import login_required
from . import models
from . import db
main = Blueprint('main', __name__)

@main.route('/')
def index():
    tweets = models.Tweet.query.all.last(100)
    return render_template('index.html', tweets = tweets)

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=g.user.username)

@main.route('/tweet')
def tweet():
    # login code goes here
    return render_template('tweet.html')