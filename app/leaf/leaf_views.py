# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/6/12 14:38

""" 视图脚本 """

from datetime import datetime
from flask import Blueprint, render_template, flash, redirect, url_for, g
from flask_login import login_required
from app import db
from .leaf_forms import PostForm
from .leaf_models import Post
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS
from flask_babel import gettext
from langdetect import detect
from app.book.book_models import Book

leaf = Blueprint('leaf', __name__,
                     template_folder='templates',
                     static_folder='static')


@leaf.route('/', methods=['GET', 'POST'])
@leaf.route('/index', methods=['GET', 'POST'])
@leaf.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
# @flask_profiler.profile()
def index(page=1):
    print('----leaf-----index------!')
    form = PostForm()
    if form.validate_on_submit():
        # 猜测文章所用的语言
        language = detect(form.post.data)
        # print('========>>%s,%s' % (language, form.post.data))
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data,
                    timestamp=datetime.utcnow(),
                    author=g.user,
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash(gettext('文章已发布！'))
        return redirect(url_for('leaf.index'))
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template("index.html",
                           title=gettext('首页'),
                           form=form,
                           posts=posts)


@leaf.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('leaf.index'))
    return redirect(url_for('leaf.search_results', query=g.search_form.search.data))


@leaf.route('/search_result/<query>')
@login_required
def search_results(query):
    post_results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    book_results = Book.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    print(book_results)
    return render_template('search_results.html',
                           query=query,
                           results=post_results)


@leaf.route('/del_post/<int:id>')
@login_required
def del_post(id):
    post = Post.query.get(id)
    if post == None:
        flash(gettext("将要删除的文章不存在！"))
        return redirect(url_for('leaf.index'))
    if post.author.user_name != g.user.user_name:
        flash(gettext("您只能删除自己发表的文章！"))
        return redirect(url_for('leaf.index'))
    db.session.delete(post)
    db.session.commit()
    flash(gettext('文章已删除！'))
    return redirect(url_for('leaf.index'))
