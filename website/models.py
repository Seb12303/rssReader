#importer fra __init__
from . import db
from flask_login import UserMixin

#get current date and time in sql form
#from sqlalchemy.sql import func, use func.now()

class FeedGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    links = db.Column(db.String(10000))
    owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    public = db.Column(db.Boolean)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    feeds = db.relationship('FeedGroup')

#todo cache articles from feeds
#class articles()
#class feed