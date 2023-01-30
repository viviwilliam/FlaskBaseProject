# 创建一个数据库的连接,所有查询和操作都需要通过该连接来执行,完事之后该链接关闭
# 在网络应用中链接往往与请求绑定,在处理请求的某个时刻，连接被创建。在发送响应 之前连接被关闭。

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:  # g独立于每一个请求,用于存储可能多个函数都能用到的数据,把链接存储其中可以多次使用
        g.db = sqlite3.connect(  # 建立数据库连接,链接指向配置中的DATABASE指定的文件
            current_app.config['DATABASE'],  # current_app指向处理请求的flask应用
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # 通过列名来操作数据

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))  # get_db 返回一个数据库连接，用于执行文件中的命令。


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

"""
app.teardown_appcontext() 告诉 Flask 在返回响应后进行清理的时候调用此函数。

app.cli.add_command() 添加一个新的 可以与 flask 一起工作的命令。
"""


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)