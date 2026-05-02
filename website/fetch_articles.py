from bs4 import BeautifulSoup
from website.models import *
from website import db
import feedparser
from datetime import datetime
import requests
from website.llm import getCustomScore
from website.cleanArticle import get_clean_text
import re


def hentBilde(artikkel):
    url = ""
    # The Verge rss
    if url == "":
        try:
            soup = BeautifulSoup(artikkel['summary'], "html.parser")
            url = soup.find("img")['src']
            return url
        except:
            pass
    # youtube (must come before nrk)
    if url == "":
        try:
            url = artikkel.media_thumbnail[0]['url']
        except:
            pass
    # nrk rss
    if url == "":
        try:
            url = artikkel.media_content[-1]['url']
        except:
            pass
    # VG
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


def convert_to_html_format(text):
    text = re.sub(r"## (.+)", r"<strong>\1</strong>", text)
    text = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\* (.+)", r"<ul><li>\1</li></ul>", text)
    return text


def createArticle(feed, url, title, published_parsed, img_src=None, summarys=None):
    article = Article(
        link=url,
        title=title,
        published_date=published_parsed
    )
    if img_src is not None:
        article.img_link = img_src
    if summarys is not None:
        article.summary = summarys

    db.session.add(article)
    db.session.commit()

    feed.articles.append(article)
    db.session.commit()
    return article


def compute_article_score(article, scoring_system) -> float | None:
    try:
        text = get_clean_text(article.link)
    except Exception as e:
        print(f"Failed to fetch content for scoring ({article.link}): {e}")
        return None

    for attempt in range(1, 4):
        try:
            return getCustomScore(text, scoring_system.prompt)
        except Exception as e:
            print(f"Scoring attempt {attempt} failed for article {article.id}: {e}")
    return None


def fetch_articles(app):
    with app.app_context():
        try:
            existing_links = {row[0] for row in db.session.query(Article.link).all()}
            for feed in Feed.query.all():
                parsed_feed = feedparser.parse(feed.source)
                for entry in parsed_feed['entries']:
                    if entry['link'] in existing_links:
                        continue
                    try:
                        link = entry['link']
                        raw_date = entry.get('published_parsed')
                        published = datetime(*raw_date[:6]) if raw_date else datetime.utcnow()
                        bilde = hentBilde(entry)
                        summary = convert_to_html_format(hentSummary(entry))
                        createArticle(feed, link, entry.title, img_src=bilde, summarys=summary, published_parsed=published)
                        existing_links.add(link)
                    except Exception as e:
                        db.session.rollback()
                        print(f"Failed to process article: {e}")
        except Exception as e:
            db.session.rollback()
            print(f"fetch_articles failed: {e}")


def score_pending_articles(app):
    """For each feedgroup with a scoring system, score the 50 newest unscored articles."""
    with app.app_context():
        feedgroups = FeedGroup.query.filter(FeedGroup.scoring_system_id.isnot(None)).all()
        for feedgroup in feedgroups:
            scoring_system = feedgroup.scoring_system
            if scoring_system is None:
                continue

            # Collect unique articles in this feedgroup, newest first
            seen_ids = set()
            all_articles = []
            for feed in feedgroup.feeds:
                for article in feed.articles:
                    if article.id not in seen_ids:
                        seen_ids.add(article.id)
                        all_articles.append(article)

            all_articles.sort(
                key=lambda a: a.published_date or datetime.min,
                reverse=True
            )

            # Already-scored article IDs for this system
            scored_ids = {
                row[0] for row in db.session.query(ArticleScore.article_id)
                .filter_by(scoring_system_id=scoring_system.id).all()
            }

            # Score the 50 newest that are not yet scored
            to_score = [a for a in all_articles[:50] if a.id not in scored_ids]

            for article in to_score:
                score = compute_article_score(article, scoring_system)
                if score is not None:
                    try:
                        article_score = ArticleScore(
                            article_id=article.id,
                            scoring_system_id=scoring_system.id,
                            score=score
                        )
                        db.session.add(article_score)
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        print(f"Failed to save score for article {article.id}: {e}")


if __name__ == "__main__":
    fetch_articles()
