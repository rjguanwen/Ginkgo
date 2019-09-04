# -*- coding: utf-8 -*-
# Copyright (c) 2017 - zhengbin <rjguanwen001@163.com>
# Create Date: 2018/6/26 9:25

""" 简单的邮件框架 """

from flask_mail import Message
from threading import Thread
from flask import render_template
from app import mail
from app import app
from config import ADMINS
from .decorators import async


@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    """ 发送邮件，采用异步方式发送 """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)
    # 下面两行代码作废,通过装饰器 @async 替代
    # thr = Thread(target=send_async_email, args=[app, msg])
    # thr.start()


def follower_notification(followed, follower):
    send_email("【microblog】 %s 关注了你！" % follower.nickname,
               ADMINS[0],
               [followed.email],
               render_template("follower_email.txt",
                               user=followed,
                               follower=follower),
               render_template("follower_email.html",
                                user=followed,
                                follower=follower))
