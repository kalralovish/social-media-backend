from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from .database import Base
import datetime

followers = Table('followers', Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id')),
    Column('followed_id', Integer, ForeignKey('users.id'))
)

discussion_hashtag = Table('discussion_hashtag', Base.metadata,
    Column('discussion_id', Integer, ForeignKey('discussions.id')),
    Column('hashtag_id', Integer, ForeignKey('hashtags.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    mobile_no = Column(String(15), unique=True, index=True)
    hashed_password = Column(String(255))
    discussions = relationship("Discussion", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    likes = relationship("Like", back_populates="user")
    comment_likes = relationship("CommentLike", back_populates="user")
    following = relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=backref('followers', lazy='dynamic'), lazy='dynamic')

    def follow(self, user):
        if not self.is_following(user):
            self.following.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        return self.following.filter(followers.c.followed_id == user.id).count() > 0

class Discussion(Base):
    __tablename__ = "discussions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(1000), index=True)
    image = Column(String(255), nullable=True)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    view_count = Column(Integer, default=0)

    user = relationship("User", back_populates="discussions")
    hashtags = relationship("Hashtag", secondary=discussion_hashtag, back_populates="discussions")
    comments = relationship("Comment", back_populates="discussion")
    likes = relationship("Like", back_populates="discussion")

class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)

    discussions = relationship("Discussion", secondary=discussion_hashtag, back_populates="hashtags")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(500))
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    discussion_id = Column(Integer, ForeignKey("discussions.id"))
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)

    user = relationship("User", back_populates="comments")
    discussion = relationship("Discussion", back_populates="comments")
    replies = relationship('Comment', backref=backref('parent', remote_side=[id]))
    likes = relationship('CommentLike', back_populates='comment')

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    discussion_id = Column(Integer, ForeignKey("discussions.id"))

    user = relationship("User", back_populates="likes")
    discussion = relationship("Discussion", back_populates="likes")

class CommentLike(Base):
    __tablename__ = 'comment_likes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    comment_id = Column(Integer, ForeignKey('comments.id'))
    user = relationship('User', back_populates='comment_likes')
    comment = relationship('Comment', back_populates='likes')