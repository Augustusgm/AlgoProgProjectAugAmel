from flask import Blueprint, render_template, redirect, url_for, request, current_app
from . import models

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        register_dict = {
            'username' : username,
            'password' : password,
            'email' : email,
            }
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        if not email:
            error = 'email is required.'
            
        if error is None:
            try:
                resp = request.post('model/users', register_dict)
            except resp.DoesNotExist:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

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