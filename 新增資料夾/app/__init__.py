import os
from flask import Flask
from app.models import db

def create_app(test_config=None):
    """
    Flask 應用程式工廠 (App Factory)
    """
    app = Flask(__name__, instance_relative_config=True)

    # 預設配置
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_secret_key_987654321_fcu'),
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(app.instance_path, 'database.db')}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config is None:
        # 載入 config.py 中的配置 (若有存在的話)
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # 確保 instance 目錄存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 初始化 SQLAlchemy 實例
    db.init_app(app)

    # 註冊 Blueprints 路由
    from app.routes.auth import auth_bp
    from app.routes.restaurant import restaurant_bp
    from app.routes.review import review_bp
    from app.routes.favorite import favorite_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(restaurant_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(favorite_bp)

    # 建立 CLI 指令: flask init-db
    @app.cli.command('init-db')
    def init_db_command():
        """清除舊資料並建立所有 SQLAlchemy 模型所對應的資料表"""
        db.create_all()
        print("資料庫已成功初始化。")

    return app

def init_db():
    """
    提供外部 Python 腳本直接呼叫初始化資料庫 (例如步驟五腳本)
    """
    app = create_app()
    with app.app_context():
        db.create_all()
        print("資料庫已成功初始化 (via init_db)。")
