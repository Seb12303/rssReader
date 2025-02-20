from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from website.models import *
from website import db
import re
import requests
import bs4
from urllib.parse import urlparse
import base64

manage = Blueprint('manage', __name__)

#routes:

@manage.route('/manage')
@login_required
def manageFeed():
    return render_template('manage.html', createFeedGroup=createFeedGroup, registerFeedToGroup=registerFeedToGroup, prettyUrl=prettyUrl, getFeedIcon=getFeedIcon, user=current_user)

# Groups first
@manage.route('/add_group', methods=['POST'])
def add_group():
    new_group_name = request.form.get('group_name')
    print("test")
    if new_group_name:
        createFeedGroup(current_user, new_group_name)
    return redirect(url_for('manage.manageFeed'))

@manage.route('/delete_group/<int:group_id>', methods=['POST'])
def delete_group(group_id):
    #Delete group.
    group = FeedGroup.query.filter_by(id=group_id).first()
    db.session.delete(group)
    db.session.commit()
    return redirect(url_for('manage.manageFeed'))

@manage.route('/rename_group/<int:group_id>', methods=['POST'])
def rename_group(group_id):
    new_name = request.form.get('new_group_name')
    if new_name:
        group = FeedGroup.query.filter_by(id=group_id).first()
        group.name=new_name
        db.session.commit()
    return redirect(url_for('manage.manageFeed'))


#Then feeds

@manage.route('/add_feed/<int:group_id>', methods=['POST'])
def add_feed(group_id):
    feed_source = request.form.get('feed_source')
    registerFeedToGroup(group_id, feed_source)
    return redirect(url_for('manage.manageFeed'))

@manage.route('/remove_feed/<int:group_id>/<int:feed_id>', methods=['POST'])
def remove_feed(group_id, feed_id):
    group = FeedGroup.query.filter_by(id=group_id).first()
    feed = Feed.query.filter_by(id=feed_id).first()
    group.feeds.remove(feed)
    db.session.commit()
    return redirect(url_for('manage.manageFeed'))


def createFeedGroup(user, groupname):
    feedgroup = FeedGroup(name=groupname, owner=user.id, public=False)
    db.session.add(feedgroup)
    db.session.commit()

#Takes groupID and link to add a link to group
def registerFeedToGroup(groupID, link):
    if link.startswith('https://') or link.startswith('http://'):
        pass
    else:
        link = "https://" + link
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
    
def prettyUrl(url):
    #stjålet :( ikke bra
    if url.startswith('http'):
        url = re.sub(r'https?://', '', url)  # Corrected regex
    if url.startswith('www.'):
        url = re.sub(r'www\.', '', url)  # Escape dot properly
    return url

def getFeedIcon(url):
    try:
        icon_link = requests.get("https://" + urlparse(url).netloc + '/favicon.ico').content
        icon_link = base64.b64encode(icon_link).decode('utf-8')
        icon_link = f"data:image/x-icon;base64,{icon_link}"
        return icon_link
    except:
        return None