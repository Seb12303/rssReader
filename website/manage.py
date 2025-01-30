from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from website.models import *
from website import db

manage = Blueprint('manage', __name__)

@manage.route('/manage')
@login_required
def manageFeed():
    return render_template('manage.html', createFeedGroup=createFeedGroup, registerFeedToGroup=registerFeedToGroup, user=current_user)

def createFeedGroup(user, groupname):
    feedgroup = FeedGroup(name=groupname, owner=user.id, public=False)
    db.session.add(feedgroup)
    db.session.commit()

def registerFeedToGroup(link, group):
# Create a feed
    db_search = Feed.query.filter_by(source=link).first()
    #checks if feed is registered by someone else
    if db_search:
        #search inn group.feeds to if db_search is in
        if is_feed_in_group(group, db_search):
                flash('feed already in this group', category='error')
        else:
            group.feeds.append(db_search)
            print("test")
    else:
        feed = Feed(source=link)
        db.session.add(feed)
        db.session.commit()
        group.feeds.append(feed)
        db.session.commit()
    # Associate feed with feed group
    
#Terrible naming of summary
def createArticle(feed, url, title, img_src=None, summarys=None):
    article = Article(
        link=url,
        title=title
    )
    if img_src is not None:
        article.img_link=img_src
    if summarys is not None:
        article.summary=summarys
    
    db.session.add(article)
    db.session.commit()

    # Associate article with feed
    feed.articles.append(article)
    db.session.commit()
def is_feed_in_group(feedgroup, feed):
    return feed in feedgroup.feeds
