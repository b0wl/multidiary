from flask import Flask, render_template, redirect, flash, url_for, request, g, session
from flask_sqlalchemy import SQLAlchemy

from flask_wtf import Form
from wtforms import StringField, BooleanField

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, VARCHAR, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'
    idUsers = Column(Integer, primary_key=True, nullable=False)
    Login = Column(VARCHAR, nullable=False)
    Password = Column(VARCHAR, nullable=False)
    CreationDate = Column(DateTime, nullable=False)

    UserRole = Column(Integer, ForeignKey('Roles.idRoles'), nullable=False)

    NumPosts = Column(Integer, nullable=False, default=0)
    NumComments = Column(Integer, nullable=False, default=0)

    # Python only objects
    posts =relationship("Post", back_populates='author')
    comments =relationship("Comment", back_populates='author')


class Post(Base):
    __tablename__ = 'Posts'
    idPosts = Column(Integer, primary_key=True, nullable=False)
    Content = Column(VARCHAR, nullable=False)
    CreationDate = Column(DateTime, nullable=False)

    Author = Column(Integer, ForeignKey('Users.idUsers'), nullable=False)
    # object of type User with id = Author
    author = relationship("User", back_populates="posts")

    NumComments = Column(Integer, nullable=False, default=0)
    comments =relationship("Comment", back_populates='parent')


class Comment(Base):
    __tablename__ = 'Comments'
    idComments = Column(Integer, primary_key=True, nullable=False)
    Content = Column(VARCHAR, nullable=False)
    CreationDate = Column(DateTime, nullable=False)

    Author = Column(Integer, ForeignKey('Users.idUsers'), nullable=False)
    author = relationship("User", back_populates="comments")

    ParentPost = Column(Integer, ForeignKey('Posts.idPosts'), nullable=False)
    parent = relationship("Post", back_populates="comments")


class Role(Base):
    __tablename__ = 'Roles'
    idRoles = Column(Integer, primary_key=True, nullable=False)
    RoleName = Column(VARCHAR, nullable=False)


app = Flask('wieloblog')
app.config.from_object('config')
db = SQLAlchemy(app)


class NewContentForm(Form):
    author = StringField('author')
    content = StringField('content')


class LoginForm(Form):
    login = StringField('Login')
    password = StringField('Password')


class RegisterForm(Form):
    newlogin = StringField('Login')
    newpassword = StringField('Password')
    piotr = BooleanField('Czy szanujesz Piotra? ')


@app.before_request
def before_request():
    if 'user' in session:
        user = db.session.query(User).filter_by(Login=session['user']).one()
    else:
        user = User()
        user.Login = ''

    g.user = user


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LoginForm(request.form)
    form2 = NewContentForm(request.form)
    form3 = RegisterForm(request.form)

    if request.method == 'POST':
        print(form.login.data, form3.newlogin.data)
        if form.login.data:
            login = form.login.data
            password = form.password.data
            try:
                user = db.session.query(User).filter_by(Login=login).one()
            except:
                flash('No user of login {}!'.format(login))
            else:
                if user.Password == password:
                    session["user"] = user.Login
                    flash('Logged in as {}'.format(user.Login))
                else:
                    flash('Incorrect password for user {}. Correct password is {}.'.format(login, user.Password))
        elif form2.content.data:
            new_post = Post(Content=form2.content.data, CreationDate=datetime.utcnow(),
                            Author=g.user.idUsers)
            db.session.add(new_post)
            db.session.commit()
            flash('Post added!')
        elif form3.newlogin.data:
            new_user = User(Login=form3.newlogin.data, CreationDate=datetime.utcnow(),
                            Password=form3.newpassword.data, UserRole=1)
            db.session.add(new_user)
            db.session.commit()
            flash('User added!')

        return redirect(url_for('index'))

    posts = db.session.query(Post).order_by(Post.CreationDate.desc()).all()

    for post in posts:
        if len(post.Content.split(' ')) > 7:
            post.brief_content = ' '.join(post.Content.split(' ')[:7])+'...'
        else:
            post.brief_content = post.Content

    return render_template('main.html', posts=posts, form=form, form2=form2, form3=form3)


@app.route('/logout_handle', methods=['GET'])
def logout_handle():
    del(session['user'])
    flash('Logged out')
    return redirect(url_for('index'))


@app.route('/user/<string:Login>')
def user(Login):
    user = db.session.query(User).filter_by(Login=Login).one()
    status = db.session.query(Role).filter_by(idRoles=user.UserRole).one()
    posts = user.posts
    comments = user.comments

    for comment in comments:
        comment.parent_content = comment.parent.Content

    return render_template('user.html', user=user, status=status.RoleName, posts=posts, comments=comments)




@app.route('/post/<string:idPost>', methods=['GET', 'POST'])
def post(idPost):

    post = db.session.query(Post).filter_by(idPosts=idPost).one()
    comments = post.comments

    form = NewContentForm(request.form)
    if request.method == 'POST':
        author = g.user

        new_comment = Comment(Content=form.content.data, CreationDate=datetime.utcnow(),
                              Author=author.idUsers, ParentPost=post.idPosts)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added!')
        return redirect(url_for('post', idPost=idPost))

    if len(post.Content) > 15:
        post.title = post.Content[:15]+'...'
    else:
        post.title = post.Content

    return render_template('post.html',
                           title=post.title,
                           post=post,
                           comments=comments,
                           form=form)


app.run(host='localhost', port=8080, debug=True)
