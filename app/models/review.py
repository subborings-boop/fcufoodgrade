from datetime import datetime
from app.models import db

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)       # 美味度 (1-5)
    cp_rating = db.Column(db.Integer, nullable=False)    # CP 值 (1-5)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯關係
    likes = db.relationship('ReviewLike', backref='review_obj', lazy=True, cascade="all, delete-orphan")
    replies = db.relationship('ReviewReply', backref='review_obj', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Review {self.id} for Restaurant {self.restaurant_id}>'

    # --- CRUD Helper Methods ---
    @classmethod
    def create(cls, user_id, restaurant_id, content, rating, cp_rating):
        """新增評論，並自動重新計算餐廳平均評分"""
        if not (1 <= rating <= 5) or not (1 <= cp_rating <= 5):
            raise ValueError("星等評分必須在 1 到 5 之間。")
            
        review = cls(
            user_id=user_id,
            restaurant_id=restaurant_id,
            content=content,
            rating=rating,
            cp_rating=cp_rating
        )
        db.session.add(review)
        db.session.commit()

        # 動態觸約更新餐廳評分快取
        from app.models.restaurant import Restaurant
        Restaurant.update_averages(restaurant_id)
        
        return review

    @classmethod
    def get_by_id(cls, review_id):
        """依據 ID 取得評論"""
        return cls.query.get(review_id)

    @classmethod
    def get_by_restaurant(cls, restaurant_id):
        """依據餐廳 ID 取得所有評論 (依時間倒序排列)"""
        return cls.query.filter_by(restaurant_id=restaurant_id).order_by(cls.created_at.desc()).all()

    def update(self, content=None, rating=None, cp_rating=None):
        """修改評論內容，並重新計算餐廳平均分數"""
        if content:
            self.content = content
        if rating:
            if not (1 <= rating <= 5):
                raise ValueError("美味度評分必須在 1 到 5 之間。")
            self.rating = rating
        if cp_rating:
            if not (1 <= cp_rating <= 5):
                raise ValueError("CP 值評分必須在 1 到 5 之間。")
            self.cp_rating = cp_rating

        db.session.commit()

        # 觸發更新
        from app.models.restaurant import Restaurant
        Restaurant.update_averages(self.restaurant_id)
        return self

    def delete(self):
        """刪除評論，並重新計算餐廳平均分數"""
        restaurant_id = self.restaurant_id
        db.session.delete(self)
        db.session.commit()

        # 觸發更新
        from app.models.restaurant import Restaurant
        Restaurant.update_averages(restaurant_id)


class ReviewLike(db.Model):
    __tablename__ = 'review_likes'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id', ondelete='CASCADE'), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<ReviewLike User {self.user_id} - Review {self.review_id}>'

    # --- CRUD Helper Methods ---
    @classmethod
    def toggle(cls, user_id, review_id):
        """切換按讚狀態 (有用/取消有用)。已按讚則取消，未按讚則按讚。"""
        like = cls.query.filter_by(user_id=user_id, review_id=review_id).first()
        if like:
            db.session.delete(like)
            db.session.commit()
            return False  # 代表已取消按讚
        else:
            like = cls(user_id=user_id, review_id=review_id)
            db.session.add(like)
            db.session.commit()
            return True   # 代表按讚成功

    @classmethod
    def get_like_count(cls, review_id):
        """獲取該評論的按讚總數"""
        return cls.query.filter_by(review_id=review_id).count()

    @classmethod
    def has_liked(cls, user_id, review_id):
        """檢查特定使用者是否已對該評論按讚"""
        return bool(cls.query.filter_by(user_id=user_id, review_id=review_id).first())


class ReviewReply(db.Model):
    __tablename__ = 'review_replies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<ReviewReply {self.id} on Review {self.review_id}>'

    # --- CRUD Helper Methods ---
    @classmethod
    def create(cls, review_id, user_id, content):
        """發表二級回覆"""
        reply = cls(review_id=review_id, user_id=user_id, content=content)
        db.session.add(reply)
        db.session.commit()
        return reply

    def delete(self):
        """刪除回覆"""
        db.session.delete(self)
        db.session.commit()
