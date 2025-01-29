from flask import Blueprint, render_template
from flask_login import login_required, current_user
#kun for learning, brukes i feed
views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html', user=current_user)