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


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = NewPostForm(request.form)

    if request.method == 'POST':
        author = db.session.query(User).filter_by(Login=form.author.data).one()

        new_post = Post(Content=form.content.data, CreationDate=datetime.utcnow(),
                        Author=author.idUsers)
        db.session.add(new_post)
        db.session.commit()
        flash('Post added!')
        return redirect(url_for('index'))

    posts = db.session.query(Post).order_by(Post.CreationDate.desc()).all()

    for post in posts:
        if len(post.Content.split(' ')) > 7:
            post.brief_content = ' '.join(post.Content.split(' ')[:7])+'...'
        else:
            post.brief_content = post.Content

    return render_template('main.html', posts=posts, form=form)


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
    author = StringField('author')
    content = StringField('content')


@app.route('/post/<string:idPost>', methods=['GET', 'POST'])
def post(idPost):

    post = db.session.query(Post).filter_by(idPosts=idPost).one()
    comments = post.comments

    form = NewPostForm(request.form)
    if request.method == 'POST':
        author = db.session.query(User).filter_by(Login=form.author.data).one()

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


app.run(host='localhost', port=80, debug=True)
