"""
蓝图是一种组织相关视图和其它代码的方式,与把视图及其它代码直接注册到应用的方式不同,蓝图方式是把他们注册到蓝图,然后在工厂函数中把蓝图注册到应用.
flask有两个蓝图,一个用于认证功能,另一个用于博客帖子管理
认证蓝图
"""
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# 这里创建了一个名称为 'auth' 的 Blueprint 。
# 和应用对象一样， 蓝图需要知道是在哪里定义的，因此把 __name__ 作为函数的第二个参数。 url_prefix 会添加到所有与该蓝图关联的 URL 前面。
bp = Blueprint('auth', __name__, url_prefix='/auth')


# 用户提交表单时，视图会验证表单内容，然后要么再次 显示表单并显示一个出错信息，要么创建新用户并显示登录页面。
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # request.form 是一个特殊类型的 dict ，其映射了提交表单的键和值。表单中，用户将会输入其 username 和 password 。
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))  # 数据保存后将转到登录页面。 url_for() 根据登录视图的名称生成相应的 URL
            # redirect() 为生成的 URL 生成一个重定向响应。
        # 如果验证失败，那么会向用户显示一个出错信息。 flash() 用于储存在渲染模块时可以调用的信息。
        flash(error)
    # 户最初访问 auth/register 时，或者注册出错时，应用显示一个注册 表单。 render_template() 会渲染一个包含 HTML 的模板
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()  # 一个数据库连接
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        # fetchone() 根据查询返回一个记录行。 如果查询没有结果，则返回 None 。后面还用到 fetchall() ，它返回包括所有结果的列表。

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        # session 是一个 dict ，它用于储存横跨请求的值。当验证 成功后，用户的 id 被储存于一个新的会话中。
        # 会话数据被储存到一个 向浏览器发送的 cookie 中，在后继请求中，浏览器会返回它。 Flask 会安全对数据进行 签名 以防数据被篡改。
        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
# bp.before_app_request() 注册一个 在视图函数之前运行的函数，不论其 URL 是什么。 load_logged_in_user 检查用户 id 是否已经储存在 session 中，
# 并从数据库中获取用户数据，然后储存在 g.user 中。 g.user 的持续时间比请求要长。 如果没有用户 id ，或者 id 不存在，那么 g.user 将会是 None 。


@bp.route('/logout')  # 注销的时候需要把用户 id 从 session 中移除。 然后 load_logged_in_user 就不会在后继请求中载入用户了
def logout():
    session.clear()
    return redirect(url_for('index'))


# 装饰器返回一个新的视图，该视图包含了传递给装饰器的原视图。
# 新的函数检查用户 是否已载入。如果已载入，那么就继续正常执行原视图，否则就重定向到登录页面。 我们会在博客视图中使用这个装饰器。
"""
当我们在写程序时，不确定将来要往函数中传入多少个参数，即可使用可变参数（即不定长参数），用*args,**kwargs表示。
*args称之为Non-keyword Variable Arguments，无关键字参数；
**kwargs称之为keyword Variable Arguments，有关键字参数；
当函数中以列表或者元组的形式传参时，就要使用*args；
当传入字典形式的参数时，就要使用**kwargs。
"""


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
# 当使用蓝图的时候，蓝图的名称会添加到函数名称的前面。上面的 login 函数 的端点为 'auth.login' ，因为它已被加入 'auth' 蓝图中。
        return view(**kwargs)

    return wrapped_view
