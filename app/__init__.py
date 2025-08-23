from flask import Flask
from .config import config
from .extensions import db, migrate, ma

def create_app(config_class=None):
    app = Flask(__name__)
    if config_class is None:
        config_class = config['default']
    elif isinstance(config_class, str):
        config_class = config.get(config_class, config['default'])
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    # 注册蓝本
    from .api import api_v1
    app.register_blueprint(api_v1, url_prefix='/api/v1')

    return app
