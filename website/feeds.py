from flask import Blueprint, render_template, request, redirect, url_for
from urllib.parse import urlparse
from website.timezoneConverter import time_since
from website.models import *
from flask_login import login_required, current_user
from website.convArticle import convArticle

feeds = Blueprint('feeds', __name__)

@feeds.route('/feed')
def feed():
    #If user is logged in, has chosen a specific feedgroup and that feedgroup exists: Show that feedgroup
    if (current_user.is_authenticated) and (current_user.active_group is not None) and (FeedGroup.query.filter_by(id=current_user.active_group).first() is not None):
        #get articles for a feedgroup
        articles = get_articles(current_user.active_group)
        return render_template('feed.html', artikler=articles, hentDomain=hentDomain, hentTid=hentTid, user=current_user)
    #If not then simply show the default feed
    articles = get_articles(2)
    return render_template('feed.html', artikler=articles, hentDomain=hentDomain, hentTid=hentTid, user=current_user)

@feeds.route('/cfeed/<int:group_id>', methods=['POST'])
def cfeed(group_id):
    if group_id == 111111111111111111111111111111:
        current_user.active_group = None
        db.session.commit()
    else:
        current_user.active_group = group_id
        db.session.commit()
    return redirect(url_for('feeds.feed'))

def get_articles(feed_group_id):
    articles=[]
    for feed in FeedGroup.query.filter_by(id=feed_group_id).first().feeds:
        for article in feed.articles[-50:]:
            converted = convArticle(title=article.title, link=article.link, bilde=article.img_link,icon=feed.icon, domain=hentDomain(article), published_parsed=article.published_date.timetuple(), summary=article.summary, score=article.score)
            articles.append(converted)
    #return sorted(articles, key=lambda hl: hl.score if hl.score is not None else -1, reverse=True)
    return sorted(articles, key=lambda hl: hl.published_parsed, reverse=True)

def hentDomain(artikkel):
    try:
        #Tries to get domain name from link in article
        #For some reason needs to be in a try clause after a change in how the articles are gotten fro for loop in jinja
        #Terrible, but cant find a better solution
        domain_with_www = urlparse(artikkel.link).netloc
        domain = domain_with_www.replace("www.", "")
        return domain
    except Exception as e:
        print(f"Error processing article: {e}")
        return ""
def hentTid(artikkel, tid):
    return time_since(artikkel.published_parsed, 'Europe/Oslo') + " siden"

if __name__ == '__main__':
    a = get_articles(['https://www.youtube.com/feeds/videos.xml?channel_id=UCBa659QWEk1AI4Tg--mrJ2A'])
    print(a[0]['published_parsed'])