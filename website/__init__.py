from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_apscheduler import APScheduler
from sqlalchemy import inspect, text

db = SQLAlchemy()
DB_NAME = "database.db"
scheduler = APScheduler()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'shgorgeoirgoierg'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .feeds import feeds
    from .manage import manage
    from .scoring import scoring_bp
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(feeds, url_prefix='/')
    app.register_blueprint(manage, url_prefix='/')
    app.register_blueprint(scoring_bp, url_prefix='/')

    from . import models
    with app.app_context():
        db.create_all()
        _run_migrations()
        _ensure_default_scoring_system()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    from website.fetch_articles import fetch_articles, score_pending_articles
    scheduler.init_app(app)
    scheduler.start()
    scheduler.add_job(
        id='fetcharticles',
        func=lambda: fetch_articles(app=app),
        trigger='interval',
        seconds=20,
        max_instances=1,
    )
    scheduler.add_job(
        id='scorearticles',
        func=lambda: score_pending_articles(app=app),
        trigger='interval',
        seconds=300,
        max_instances=1,
    )

    return app


def _run_migrations():
    try:
        inspector = inspect(db.engine)
        cols = [c['name'] for c in inspector.get_columns('feedgroup')]
        if 'scoring_system_id' not in cols:
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE feedgroup ADD COLUMN scoring_system_id INTEGER"))
                conn.commit()
    except Exception as e:
        print(f"Migration warning: {e}")


DEFAULT_PROMPT = (
    "Score this news article from 1 to 10 based on overall importance and newsworthiness. "
    "Consider: impact (how many people affected and how severely), significance (long-term consequences), "
    "timeliness (how breaking or recent), unexpectedness (surprise factor), "
    "prominence (famous or powerful figures involved), conflict (tension or controversy), "
    "human interest (emotional appeal), and clarity (how confirmed the facts are). "
    "Give 10 to globally critical breaking news and 1 to trivial or old local stories."
)

def _ensure_default_scoring_system():
    from website.models import ScoringSystem
    default = ScoringSystem.query.filter_by(is_default=True).first()
    if not default:
        default = ScoringSystem(name="Default", prompt=DEFAULT_PROMPT, owner_id=None, is_default=True)
        db.session.add(default)
        db.session.commit()
    elif not default.prompt:
        default.prompt = DEFAULT_PROMPT
        db.session.commit()
