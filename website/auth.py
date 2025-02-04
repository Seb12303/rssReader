from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import models, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
            return redirect(url_for('feeds.feed'))
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')

        user = models.User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                #flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('feeds.feed'))
            else:
                flash('Incorrect password', category='error')
        else:
            flash('Email does not exist', category='error')
    return render_template('login.html', user=current_user)

@auth.route('logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':
        if current_user.is_authenticated:
            return redirect(url_for('feeds.feed'))
        first_name = request.form.get('firstName')
        email = request.form.get('email')
        password_1 = request.form.get('password1')
        password_2 = request.form.get('password2')

        user = models.User.query.filter_by(email=email).first()
        if user:
            flash('Email already registred',category='error')
        elif password_1 != password_2:
            flash("Passwords must match", category='error')
        elif len(first_name) < 2:
            flash("Name must be atleast 2 charaters", category='error')
        elif len(password_1) < 8:
            flash('Password must be 8 or more charaters', category='error')
        else:
            new_user = models.User(email=email, first_name=first_name, password=generate_password_hash(password_1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            #flash("Account created!", category='success')
            return redirect(url_for('views.home'))
    return render_template('sign_up.html', user=current_user)