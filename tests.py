# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/6/19 16:44

""" 使用unittest构建测试框架 """

import os
import unittest
from datetime import datetime, timedelta
from coverage import coverage
from config import base_dir
from app import app, db
from app.main.models import User
from app.leaf.leaf_models import Post
from app.book.book_models import Book
from app.translate_baidu import *

# 引入converage是为了生成测试覆盖率的报告，但是目前还存在一些问题，没有调试好
cov = coverage(branch=True, omit=['flask/*', 'tests.py'])
cov.start()


class TestCase(unittest.TestCase):
    def setUp(self):
        """ 测试之前执行，进行一些必要的配置 """
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        """ 测试之后执行，重置数据库内容 """
        db.session.remove()
        db.drop_all()

    def test_avatar(self):
        """ 测试头像 """
        u = User(user_name='guanwen', password='1', nickname='关文', email='rjguanwen001@163.com')
        avatar = u.avatar(128)
        expected = 'https://secure.gravatar.com/avatar/5e1f2c7792fea6da8f4e56b899620e5d?d=mm&s=128'
        assert avatar[0:len(expected)] == expected

    def test_make_unique_nickname(self):
        """ 测试昵称唯一方法 """
        u = User(user_name='guanwen', password='1', nickname='关文', email='rjguanwen001@163.com')
        db.session.add(u)
        db.session.commit()
        nickname = User.make_unique_nickname('关文')
        assert nickname != '关文'
        u = User(user_name='susan', password='1', nickname=nickname, email='susan@example.com')
        db.session.add(u)
        db.session.commit()
        nickname2 = User.make_unique_nickname('关文')
        assert nickname2 != '关文'
        assert nickname2 != nickname

    def test_follow(self):
        """ 测试关注 """
        u1 = User(user_name='john', password='1', nickname='john', email='john@example.com')
        u2 = User(user_name='susan', password='1', nickname='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        assert u1.unfollow(u2) == None
        u = u1.follow(u2)
        db.session.add(u)
        db.session.commit()
        assert u1.follow(u2) == None
        assert u1.is_following(u2)
        assert u1.followed.count() == 1
        assert u1.followed.first().nickname == 'susan'
        assert u2.followers.count() == 1
        assert u2.followers.first().nickname == 'john'
        u = u1.unfollow(u2)
        assert u != None
        db.session.add(u)
        db.session.commit()
        assert u1.is_following(u2) == False
        assert u1.followed.count() == 0
        assert u2.followers.count() == 0

    def test_follow_posts(self):
        """ 测试获取关注者文章列表 """
        u1 = User(user_name='john', password='1', nickname='john', email='john@example.com')
        u2 = User(user_name='susan', password='1', nickname='susan', email='susan@example.com')
        u3 = User(user_name='mary', password='1', nickname='mary', email='mary@example.com')
        u4 = User(user_name='david', password='1', nickname='david', email='david@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        # make four posts
        utcnow = datetime.utcnow()
        p1 = Post(body="post from john", author=u1, timestamp=utcnow + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2, timestamp=utcnow + timedelta(seconds=2))
        p3 = Post(body="post from mary", author=u3, timestamp=utcnow + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4, timestamp=utcnow + timedelta(seconds=4))
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.add(p4)
        db.session.commit()
        # setup the followers
        u1.follow(u1)  # john follows himself
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u2)  # susan follows herself
        u2.follow(u3)  # susan follows mary
        u3.follow(u3)  # mary follows herself
        u3.follow(u4)  # mary follows david
        u4.follow(u4)  # david follows himself
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(u4)
        db.session.commit()
        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        assert len(f1) == 3
        assert len(f2) == 2
        assert len(f3) == 2
        assert len(f4) == 1
        assert f1 == [p4, p2, p1]
        assert f2 == [p3, p2]
        assert f3 == [p4, p3]
        assert f4 == [p4]


    def test_translate_by_baidu(self):
        """ 测试翻译服务的调用 """
        text = 'apple'
        from_lang = 'en'
        to_lang = 'zh'
        result = translate_by_baidu(text, from_lang, to_lang)
        assert result == '苹果'
        text = '香蕉'
        from_lang = 'zh'
        to_lang = 'en'
        result = translate_by_baidu(text, from_lang, to_lang)
        assert result == 'Banana'


if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print('测试覆盖率报告：')
    cov.report()
    print("HTML version:" + os.path.join(base_dir, "tmp/coverage/index.html"))
    cov.html_report(directory='tmp/coverage')
    cov.erase()
