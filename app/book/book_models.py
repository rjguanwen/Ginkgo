# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/7/30 14:09

""" 图书共享管理相关models """

from app import db
from jieba.analyse.analyzer import ChineseAnalyzer


class Book(db.Model):
    """ 图书模型 """
    # 检索内容，多个字段用逗号分隔
    __searchable__ = ['title', 'author', 'publisher', 'summary']
    # 采用中文分词
    __analyzer__ = ChineseAnalyzer()

    isbn = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    # 书籍名称
    title = db.Column(db.String(120), nullable=False)
    # 作者
    author = db.Column(db.String(120))
    # 出版日期
    pubdate = db.Column(db.String(8))
    # 源标题，国外源标题
    origin_title = db.Column(db.String(140))
    # 装订方式
    binding = db.Column(db.String(32))
    # 总页数
    pages = db.Column(db.Integer)
    # 缩略图
    images_medium = db.Column(db.String(256))
    # 大图
    images_large = db.Column(db.String(256))
    # 出版社名称
    publisher = db.Column(db.String(100))
    # 10位ISBN码
    isbn10 = db.Column(db.String(10))
    # 13位ISBN码
    isbn13 = db.Column(db.String(13))
    # 内容简介
    summary = db.Column(db.String(1024))
    # 录入时间
    timestamp = db.Column(db.DateTime)
    # 推荐书籍
    is_recommendation = db.Column(db.String(1), default='0')
    # 推荐语
    recommendation = db.Column(db.String(1024))
    # 尝试………………
    book_in_lib = db.relationship('Book_Lib', backref='book', lazy='dynamic')

    def to_json(self):
        """ 将book对象转换为json格式数据 """
        book_json = {}
        book_json['isbn'] = self.isbn
        book_json['title'] = self.title
        book_json['author'] = self.author
        book_json['pubdate'] = self.pubdate
        book_json['origin_title'] = self.origin_title
        book_json['binding'] = self.binding
        book_json['pages'] = self.pages
        book_json['images_medium'] = self.images_medium
        book_json['images_large'] = self.images_large
        book_json['publisher'] = self.publisher
        book_json['isbn10'] = self.isbn10
        book_json['isbn13'] = self.isbn13
        book_json['summary'] = self.summary
        book_json['timestamp'] = self.timestamp
        book_json['is_recommendation'] = self.is_recommendation
        book_json['recommendation'] = self.recommendation
        return book_json

    def book_owners(self):
        """ 返回本书籍的拥有信息，按序号倒序排列 """
        return Book_Lib.filter(Book_Lib.isbn == self.isbn).order_by(Book_Lib.book_id.desc())

    def __repr__(self):
        return '<Book %r>' % self.title


class Book_Lib(db.Model):
    """ 用户图书表 """
    book_id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.Integer, db.ForeignKey('book.isbn'), nullable=False)
    user_name = db.Column(db.String(32), db.ForeignKey('user.user_name'))
    borrow_period = db.Column(db.Integer, default=10)
    in_use = db.Column(db.String(1), default='1', nullable=False)
    borrower = db.Column(db.String(32), db.ForeignKey('user.user_name'))
    begin_date = db.Column(db.String(8))
    end_date = db.Column(db.String(8))
    status = db.Column(db.String(2), default='00', nullable=False)
    recommendation = db.Column(db.String(1024))

    def __repr__(self):
        return '<BookLib %r:%r>' % (self.isbn, self.user_name)


class Book_Borrow_Log(db.Model):
    """ 书籍借阅记录 """
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book_lib.book_id'), nullable=False)
    borrower = db.Column(db.String(32), db.ForeignKey('user.user_name'), nullable=False)
    borrow_date = db.Column(db.String(8))
    return_date = db.Column(db.String(8))

