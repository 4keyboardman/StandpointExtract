import os
import logging
from logging import handlers
from flask import Flask
from flask import request


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="dev",
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    log_handler = handlers.TimedRotatingFileHandler('logs/flaskr.log', 'D', 1, 0, encoding='utf-8')
    log_handler.suffix = "%Y-%m-%d"
    log_handler.setLevel('DEBUG')
    fmt = "[%(asctime)-15s] [%(levelname)s] [%(pathname)s.%(funcName)s:%(lineno)d] [%(process)d] - %(message)s"
    datefmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(fmt, datefmt)
    log_handler.setFormatter(formatter)
    app.logger.addHandler(log_handler)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)
    # 请求响应的json字符串返回中文，默认中文会编码成Unicode返回
    app.config['JSON_AS_ASCII'] = False
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/hello")
    def hello():
        return "Hello, World!"

    @app.before_request
    def before_request():
        request_info = {'ip': request.remote_addr,
                        'path': request.path,
                        'form': {k: v for k, v in request.form.items()},
                        'data': repr(request.data),
                        'args': {k: v for k, v in request.args.items()},
                        'headers': {k: v for k, v in request.headers.items()}}
        app.logger.info(request_info)

    # register the database commands
    from flaskr import db

    db.init_app(app)
    with app.app_context():
        db.init_db()

    # apply the blueprints to the app
    from flaskr import auth, blog, extractor_controller

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(extractor_controller.bp)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="index")

    return app
