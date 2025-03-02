from bs4 import BeautifulSoup
from website.models import *
from website import db
import feedparser
from datetime import datetime

def hentBilde(artikkel):
    url=""
    #The Verge rss
    if url == "":
        try:
            soup = BeautifulSoup(artikkel['summary'], "html.parser")
            url = soup.find("img")['src']
            return url
        except:
            pass
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
        #return hentSummaryWeb(artikkel)
        basic = artikkel.summary
        soup = BeautifulSoup(basic, "html.parser")
        summary = soup.getText()
        return summary
    except:
        pass
    return ""

#Terrible naming of summary
def createArticle(feed, url, title, published_parsed, img_src=None, summarys=None):
    article = Article(
        link=url,
        title=title,
        published_date = published_parsed
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


def fetch_articles(app):
    with app.app_context():
            links=[article.link for article in Article.query.all()]
            for feed in Feed.query.all():
                parsed_feed = feedparser.parse(feed.source)
                for article in parsed_feed['entries']:
                    if article['link'] in links:
                        pass
                    else:
                        try:
                            link = article['link']
                            published = datetime(*article['published_parsed'][:6])
                            print(type(published))
                            icon_url = article['iconUrl'] = feed.icon
                            bilde = article['bilde'] = hentBilde(article)
                            createArticle(feed, link, article.title, img_src=bilde, summarys=hentSummary(article), published_parsed=published)
                        except Exception as e:
                            pass
                


if __name__ == "__main__":
    fetch_articles()