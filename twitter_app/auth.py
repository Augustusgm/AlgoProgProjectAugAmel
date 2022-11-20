from flask import Blueprint, render_template, redirect, url_for,session, request, current_app, flash, g
from . import model
from . import db
from .model import User
import functools
import requests
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User.query.filter_by(username=email).first()
    
    if not user or not check_password_hash(user.password, password):
        flash('Username/email or password not registered.')
        return redirect(url_for('auth.login'))
    session.clear()
    session['user_id'] = user['id']

    return redirect(url_for('main.profile'))

@auth.route('/register')
def register():
    return render_template('register.html')

@auth.route('/register', methods=('GET', 'POST'))
def register_post():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        user = User.query.filter_by(email=email).first()
        if user: 
            error = f"User {username} or email {email} is already registered."
            flash(error)
            return redirect(url_for('auth.register'))

        new_user = User(email=email, username=username, password=generate_password_hash(password, method='sha256'))

        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
        
@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(uid=user_id).first()
        
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
