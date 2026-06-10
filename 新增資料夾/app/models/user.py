import re
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯關係說明（一對多）
    reviews = db.relationship('Review', backref='author', lazy=True, cascade="all, delete-orphan")
    replies = db.relationship('ReviewReply', backref='author', lazy=True, cascade="all, delete-orphan")
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """將密碼經 Hash 加密儲存"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """驗證輸入的密碼是否與 Hash 一致"""
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_fcu_email(email):
        """驗證是否為逢甲大學的官方信箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@o365\.fcu\.edu\.tw$'
        return bool(re.match(pattern, email))

    # --- CRUD Helper Methods ---
    @classmethod
    def create(cls, username, email, password):
        """建立並儲存新使用者，含信箱格式檢查"""
        if not cls.validate_fcu_email(email):
            raise ValueError("必須使用逢甲大學信箱 (@o365.fcu.edu.tw) 進行註冊。")
        
        # 檢查帳號與信箱是否重複
        if cls.query.filter_by(username=username).first():
            raise ValueError("該使用者名稱已被註冊。")
        if cls.query.filter_by(email=email).first():
            raise ValueError("該電子信箱已被註冊。")

        user = cls(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_by_id(cls, user_id):
        """依據 ID 取得使用者"""
        return cls.query.get(user_id)

    @classmethod
    def get_all(cls):
        """取得所有使用者列表"""
        return cls.query.all()

    def update(self, username=None, email=None, password=None):
        """更新使用者資料"""
        if username:
            existing = User.query.filter_by(username=username).first()
            if existing and existing.id != self.id:
                raise ValueError("該使用者名稱已被他人使用。")
            self.username = username
        if email:
            if not self.validate_fcu_email(email):
                raise ValueError("必須使用逢甲大學信箱 (@o365.fcu.edu.tw)。")
            existing = User.query.filter_by(email=email).first()
            if existing and existing.id != self.id:
                raise ValueError("該電子信箱已被註冊。")
            self.email = email
        if password:
            self.set_password(password)
        
        db.session.commit()
        return self

    def delete(self):
        """刪除目前使用者"""
        db.session.delete(self)
        db.session.commit()
