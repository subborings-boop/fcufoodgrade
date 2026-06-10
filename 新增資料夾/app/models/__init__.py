from flask_sqlalchemy import SQLAlchemy

# 初始化 SQLAlchemy 實例，由 app/__init__.py 動態綁定
db = SQLAlchemy()

# 匯入各個 Model 類別，便於外部統一匯入，並讓 SQLAlchemy 可以追蹤模型以建立資料表
from app.models.user import User
from app.models.restaurant import Restaurant, Tag
from app.models.review import Review, ReviewLike, ReviewReply
from app.models.favorite import Favorite

__all__ = [
    'db',
    'User',
    'Restaurant',
    'Tag',
    'Review',
    'ReviewLike',
    'ReviewReply',
    'Favorite'
]
