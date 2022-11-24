from flask import Blueprint, render_template, Blueprint, render_template, redirect, url_for,session, request, current_app, flash, g
from .auth import login_required
from .model import User, Tweet, Follow
from . import db
from . import user_by_name
from . import user_by_id
from . import follows
import networkx as nx
from .model import update_follow_graph
main = Blueprint('main', __name__)

@main.route('/')
def index():
    isUser = False
    following = []
    if g.user:
        isUser = True
        following = [g.user.id]
        if g.user.id in follows:
            f = list(map(int, follows.neighbors(g.user.id)))
            following += f
            print(following)
    tweets = Tweet.query.order_by(Tweet.id.desc()).all()
    
    return render_template('index.html', tweets = tweets, isUser = isUser, following = following, user_by_id = user_by_id)

@main.route('/follow_someone/<uid2>')
@login_required
def follow_someone(uid2):
    isFrom = "index"
    uid1 = g.user.id
    if Follow.query.filter_by(uid1 = uid1).filter_by(uid2 = uid2).first():
        return redirect(url_for(f'main.{isFrom}'))
    new_follow = Follow(uid1 = uid1, uid2 = uid2)
    db.session.add(new_follow)
    db.session.commit()
    update_follow_graph(follows, uid1, uid2)
    print(uid1, ' now follows ', uid2)
    return redirect(url_for(f'main.{isFrom}'))

@main.route('/find_someone/<isFrom>', methods=['POST'])
def find_someone(isFrom):
    username = request.form['username']
    if username in user_by_name:
        return redirect(url_for('main.user_profile', user = username))
    flash('this username does not exist')
    return redirect(url_for(f'main.{isFrom}'))

@main.route('/find_tweet', methods=['POST'])
def find_tweet():
    sentence = request.form['sentence']
    l_sentence = sentence.lower().split()
    tweets = Tweet.query.order_by(Tweet.id.desc()).all()
    F_tweets = {}
    for tweet in tweets:
        pass #use bloom filter
    return render_template('find_tweet.html', F_tweets)


@main.route('/profile')
@login_required
def profile():
    tweets = Tweet.query.filter_by(uid = g.user.id).order_by(Tweet.id.desc()).all()
    f = []
    if g.user.id in follows:
            f = list(map(int, follows.neighbors(g.user.id)))
            print(f)
    return render_template('profile.html', name=g.user.username, tweets = tweets, following = f, user_by_id = user_by_id)

@main.route('/user_profile/<user>')
def user_profile(user):
    id_u = user_by_name[user]['id']
    if g.user:
        if g.user.id == id_u:
            return redirect(url_for('main.profile'))
    isUser = False
    following = []
    if g.user:
        isUser = True
        if g.user.id in follows:
            f = list(map(int, follows.neighbors(g.user.id)))
            following = f
            print(following)
    tweets = Tweet.query.filter_by(uid = id_u).order_by(Tweet.id.desc()).all()
    return render_template('user_profile.html', name=user, tweets = tweets, user_by_id = user_by_id, user_by_name = user_by_name, following = following, isUser = isUser)



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
    return redirect(url_for('main.index'))

@main.route('/feed')
@login_required
def feed():
    isUser = False
    following = []
    if g.user:
        isUser = True
        following = [g.user.id]
        if g.user.id in follows:
            f = list(map(int, follows.neighbors(g.user.id)))
            following += f
            print(following)
    tweets = Tweet.query.order_by(Tweet.id.desc()).all()
    return render_template('feed.html', name=g.user.username, tweets = tweets, user_by_id = user_by_id, following = following)