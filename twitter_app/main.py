from flask import Blueprint, render_template, Blueprint, render_template, redirect, url_for,session, request, current_app, flash, g
from .auth import login_required
from .model import User, Tweet, Follow
from . import db, user_by_name,user_by_id,follows, tweet_find
import networkx as nx
from .model import update_follow_graph, del_follow_graph, update_tweet_find
main = Blueprint('main', __name__)

@main.route('/')
def index():
    isUser = False
    following = []
    user = False
    if g.user:
        isUser = True
        following = [g.user.id]
        user = g.user.id
        if g.user.id in follows:
            f = list(map(int, follows.neighbors(g.user.id)))
            following += f
    tweets = Tweet.query.order_by(Tweet.id.desc()).all()
    return render_template('index.html', tweets = tweets,user = user, isUser = isUser, following = following, user_by_id = user_by_id)

@main.route('/follow_someone/<isFrom>/<int:uid2>/<argument>')
@login_required
def follow_someone(isFrom, uid2, argument):
    if isFrom == "home":
        isFrom = "index"
    uid1 = g.user.id
    if Follow.query.filter_by(uid1 = uid1).filter_by(uid2 = uid2).first():
        return redirect(url_for(f'main.{isFrom}'))
    new_follow = Follow(uid1 = uid1, uid2 = uid2)
    db.session.add(new_follow)
    db.session.commit()
    update_follow_graph( uid1, uid2)
    if argument == "error":
        return redirect(url_for(f'main.{isFrom}'))
    return redirect(url_for(f'main.{isFrom}', user = argument))

@main.route('/unfollow_someone/<isFrom>/<int:uid2>/<argument>')
@login_required
def unfollow_someone(isFrom, uid2, argument):
    if isFrom == "home":
        isFrom = "index"
    uid1 = g.user.id
    if not Follow.query.filter_by(uid1 = uid1).filter_by(uid2 = uid2).first():
        return redirect(url_for(f'main.{isFrom}'))
    del_follow_graph(uid1, uid2)
    unfollow = Follow.query.filter_by(uid1 = uid1).filter_by(uid2 = uid2).first()
    db.session.delete(unfollow)
    db.session.commit()
    if argument == "error":
        return redirect(url_for(f'main.{isFrom}'))
    return redirect(url_for(f'main.{isFrom}', user = argument))

@main.route('/find/<isFrom>', methods=['POST'])
def find(isFrom):
    research = request.form['research']
    if request.form['action'] == 'Username':
        return redirect(url_for('main.find_someone', research = research, isFrom = isFrom))
    elif request.form['action'] == 'Tweet':
        return redirect(url_for('main.find_tweet', research = research ))
    return redirect(url_for(f'main.{isFrom}'))

@main.route('/find_someone/<research>/<isFrom>')
def find_someone(research, isFrom):
    if research in user_by_name:
        return redirect(url_for('main.user_profile', user = research))
    flash('this username does not exist')
    return redirect(url_for(f'main.{isFrom}'))

@main.route('/find_tweet/<research>')
def find_tweet(research):
    l_sentence = research.lower().split()
    final_tweets = []
    for l in l_sentence:
        if l in tweet_find:
            for t in tweet_find[l]:
                final_tweets.append(t)
    if len(final_tweets) < 10 :
        pass #extend search
    tweets = Tweet.query.filter(Tweet.id.in_(final_tweets)).order_by(Tweet.id.desc()).all()
    isUser = False
    user = False
    if g.user:
        isUser = True
        following = [g.user.id]
        user = g.user.id
        if g.user.id in follows:
            f = list(map(int, follows.neighbors(g.user.id)))
            following += f
    return render_template('find_tweet.html', tweets = tweets, user = user, isUser = isUser, following = following, user_by_id = user_by_id)


@main.route('/profile')
@login_required
def profile():
    tweets = Tweet.query.filter_by(uid = g.user.id).order_by(Tweet.id.desc()).all()
    f = []
    if g.user.id in follows:
            f = list(map(int, follows.neighbors(g.user.id)))
    return render_template('profile.html', name=g.user.username, tweets = tweets, following = f, user_by_id = user_by_id)

@main.route('/user_profile/<user>')
def user_profile(user):
    id_u = user_by_name[user]['id']
    if g.user:
        if g.user.id == id_u:
            return redirect(url_for('main.profile'))
    isUser = False
    isfollowing = False
    if g.user:
        isUser = True
        if follows.has_edge(g.user.id,id_u):
            isfollowing = True
    Me_following = []
    if g.user.id in follows:
        f = list(map(int, follows.neighbors(g.user.id)))
        Me_following = f
    following = []
    if id_u in follows:
        f = list(map(int, follows.neighbors(id_u)))
        following = f
    tweets = Tweet.query.filter_by(uid = id_u).order_by(Tweet.id.desc()).all()
    return render_template('user_profile.html', name=user, tweets = tweets, user_by_id = user_by_id, user_by_name = user_by_name, following = following, Me_following=Me_following,  isfollowing = isfollowing, isUser = isUser)

    


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
        update_tweet_find(new_tweet)
    return redirect(url_for('main.index'))

@main.route('/feed')
@login_required
def feed():
    following = [g.user.id]
    if g.user.id in follows:
        f = list(map(int, follows.neighbors(g.user.id)))
        following += f
        print(following)
    tweets = Tweet.query.filter(Tweet.uid.in_(following)).order_by(Tweet.id.desc()).all()
    return render_template('feed.html', name=g.user.username,user = g.user.id, tweets = tweets, user_by_id = user_by_id, following = following)