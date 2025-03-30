from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_apscheduler import APScheduler

db = SQLAlchemy()
DB_NAME = "database.db"
scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'shgorgeoirgoierg'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # Register blueprints
    from .views import views
    from .auth import auth
    from .feeds import feeds
    from .manage import manage
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(feeds, url_prefix='/')
    app.register_blueprint(manage, url_prefix='/')

    # Initialize database
    from . import models
    with app.app_context():
        db.create_all()

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    #Initiate Background task for getting data.
    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    from website.fetch_articles import fetch_articles
    scheduler.init_app(app)
    scheduler.start()

    scheduler.add_job(id='fetcharticles', func=lambda: fetch_articles(app=app), trigger='interval', seconds=20)

    return app
