# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/6/13 10:18

""" 数据模型脚本 """

from app import db
from jieba.analyse.analyzer import ChineseAnalyzer


class Post(db.Model):
    # 检索内容，多个字段用逗号分隔
    __searchable__ = ['body']
    # 采用中文分词
    __analyzer__ = ChineseAnalyzer()

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_name = db.Column(db.String(32), db.ForeignKey('user.user_name'))
    # 文章所使用的语言
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post %r>' % self.body
