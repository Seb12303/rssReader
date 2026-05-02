from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


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


class ScoringSystem(db.Model):
    __tablename__ = 'scoringsystem'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    # None = use the default weighted multi-criteria algorithm
    prompt = db.Column(db.String(5000), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_default = db.Column(db.Boolean, default=False)

    owner = db.relationship('User', foreign_keys=[owner_id], back_populates='scoring_systems')
    feedgroups = db.relationship(
        'FeedGroup',
        foreign_keys='FeedGroup.scoring_system_id',
        back_populates='scoring_system'
    )
    scores = db.relationship('ArticleScore', back_populates='scoring_system', cascade='all, delete-orphan')


class ArticleScore(db.Model):
    __tablename__ = 'articlescore'

    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), primary_key=True)
    scoring_system_id = db.Column(db.Integer, db.ForeignKey('scoringsystem.id'), primary_key=True)
    score = db.Column(db.Float, nullable=False)

    article = db.relationship('Article', back_populates='scores')
    scoring_system = db.relationship('ScoringSystem', back_populates='scores')


class FeedGroup(db.Model):
    __tablename__ = 'feedgroup'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    public = db.Column(db.Boolean, default=False)
    scoring_system_id = db.Column(db.Integer, db.ForeignKey('scoringsystem.id'), nullable=True)

    feeds = db.relationship('Feed', secondary=feedgroup_feed_association, back_populates='feedgroups')
    scoring_system = db.relationship(
        'ScoringSystem',
        foreign_keys=[scoring_system_id],
        back_populates='feedgroups'
    )


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    active_group = db.Column(db.Integer)
    settings = db.Column(db.String(1000))

    feedgroups = db.relationship('FeedGroup', foreign_keys='FeedGroup.owner')
    scoring_systems = db.relationship(
        'ScoringSystem',
        foreign_keys='ScoringSystem.owner_id',
        back_populates='owner'
    )


class Article(db.Model):
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(1000), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    published_date = db.Column(db.DateTime, default=func.now())
    img_link = db.Column(db.String(1000), nullable=True)
    summary = db.Column(db.String(10000), nullable=True)
    score = db.Column(db.Float, nullable=True)  # legacy column
    feeds = db.relationship('Feed', secondary=article_feed_association, back_populates='articles')
    scores = db.relationship('ArticleScore', back_populates='article', cascade='all, delete-orphan')


class Feed(db.Model):
    __tablename__ = 'feed'

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(1000), unique=True)
    icon = db.Column(db.String(70000))

    articles = db.relationship('Article', secondary=article_feed_association, back_populates='feeds')
    feedgroups = db.relationship('FeedGroup', secondary=feedgroup_feed_association, back_populates='feeds')
