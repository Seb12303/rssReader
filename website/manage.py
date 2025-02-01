from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from website.models import *
from website import db

manage = Blueprint('manage', __name__)

#routes first!

@manage.route('/manage')
@login_required
def manageFeed():
    return render_template('manage.html', createFeedGroup=createFeedGroup, registerFeedToGroup=registerFeedToGroup, user=current_user)

@manage.route('/add_group', methods=['POST'])
def add_group():
    new_group_name = request.form.get('group_name')
    if new_group_name:
        createFeedGroup(current_user, new_group_name)
    return redirect(url_for('manage.manage'))

@manage.route('/delete_group/<int:group_id>', methods=['POST'])
def delete_group(group_id):
    #Delete group.
    group = FeedGroup.query.filter_by(id=group_id).first()
    db.session.delete(group)
    db.session.commit()
    return redirect(url_for('manage.manageFeed'))


def createFeedGroup(user, groupname):
    feedgroup = FeedGroup(name=groupname, owner=user.id, public=False)
    db.session.add(feedgroup)
    db.session.commit()

#Takes groupID and link to add a link to group
def registerFeedToGroup(groupID, link):
    #Check if group exists before adding feed to group
    group = FeedGroup.query.filter_by(id=groupID).first()
    if group:
        #Check if feed exists
        db_search = Feed.query.filter_by(source=link).first()
        #checks if feed is registered by someone else
        if db_search:
            #search inn group.feeds to if db_search is in
            print("Er feed i gruppe: " + str(is_feed_in_group(group.feeds, db_search)))
            if is_feed_in_group(group.feeds, db_search):
                    flash('feed already in this group', category='error')
            else:
                group.feeds.append(db_search)
                #terribly important commit
                db.session.commit()
        else:
            #creates feed
            feed = Feed(source=link)
            db.session.add(feed)
            db.session.commit()
            #add that feed to feedgroup
            group.feeds.append(feed)
            db.session.commit()
    
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

def is_feed_in_group(feedgroupfeeds, feed):
    print("feedgroup.feeds: " + str(feedgroupfeeds))
    for f in feedgroupfeeds:
        if f.id == feed.id:
            return True
    return False
    
