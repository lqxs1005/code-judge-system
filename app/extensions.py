from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

# 数据库对象
db = SQLAlchemy()
# 迁移对象
migrate = Migrate()
# Marshmallow对象
ma = Marshmallow()
