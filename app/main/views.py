# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/6/12 14:38

""" 视图脚本 """

from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g
from flask import jsonify, make_response
from flask_babel import gettext
from flask_login import login_user, logout_user, current_user, login_required
from flask_sqlalchemy import get_debug_queries

from app import app, db, lm
from app.leaf.leaf_forms import SearchForm
from .models import User
from .forms import UserEditForm
from app.main.forms import LoginForm
from app.translate_baidu import translate_by_baidu
from app.locale import get_locale
from app.emails import follower_notification
from config import POSTS_PER_PAGE, DATABASE_QUERY_TIMEOUT

main = Blueprint('main', __name__,
                 template_folder='templates',
                 static_folder='static')


@lm.user_loader
def load_user(user_name):
    return User.query.get(user_name)


@app.before_request
def before_request():
    # print('---main--app.before_request----')
    # 全局变量current_user是被Flask - Login设置的
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()
    # 将语言代码记录到全局变量,供前端使用
    g.locale = get_locale()


@app.after_request
def after_request(response):
    # print('---main--app.after_request----')
    for query in get_debug_queries():
        # get_debug_queries返回请求期间的所有查询列表
        # app.logger.info('==> QUERY:%s\nParameters: %s\nDuration: %fs\nContext: %s\n' % (
        # query.statement, query.parameters, query.duration, query.context))
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning('SLOW QUERY:%s\nParameters: %s\nDuration: %fs\nContext: %s\n' %
                               (query.statement, query.parameters, query.duration, query.context))
    return response


@main.route('/')
def index():
    return redirect(url_for('leaf.index'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    # print('--main----login-----')
    if g.user is not None and g.user.is_authenticated:
        # 如果已认证则进入index页
        return redirect(url_for('leaf.index'))
    form = LoginForm()
    # 如果 validate_on_submit在表单提交请求中被调用，它将会收集所有的数据，对字段进行验证，如果所有的事情都通过的话，
    # 它将会返回True，表示数据都是合法的。
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        user_name = form.user_name.data
        user = User.query.get(user_name)
        if not user:
            flash(gettext('没有该用户，请检查！'))
            return render_template('login.html',
                                   title=gettext('登录'),
                                   form=form)
        password = form.password.data
        if password != user.password:
            flash(gettext('密码错误，请重新输入！'))
            return render_template('login.html',
                                   title=gettext('登录'),
                                   form=form)
        # 登录
        login_user(user, remember=form.remember_me.data)
        next = request.args.get('next')
        return redirect(next or url_for('leaf.index'))
    return render_template('login.html',
                           title=gettext('登录'),
                           form=form)


@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('leaf.index'))


@main.route('/user/<nickname>')
@main.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    # print('nickname:' + nickname)
    # print('username:' + user.user_name)
    if user == None:
        # flash('用户 %s 不存在！' % nickname)
        flash(gettext('用户 %(nickname)s 不存在!', nickname=nickname))
        return redirect(url_for('leaf.index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
                           user=user,
                           posts=posts)


@main.route('/useredit', methods=['GET', 'POST'])
@login_required
# @flask_profiler.profile()
def user_edit():
    form = UserEditForm(g.user.nickname)
    if form.validate_on_submit():
        # if form.validate():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        # 使用gettext实现提示信息的多语言功能
        flash(gettext('用户信息修改成功！'))
        return redirect(url_for('main.user_edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('user_edit.html', form=form)


@main.route('/follow/<nickname>')
@login_required
def follow(nickname):
    """ 关注 """
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash(gettext('用户 %s 不存在！') % nickname)
        return redirect(url_for('leaf.index'))
    if user == g.user:
        flash(gettext('您不能关注自己！'))
        return redirect(url_for('main.user', nickname=nickname))
    # 关注用户
    u = g.user.follow(user)
    if u is None:
        flash(gettext('无法关注 %s !') % nickname)
        return redirect(url_for('main.user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash(gettext('您已关注 %s !') % nickname)
    # 通过邮件通知被关注
    follower_notification(user, g.user)
    return redirect(url_for('main.user', nickname=nickname))


@main.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    """ 取消关注 """
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash(gettext('用户 %s 不存在！') % nickname)
        return redirect(url_for('leaf.index'))
    if user == g.user:
        flash(gettext('不能取消关注自己！'))
        return redirect(url_for('main.user', nickname=nickname))
    # 取消关注
    u = g.user.unfollow(user)
    if u is None:
        flash(gettext('无法取消关注 %s ！') % nickname)
        return redirect(url_for('main.user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash(gettext('您已取消关注 %s !') % nickname)
    return redirect(url_for('main.user', nickname=nickname))


@main.route('/translate', methods=['POST'])
@login_required
def translate():
    """ 翻译服务 """
    return jsonify({
        'text': translate_by_baidu(
            request.form['text'],
            request.form['sourceLang'],
            request.form['destLang']
        )
    })


@app.errorhandler(404)
def internal_error(error):
    # 两种不同的处理方式，一种供rest服务使用，另外一种供页面模块使用
    # return make_response(jsonify({'error': 'Not found'}), 404)
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
