from flask import Blueprint, render_template, request
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from website.timezoneConverter import time_since

feeds = Blueprint('feeds', __name__)

@feeds.route('/feed')
def feed():
    links=['https://www.vg.no/rss/feed','https://www.theverge.com/rss/index.xml','https://www.nrk.no/toppsaker.rss','https://www.tv2.no/rss/nyheter','https://www.theguardian.com/us/rss']
    articles = get_articles(links)
    user_timezone = request.args.get('timezone', 'UTC')

    return render_template('feed.html', artikler=articles, hentBilde=hentBilde, hentSummary=hentSummary, hentDomain=hentDomain, hentTid=hentTid, user_timezone=user_timezone)

@feeds.route('/manage')
def manageFeed():
    return render_template('manage.html')

def get_articles(links):

    articles = []
    for link in links:
        feed = feedparser.parse(link)
        for article in feed['entries']:
            try:
                article['link']
                article['published_parsed']
                articles.append(article)
            except:
                print("Bad article, no link")
    return sorted(articles, key=lambda hl: hl.get('published_parsed', None), reverse=True)
#returnerer "" hvis det ikke finnes bilde, eller bildeurl hvis det er bilde.
def hentBilde(artikkel):
    url=""
    #youtube (må før nrk) if url =="" er her egentlig unødvendig, men hvis disse blokkene skal flyttes senere er det greit å ha.
    if url == "":
        try:
            url = artikkel.media_thumbnail[0]['url']
        except:
            pass
    #nrk rss
    if url == "":
        try:
            url = artikkel.media_content[-1]['url']
        except:
            pass
    #The Verge rss
    if url == "":
        try:
            soup = BeautifulSoup(artikkel['summary'], "html.parser")
            url = soup.find("img")['src']
            return url
        except:
            pass
    #VG:
    if url == "":
        try:
            links = artikkel['links']
            for x in links:
                if x.type.startswith('img') or x.type.startswith("image"):
                    url = x.href
                    return url
        except:
            pass

    return url
def hentSummary(artikkel):
    try:
        basic = artikkel.summary
        soup = BeautifulSoup(basic, "html.parser")
        summary = soup.getText()
        return summary
    except:
        pass
    return ""
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
    return time_since(artikkel.published_parsed, tid) + " siden"
if __name__ == '__main__':
    a = get_articles(['https://www.youtube.com/feeds/videos.xml?channel_id=UCBa659QWEk1AI4Tg--mrJ2A'])
    print(a[0]['published_parsed'])