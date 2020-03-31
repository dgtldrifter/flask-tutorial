from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse

from app import app, db
from forms.loginForm import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from models.models import User


def hello_world():
    return 'Hello World!'


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'This is a text string...'
        },
        {
            'author': {'username': "Susan"},
            'body': 'This is another text string...'
        }
    ]
    return render_template('index.html', title="Home", posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # checks for if a user already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    # Checks if the user clicked submit
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        # generic redirect back to whatever page the user came from
        # if the user was automatically redirected to login if they
        # weren't originally signed in
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Congrats, your information has been registered!')

        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test Post #1'},
        {'author': user, 'body': 'Test Post #2'}
    ]

    return render_template('user.html', user=user, posts=posts)
