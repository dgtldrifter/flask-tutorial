from flask import render_template, flash, redirect, url_for
from app import app
from forms.loginForm import LoginForm
from flask_login import current_user, login_user
from models.models import User


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/index')
def index():
    user = {'username': 'Micheal'}
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
    return render_template('index.html', title="Home", user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))

    return render_template('login.html', title='Sign In', form=form)