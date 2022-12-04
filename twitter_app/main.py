from flask import Blueprint, render_template, Blueprint, render_template, redirect, url_for,session, request, current_app, flash, g
from .auth import login_required
from .model import User, Tweet, Follow
from . import db, user_by_name,user_by_id,follows, tweet_find, tweet_likes
import networkx as nx
from . import model
from thefuzz import fuzz
from thefuzz import process
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
    return render_template('index.html', tweets = tweets, tweet_likes = tweet_likes, user = user, isUser = isUser, following = following, user_by_id = user_by_id)

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
    model.update_follow_graph( uid1, uid2)
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
    model.del_follow_graph(uid1, uid2)
    unfollow = Follow.query.filter_by(uid1 = uid1).filter_by(uid2 = uid2).first()
    db.session.delete(unfollow)
    db.session.commit()
    if argument == "error":
        return redirect(url_for(f'main.{isFrom}'))
    return redirect(url_for(f'main.{isFrom}', user = argument))

@main.route('/like_tweet/<isFrom>/<int:tid>/<argument>')
@login_required
def like_tweet(isFrom, tid, argument):
    if isFrom == "home":
        isFrom = "index"
    uid1 = g.user.id
    model.update_like_tweet( uid1, tid)
    if argument == "error":
        return redirect(url_for(f'main.{isFrom}'))
    return redirect(url_for(f'main.{isFrom}', user = argument))

@main.route('/dislike_tweet/<isFrom>/<int:tid>/<argument>')
@login_required
def dislike_tweet(isFrom, tid, argument):
    if isFrom == "home":
        isFrom = "index"
    uid1 = g.user.id
    model.del_like_tweet( uid1, tid)
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
    final_tweets_a = []
    more = False
    for l in l_sentence:
        if l in tweet_find:
            for t in tweet_find[l]:
                final_tweets.append(t)
    if len(final_tweets) < 10 :
        words_in_tweets = tweet_find.keys()
        i = -1
        while len(final_tweets_a)<10 and i<4:
            i+=1
            for l in l_sentence:
                c= process.extract(l, words_in_tweets, limit=i+1)
                word = c[i][0]
                score = c[i][1]
                if word != l and score>0.9:
                    for t in tweet_find[word]:
                        final_tweets_a.append(t)
        if len(final_tweets_a)>0:
            more = True
    tweets = Tweet.query.filter(Tweet.id.in_(final_tweets)).order_by(Tweet.id.desc()).all()
    tweets_a = Tweet.query.filter(Tweet.id.in_(final_tweets_a)).order_by(Tweet.id.desc()).all()
    isUser = False
    user = False
    following = []
    if g.user:
        isUser = True
        following = [g.user.id]
        user = g.user.id
        if g.user.id in follows:
            f = list(map(int, follows.neighbors(g.user.id)))
            following += f
    return render_template('find_tweet.html', tweets = tweets, tweets_a = tweets_a , more = more, user = user, isUser = isUser, following = following, user_by_id = user_by_id, research=research)


@main.route('/profile')
@login_required
def profile():
    tweets = Tweet.query.filter_by(uid = g.user.id).order_by(Tweet.id.desc()).all()
    f = []
    pred = []
    doublepred = set()
    if g.user.id in follows:
        f = list(map(int, follows.neighbors(g.user.id)))
        pred = list(map(int, follows.predecessors(g.user.id))) 
    if g.user.id in follows:
        for predec in list(map(int, follows.predecessors(g.user.id))):
            for i in list(map(int, follows.predecessors(predec))):
                doublepred.add(i)
    doublepred = list(doublepred)
    return render_template('profile.html', doublepred = doublepred, pred = pred, tweet_likes= tweet_likes, name=g.user.username, myid =g.user.id, tweets = tweets, following = f, user_by_id = user_by_id)

@main.route('/friends/<int:uid>')
def friends(uid):
    isUser1 = False
    isUser2 = False
    if g.user:
        isUser1 = True
        if g.user.id == uid:
            isUser2 = True
    follow_list = list(follows.edges())
    connection_list = {}
    people_with_friends = {}
    the_friend_list = []
    for i in range(len(follow_list)):
        first, second = follow_list[i]
        try:
            if max(first,second) in connection_list[min(first,second)]:
                if uid == first:
                    the_friend_list.append(second)
                if uid == second:
                    the_friend_list.append(first)    
                try:
                    people_with_friends[first]+=1
                except KeyError:
                    people_with_friends[first]=1
                try:
                    people_with_friends[second]+=1
                except KeyError:
                    people_with_friends[second]=1
            else:
                connection_list[min(first,second)].add(max(first,second))
        except KeyError:
            connection_list[min(first,second)] = set()
            connection_list[min(first,second)].add(max(first,second))
    return render_template('friends.html', isUser1 = isUser1, isUser2 = isUser2, user_by_id = user_by_id, the_friend_list = the_friend_list, people_with_friends = people_with_friends, uid=uid)


@main.route('/user_profile/<user>')
def user_profile(user):
    id_u = user_by_name[user]['id']
    if g.user:
        if g.user.id == id_u:
            return redirect(url_for('main.profile'))
    isUser = False
    isfollowing = False
    me = False
    Me_following = []
    if g.user:
        isUser = True
        me = g.user.id
        if follows.has_edge(g.user.id,id_u):
            isfollowing = True
        if g.user.id in follows:
            f = list(map(int, follows.neighbors(g.user.id)))
            Me_following = f
    following = []
    if id_u in follows:
        f = list(map(int, follows.neighbors(id_u)))
        following = f
    tweets = Tweet.query.filter_by(uid = id_u).order_by(Tweet.id.desc()).all()
    return render_template('user_profile.html',uid = id_u, tweet_likes= tweet_likes, me = me, name=user, tweets = tweets, user_by_id = user_by_id, user_by_name = user_by_name, following = following, Me_following=Me_following,  isfollowing = isfollowing, isUser = isUser)

    


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
        model.update_tweet_find(new_tweet)
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
    return render_template('feed.html',tweet_likes= tweet_likes, name=g.user.username,user = g.user.id, tweets = tweets, user_by_id = user_by_id, following = following)

@main.route('/profile/<int:tid>')
@login_required
def tweet_delete(tid):
    tweet = Tweet.query.filter_by(id = tid).first()
    db.session.delete(tweet)
    db.session.commit()
    model.del_tweet_like_tweet(tid)
    return redirect(url_for('main.profile'))

@main.route('/user_delete')
@login_required
def user_delete():
    tweets = Tweet.query.filter_by(uid = g.user.id).all()
    for tweet in tweets:
        model.del_tweet_like_tweet(tweet.id)
    user = User.query.filter_by(id = g.user.id).first()
    db.session.delete(user)
    db.session.commit()
    model.del_user_like_tweet(g.user.id)
    model.del_user_follow_graph(g.user.id)
    model.del_user_by_name(g.user.username)
    model.del_user_by_id(g.user.id)
    return redirect(url_for('auth.logout'))

@main.route('/ask_user_delete')
@login_required
def ask_user_delete():
    return render_template('check_delete.html')