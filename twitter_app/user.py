from . import db
from flask import Blueprint, jsonify, request

user = Blueprint('user', __name__)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24))
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))
    tweets = db.relationship("Tweet", cascade="all, delete")
    
@user.route("/api/users", methods=["GET", "POST", "DELETE"])
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
    
@user.route("/api/users/follows", methods=["GET", "POST", "DELETE"])
def follows(user_id, follows):
    if request.method == 'GET':#We will use a hashmap in the form of python sets to get fast access in average O(1)
        pass
    if request.method == 'POST':
        pass
    if request.method == 'DELETE':
        pass