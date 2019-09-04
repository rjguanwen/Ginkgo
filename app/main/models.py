# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/7/31 9:07

""" 公用models """

from hashlib import md5
from app import db
import re
from app.leaf.leaf_models import Post

followers = db.Table('followers',
                     db.Column('follower_id', db.String(32), db.ForeignKey('user.user_name')),
                     db.Column('followed_id', db.String(32), db.ForeignKey('user.user_name'))
                     )


class User(db.Model):
    user_name = db.Column(db.String(32), primary_key=True, index=True, unique=True)
    password = db.Column(db.String(64), nullable=False)
    nickname = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id==user_name),
                               secondaryjoin=(followers.c.followed_id==user_name),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    @property
    def is_authenticated(self):
        # 这个方法应该只返回 True，除非表示用户的对象因为某些原因不允许被认证
        return True

    @property
    def is_active(self):
        # 应该返回 True，除非是用户是无效的，比如因为他们的账号是被禁止
        return True

    @property
    def is_anonymous(self):
        # 应该返回 True，如果是匿名的用户不允许登录系统
        return False

    def get_id(self):
        return self.user_name

    def avatar(self, size):
        return "https://secure.gravatar.com/avatar/%s?d=mm&s=%d" % (md5(self.email.encode('utf-8')).hexdigest(), size)

    def __repr__(self):
        return '<User %r>' % self.nickname

    @staticmethod
    def make_unique_nickname(nickname):
        """ 为重复的昵称选出唯一昵称 """
        if User.query.filter_by(nickname=nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() == None:
                break
            version += 1
        return new_nickname

    @staticmethod
    def make_valid_nickname(nickname):
        """ 转换昵称,去掉各种特殊字符 """
        return re.sub('[^a-zA-Z0-9_\.]', '', nickname)

    def follow(self, user):
        """ 关注 """
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        """ 取消关注 """
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        """ 是否已关注 """
        return self.followed.filter(followers.c.followed_id == user.user_name).count() > 0

    def followed_posts(self):
        """ 返回本用户所关注的用户的文章列表，按时间排序 """
        return Post.query.join(followers, (followers.c.followed_id == Post.user_name))\
            .filter(followers.c.follower_id == self.user_name)\
            .order_by(Post.timestamp.desc())
