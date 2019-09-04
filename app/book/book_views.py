# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/7/27 20:35

"""  """

from flask import Blueprint, jsonify, request, make_response
from config import WECHAT_APP_ID, WECHAT_APP_SECRET, JUHE_ISBN_KEY, BOOK_PER_PAGE
import requests
from .book_models import Book
from app import app, db
import json
from datetime import datetime, timedelta

book = Blueprint('book', __name__)


@book.route('/')
def show():
    return 'book.hello!'


@book.route('/api/user/get_token', methods=['POST'])
def get_token():
    """ 通过微信小程序传入的code，调用微信服务端，获取openid与session_key, 返回openid """
    js_code = request.form['code']
    # print('----get_all_book_list------:code:%s' % js_code)
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code' \
          % (WECHAT_APP_ID, WECHAT_APP_SECRET, js_code)
    # print('----get_all_book_list------:url:%s' % url)
    req = requests.get(url)
    result = req.json()
    session_key = result.get('session_key')
    openid = result.get('openid')
    # print('----get_all_book_list------:session_key:%s' % session_key)
    # print('----get_all_book_list------:openid:%s' % openid)
    return openid


@book.route('/api/user/update_login_log', methods=['GET', 'POST'])
def update_login_log():
    """ 记录用户登录日志，》》》尚未完整实现《《《 """
    token = request.form['token']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    print('----update_login_log------:%s:%s:%s' % (token, latitude, longitude))
    status = {'code': "000", 'note': '保存成功！'}
    return jsonify(status)



@book.route('/api/user/update_user_info', methods=['GET', 'POST'])
def update_user_info():
    """ 修改用户信息，》》》尚未完整实现《《《 """
    nickname = request.form['nickName']
    head = request.form['head']
    gender = request.form['gender']
    city = request.form['city']
    province = request.form['province']
    country = request.form['country']
    language = request.form['language']
    token = request.form['token']
    print('----update_user_info------:%s:%s:%s' % (token, nickname, city))
    status = {'code': "000", 'note': '保存成功！'}
    return jsonify(status)


@book.route('/api/1.0/index/get_init_data', methods=['GET'])
@book.route('/api/1.0/index/get_init_data/<int:page>', methods=['GET'])
def get_index_page_init_data(page=1):
    """ 为小程序首页提供初始化数据，包含推荐书籍列表与全部书籍列表 """
    book_list_page = query_all_book_page(page)
    book_json_page = []
    for book in book_list_page.items:
        book_json_page.append(book.to_json())
    recomend_books = query_recomend_books()
    recomend_books_json = []
    for book in recomend_books:
        recomend_books_json.append(book.to_json())
    runpics = [{'isbn': '9787010009148',
                'url': 'http://open.6api.net/mpic/s5804333.jpg',
                'description': '<div style="background:red">《毛泽东选集》(第1卷)包括了毛泽东同志在中国革命各个时期中的重要著作。</div>'},
               {'isbn': '9787508647357',
                'url': 'http://open.6api.net/lpic/s27814883.jpg',
                'description': '十万年前，地球上至少有六种不同的人，但今日，世界舞台为什么只剩下了我们自己？'}]
    return jsonify({'allBooks': book_json_page, 'recomendBooks': recomend_books_json, 'runpics': runpics})


@book.route('/api/1.0/booklist', methods=['GET'])
@book.route('/api/1.0/booklist/<int:page>', methods=['GET'])
def get_all_book_list(page=1):
    """ 查询数据库中的书籍，并返回json格式的数据 """
    # 到数据库中按页查询书籍
    book_list_page = query_all_book_page(page)
    book_json_page = []
    # 循环书籍列表，将其转换为json数据格式
    for book in book_list_page.items:
        book_json_page.append(book.to_json())
    book_list_return = {'items': book_json_page, 'prev_num': book_list_page.prev_num, 'next_num': book_list_page.next_num}
    return jsonify(book_list_return)


def query_all_book_page(page=1):
    """ 到数据库中按页查询书籍 """
    book_list_page = Book.query.order_by(Book.timestamp.desc()).paginate(page, BOOK_PER_PAGE, False)
    return book_list_page


def query_recomend_books():
    """ 查询推荐的书籍 """
    recomend_books = Book.query.filter_by(is_recommendation='1').order_by(Book.timestamp.desc())
    return recomend_books


@book.route('/api/1.0/book/get_book_info/<isbn>', methods=['GET', 'POST'])
def get_book_info(isbn):
    """ 获取书籍信息，如果数据库中已存在，则返回，否则查询isbn服务，存储到数据库中，并返回 """

    app.logger.info('Book - book_views - get_book_info - start:')
    # 查询数据库中是否已有该书籍
    book = query_book_info(isbn)
    app.logger.info('Book - book_views - get_book_info ------ 1 ------')
    #如果存在，直接返回数据库中的值
    if book is not None:
        app.logger.info('Book - book_views - get_book_info ------ 2 ------')
        return jsonify(book.to_json())
    # 如果不存在，则调用服务查询
    app.logger.info('Book - book_views - get_book_info ------ 3 ------')
    url = 'http://feedback.api.juhe.cn/ISBN?key=%s&sub=%s' % (JUHE_ISBN_KEY, isbn)
    req = requests.get(url)
    result = req.json()
    app.logger.info('Book - book_views - get_book_info ------ 4 ------')
    # print(result)
    # 判断调用是否成功
    error_code = result.get('error_code')
    if error_code != 0:
        app.logger.info('Book - book_views - get_book_info ------ 5 ------')
        # 接口调用出错
        return None
    # 将查询结果存储到数据库
    book_info = result.get('result')
    app.logger.info('Book - book_views - get_book_info ------ 6 ------')
    save_book_info(isbn, book_info)
    app.logger.info('Book - book_views - get_book_info ------ 7 ------')
    # 返回查询结果
    return jsonify(book_info)

def query_book_info(isbn):
    """ 根据传入的isbn码查询书籍信息 """
    book = Book.query.filter_by(isbn=isbn).first()
    return book


def save_book_info(isbn, bookinfo):
    """ 将书籍信息保存到数据库 """
    book = Book(
        isbn=isbn,
        title=bookinfo.get('title'),
        author=bookinfo.get('author'),
        pubdate=bookinfo.get('pubdate'),
        origin_title=bookinfo.get('origin_title'),
        binding=bookinfo.get('binding'),
        pages=bookinfo.get('pages'),
        images_medium=bookinfo.get('images_medium'),
        images_large=bookinfo.get('images_large'),
        publisher=bookinfo.get('publisher'),
        isbn10=bookinfo.get('isbn10'),
        isbn13=bookinfo.get('isbn13'),
        summary=bookinfo.get('summary'),
        # 直接存储转化为本地的时间
        timestamp=datetime.utcnow() + timedelta(hours=8)
    )
    db.session.add(book)
    db.session.commit()
    app.logger.info('Book - save_book_info - end!')


@book.route('/api/1.0/book/tmp_query_book_test/<isbn>', methods=['GET', 'POST'])
def tmp_query_book_test(isbn):
    """ 纯是用来测试………… """
    print(1111)
    book = query_book_info(isbn)
    print(2222)
    print(book)
    print(3333)
    print(book.to_json())
    return jsonify({'status': 1})
