from . import db
from .models import User, FeedGroup, Feed, Article

# Create a user
user = User(email="test@example.com", password="hashed_password", first_name="John")
db.session.add(user)
db.session.commit()

# Create a feed group
feedgroup = FeedGroup(name="Tech News", owner=user.id, public=True)
db.session.add(feedgroup)
db.session.commit()

# Create a feed
feed = Feed(source="https://example.com/rss")
db.session.add(feed)
db.session.commit()

# Associate feed with feed group
feedgroup.feeds.append(feed)
db.session.commit()

# Create an article
article = Article(
    link="https://example.com/article1",
    title="Breaking Tech News",
    img_link="https://example.com/image.jpg",
    summary="This is a summary of the tech news article."
)
db.session.add(article)
db.session.commit()

# Associate article with feed
feed.articles.append(article)
db.session.commit()

# Verify associations
print(f"User: {user.email} owns FeedGroup: {feedgroup.name}")
print(f"FeedGroup: {feedgroup.name} has Feed: {feed.source}")
print(f"Feed: {feed.source} contains Article: {article.title}")
