from bs4 import BeautifulSoup
from website.models import *
from website import db
import feedparser
from datetime import datetime
import requests
from website.summarizeGPT import getSummary as chatSummary
from website.cleanArticle import get_clean_text
import re
import json

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
        basic = artikkel.summary
        soup = BeautifulSoup(basic, "html.parser")
        summary = soup.getText()
        return summary
    except:
        pass
    return ""
def hentSummaryWeb(artikkel):
    try:
        cleaned = get_clean_text(artikkel.link)
        return chatSummary(cleaned)
    except:
        return ""

def convert_to_html_format(text):
    # Konverterer overskrifter (##)
    text = re.sub(r"## (.+)", r"<strong>\1</strong>", text)
    
    # Konverterer argumentene med fet tekst
    text = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", text)
    
    # Konverterer punktlister
    text = re.sub(r"\* (.+)", r"<ul><li>\1</li></ul>", text)
    
    # Returnerer den konverterte HTML-strengen
    return text

def extract_json(text):
    start = text.find('{')  # Find the first occurrence of '{'
    if start == -1:
        return None  # No JSON found

    stack = []
    for i in range(start, len(text)):
        if text[i] == '{':
            stack.append('{')
        elif text[i] == '}':
            stack.pop()
            if not stack:  # Found the matching closing '}'
                return text[start:i+1]
    
    return None  # No valid JSON found

def getScore(artikkel):
    for i in range(1,5):
        try:
            text = hentSummaryWeb(artikkel)
            return text["overall_importance_score"]
        except Exception as e:
            print(e)
    return None

#Terrible naming of summary
def createArticle(feed, url, title, published_parsed, img_src=None, summarys=None, score=None):
    article = Article(
        link=url,
        title=title,
        published_date = published_parsed
    )
    if img_src is not None:
        article.img_link=img_src
    if summarys is not None:
        article.summary=summarys
    if score is not None:
        article.score = score
    
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
                            #Med ai:
                            #createArticle(feed, link, article.title, img_src=bilde, summarys=convert_to_html_format(hentSummary(article)), published_parsed=published, score=getScore(article))
                            #Uten ai:
                            createArticle(feed, link, article.title, img_src=bilde, summarys=convert_to_html_format(hentSummary(article)), published_parsed=published)
                        except Exception as e:
                            pass
                


if __name__ == "__main__":
    fetch_articles()