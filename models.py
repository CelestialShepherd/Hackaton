# -*- coding: utf-8 -*-
from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

voters = db.Table('voters',
    db.Column('voter_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('voted_id', db.Integer, db.ForeignKey('user.id')))

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    midle_name = db.Column(db.String(64), index=True)
    address = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    phone = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    voted = db.relationship(
        'User', secondary=voters,
        primaryjoin=(voters.c.voter_id == id),
        secondaryjoin=(voters.c.voted_id == id),
        backref=db.backref('voters', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.email) 
    
    def vote(self, user):
        if not self.is_voting(user):
            self.voted.append(user)
    def cancel_vote(self, user):
        if self.is_voting(user):
            self.voted.remove(user)
    def is_voting(self, user):
        return self.voted.filter(
            voters.c.voted_id == user.id).count() > 0

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

@login.user_loader
def load_user(id):
        return User.query.get(int(id))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Offer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    body = db.Column(db.String(250), index=True)
    on_site = db.Column(db.Boolean, index=True, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))#Создатель предложения
    
    def __repr__(self):
        return '<Offer {}>'.format(self.title)

class Feedback(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    feedbody = db.Column(db.String(250), index=True) 
    feedemail = db.Column(db.String(120), index=True)

    def __repr__(self): 
        return '<Feedback {}>'.format(self.body) 
