import os
from flask import Flask
from . import test2
from . import cv_test


def create_app(test_config=None):
    app = Flask(__name__,instance_relative_config=True)#创建flask实例,
    app.config.from_mapping(#设置应用的缺省(默认)配置
        SECRET_KEY='dev',#发布时候保证数据安全的
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),#数据库文件存放的路径
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)# 利用config.py 中的值来重载缺省配置，如果 config.py 存在的话
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)#实现测试和开发的配置分离

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)#确保保存SQLite数据库文件的实例文件夹存在
    except OSError:
        pass

    # a simple page that says hello 创建路由
    @app.route('/hello')
    def hello():
        print("2222222222")
        test2.test()
        cv_test.test()
        return 'Hello, World!'

    from . import db
    db.init_app(app)
#使用 app.register_blueprint() 导入并注册 蓝图。新的代码放在工厂函数的尾部返回应用之前
    from . import auth
    app.register_blueprint(auth.bp)
# 下文的 index 视图的端点会被定义为 blog.index 。一些验证视图 会指定向普通的 index 端点。
# 我们使用 app.add_url_rule() 关联端点名称 'index' 和 / URL ，
# 这样 url_for('index') 或 url_for('blog.index') 都会有效，会生成同样的 / URL 。

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
