from flask import Blueprint, render_template, request, flash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        data = request.form
        print(data)
    return render_template('login.html', name="Sebastian")

@auth.route('logout')
def logout():
    return 'logout'

@auth.route('/sign-up', methods=['GET','POST'])
def sign_up():
    if request.method == 'POST':    
        name = request.form.get('firstName')
        email = request.form.get('email')
        password_1 = request.form.get('password1')
        password_2 = request.form.get('password2')
        if password_1 != password_2:
            flash("Passwords must match", category='error')
    return render_template('sign_up.html')