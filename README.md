# Ginkgo
some useful web applications. 


flask-mail对windows支持存在问题,需要使用下面的命令安装
pip install --no-deps lamson chardet flask-mail

国际化功能,通过下面的命令提取程序中需要国际化的部分
pybabel extract -F babel.cfg -o messages.pot app

# 添加英语到我们应用程序的命令:
* pybabel init 命令把 .pot 文件作为输入，生成一个新语言目录，
- 以 -d 选项指定的目录为新语言的目录，
- 以 -l 指定的语言为想要翻译成的语言类型。
pybabel init -i messages.pot -d app/translations -l en

* 一旦文本翻译完成并且保存成 messages.po 文件，
* 还有另外一个命令来发布这些文本
pybabel compile -d app/translations

* 添加新的翻译内容后,升级翻译文件
pybabel extract -F babel.cfg -o messages.pot app
pybabel update -i messages.pot -d app/translations
* 升级完之后编译发布
pybabel compile -d app/translations


* 当使用 lazy_gettext 的时候，pybabel extract 命令需要一个额外的 -k 的选项指明是 lazy_gettext 函数:
pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot app



非常不幸地是，Flask-WhooshAlchemy 这个包在 Python 3 中存在问题。并且 Flask-WhooshAlchemy 不会兼容 Python 3。
国外大神为这个扩展做了一个分支并且做了一些改变以便其兼容 Python 3，因此需要卸载官方的版本并且安装其分支:
$ flask/bin/pip uninstall flask-whooshalchemy
$ flask/bin/pip install git+git://github.com/miguelgrinberg/flask-whooshalchemy.git

