from flask import Blueprint, render_template, request, redirect, url_for
from urllib.parse import urlparse
from website.timezoneConverter import time_since
from website.models import *
from flask_login import login_required, current_user
from website.convArticle import convArticle

feeds = Blueprint('feeds', __name__)


@feeds.route('/feed')
def feed():
    ss_param = request.args.get('ss', type=int)  # None=use group default, 0=no scoring, N=system N
    scoring_systems = _available_scoring_systems()

    if current_user.is_authenticated and current_user.active_group:
        group = FeedGroup.query.filter_by(id=current_user.active_group).first()
        if group:
            if ss_param is None:
                active_id = group.scoring_system_id  # feedgroup default
            elif ss_param == 0:
                active_id = None  # explicitly disabled
            else:
                active_id = ss_param
            active_name = next((s.name for s in scoring_systems if s.id == active_id), None)
            articles = get_articles(group.id, active_id)
            return render_template(
                'feed.html',
                artikler=articles,
                hentDomain=hentDomain,
                hentTid=hentTid,
                user=current_user,
                scoring_systems=scoring_systems,
                active_ss_id=active_id,
                active_ss_name=active_name,
                active_group=group,
                scoring_locked=False,
            )

    # Standard view: always lock to the Default scoring system
    default_ss = ScoringSystem.query.filter_by(is_default=True).first()
    active_id = default_ss.id if default_ss else None
    active_name = default_ss.name if default_ss else None
    articles = get_articles(2, active_id)
    return render_template(
        'feed.html',
        artikler=articles,
        hentDomain=hentDomain,
        hentTid=hentTid,
        user=current_user,
        scoring_systems=scoring_systems,
        active_ss_id=active_id,
        active_ss_name=active_name,
        active_group=None,
        scoring_locked=True,
    )


@feeds.route('/cfeed/<int:group_id>', methods=['POST'])
def cfeed(group_id):
    if group_id == 111111111111111111111111111111:
        current_user.active_group = None
    else:
        current_user.active_group = group_id
    db.session.commit()
    return redirect(url_for('feeds.feed'))


def _available_scoring_systems():
    systems = ScoringSystem.query.filter_by(is_default=True).all()
    if current_user.is_authenticated:
        systems += ScoringSystem.query.filter_by(owner_id=current_user.id).all()
    return systems


def get_articles(feed_group_id, scoring_system_id=None):
    feedgroup = FeedGroup.query.filter_by(id=feed_group_id).first()
    if feedgroup is None:
        return []

    score_lookup = {}
    if scoring_system_id:
        rows = (
            db.session.query(ArticleScore.article_id, ArticleScore.score)
            .filter_by(scoring_system_id=scoring_system_id)
            .all()
        )
        score_lookup = {row[0]: row[1] for row in rows}

    seen_ids = set()
    articles = []
    for feed_obj in feedgroup.feeds:
        for article in feed_obj.articles:
            if article.id in seen_ids:
                continue
            seen_ids.add(article.id)
            score = score_lookup.get(article.id)
            converted = convArticle(
                title=article.title,
                link=article.link,
                bilde=article.img_link,
                icon=feed_obj.icon,
                domain=hentDomain(article),
                published_parsed=article.published_date.timetuple() if article.published_date else None,
                summary=article.summary,
                score=score,
            )
            articles.append(converted)

    # Scored articles ranked first (desc score), unscored articles follow
    articles.sort(key=lambda a: (a.score is not None, a.score or 0), reverse=True)
    return articles[:50]


def hentDomain(artikkel):
    try:
        domain_with_www = urlparse(artikkel.link).netloc
        return domain_with_www.replace("www.", "")
    except Exception as e:
        print(f"Error processing article domain: {e}")
        return ""


def hentTid(artikkel, tid):
    return time_since(artikkel.published_parsed, 'Europe/Oslo') + " ago"
