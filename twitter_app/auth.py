from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash
from . import models
import requests


auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/register')
def register():
    return render_template('register.html')

@auth.route('/register', methods=('GET', 'POST'))
def register_post():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        register_dict = {
            'username' : username,
            'password' : password,
            'email' : email,
            }
        
        #try:
        resp = requests.post('http://127.0.0.1:5000/users', register_dict)
        print(resp)
        #except :
        #    error = f"User {username} is already registered."
        #else:
        #return redirect(url_for("auth.login"))

        flash(error)
        return render_template('register.html')
        
@auth.route('/logout')
def logout():
    return render_template('logout.html')



@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    return redirect(url_for('main.profile'))