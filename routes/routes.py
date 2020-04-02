from datetime import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from models.models import User, Post
from forms.loginForm import LoginForm, RegistrationForm
from forms.profileForm import EditProfileForm
from forms.postForm import PostForm


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post Created!')
        return redirect(url_for('index'))
    posts = current_user.followed_posts().all()
    return render_template('index.html', title="Home", posts=posts, form=form)


@app.route('/explore')
@login_required
def explore():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html', title='Explore', posts=posts)


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

    return render_template('auth/login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # checks if a user is already logged in, then redirects to index if True
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    # script that gets triggered when submit is selected, pushes registration information to database
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Congrats, your information has been registered!')

        return redirect(url_for('login'))
    return render_template('auth/register.html', title='Register', form=form)


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

    return render_template('profiles/user.html', user=user, posts=posts)


# Updates the user profile/delivers the edit profile page
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():  # if the submit button gets clicked on the form
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':  # if the request that is being made is using GET
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('profiles/edit_profile.html', title="Edit Profile", form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()  # gets the user one is trying to follow
    if user is None:  # checks if the user exists
        flash('user {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:  # checks if the logged in user is attempting to follow themselves
        flash('You cannot follow youself!')
        return redirect(url_for(user), username=username)

    # push follow to db
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash('You are no longer following {}.'.format(username))
    return redirect(url_for('user', username=username))