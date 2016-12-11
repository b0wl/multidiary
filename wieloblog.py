from flask import Flask, render_template, redirect, flash, url_for, request
from flask_sqlalchemy import SQLAlchemy

from flask_wtf import Form
from wtforms import StringField

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


@app.route('/')
@app.route('/index')
def index():

    posts = db.session.query(Post).order_by(Post.CreationDate).all()

    for post in posts:
        post.brief_content = ' '.join(post.Content.split(' ')[:2])

    return render_template('main.html', posts=posts)


@app.route('/user/<string:Login>')
def user(Login):
    user = db.session.query(User).filter_by(Login=Login).one()
    status = db.session.query(Role).filter_by(idRoles=user.UserRole).one()
    posts = user.posts
    comments = user.comments

    for comment in comments:
        comment.parent_content = comment.parent.Content

    return render_template('user.html', user=user, status=status.RoleName, posts=posts, comments=comments)


class NewPostForm(Form):
    content = StringField('content')


@app.route('/say/<string:Login>', methods=['GET', 'POST'])
def say(Login):
    user = db.session.query(User).filter_by(Login=Login).one()

    form = NewPostForm(request.form)
    if request.method == 'POST':
        post = Post(Content=form.content.data, CreationDate=datetime.utcnow(),
                    Author=user.idUsers)
        db.session.add(post)
        db.session.commit()
        flash('Dodano post!')
        return redirect(url_for('say', Login=Login))
    return render_template('say.html',
                           title='You saying what?!',
                           form=form,
                           user=user)



@app.route('/post/<string:idPosts>')
def post(idPosts):

    post = db.session.query(Post).filter_by(idPosts=idPosts).one()
    comments = post.comments

    return render_template('post.html', post=post, comments=comments)


app.run(host='localhost', port=8080, debug=True)
