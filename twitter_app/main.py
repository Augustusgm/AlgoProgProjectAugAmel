from flask import Blueprint, render_template, Blueprint, render_template, redirect, url_for,session, request, current_app, flash, g
from .auth import login_required
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/tweet')
def tweet():
    # login code goes here
    return render_template('tweet.html')