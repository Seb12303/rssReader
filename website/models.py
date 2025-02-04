from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Relations
article_feed_association = db.Table(
    'article_feed',
    db.Column('article_id', db.Integer, db.ForeignKey('article.id'), primary_key=True),
    db.Column('feed_id', db.Integer, db.ForeignKey('feed.id'), primary_key=True)
)

feedgroup_feed_association = db.Table(
    'feedgroup_feed',
    db.Column('feedgroup_id', db.Integer, db.ForeignKey('feedgroup.id'), primary_key=True),
    db.Column('feed_id', db.Integer, db.ForeignKey('feed.id'), primary_key=True)
)

class FeedGroup(db.Model):
    __tablename__ = 'feedgroup'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    public = db.Column(db.Boolean, default=False)

    feeds = db.relationship('Feed', secondary=feedgroup_feed_association, back_populates='feedgroups')

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    active_group = db.Column(db.Integer)

    feedgroups = db.relationship('FeedGroup')

class Article(db.Model):
    __tablename__ = 'article'
    
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(1000), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    published_date = db.Column(db.DateTime, default=func.now())
    img_link = db.Column(db.String(1000), nullable=True)
    summary = db.Column(db.String(10000), nullable=True)

    feeds = db.relationship('Feed', secondary=article_feed_association, back_populates='articles')

class Feed(db.Model):
    __tablename__ = 'feed'
    
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(1000), unique=True)

    articles = db.relationship('Article', secondary=article_feed_association, back_populates='feeds')
    feedgroups = db.relationship('FeedGroup', secondary=feedgroup_feed_association, back_populates='feeds')