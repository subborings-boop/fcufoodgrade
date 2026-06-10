from datetime import datetime
from app.models import db

class Favorite(db.Model):
    __tablename__ = 'favorites'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'restaurant_id', 'list_name', name='uq_user_restaurant_list'),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    list_name = db.Column(db.String(50), nullable=False, default='我的最愛')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Favorite User {self.user_id} - Restaurant {self.restaurant_id} in {self.list_name}>'

    # --- CRUD Helper Methods ---
    @classmethod
    def toggle(cls, user_id, restaurant_id, list_name='我的最愛'):
        """切換收藏狀態。如果已存在，則取消收藏並回傳 False；不存在，則建立收藏並回傳 True。"""
        fav = cls.query.filter_by(user_id=user_id, restaurant_id=restaurant_id, list_name=list_name).first()
        if fav:
            db.session.delete(fav)
            db.session.commit()
            return False  # 取消收藏
        else:
            fav = cls(user_id=user_id, restaurant_id=restaurant_id, list_name=list_name)
            db.session.add(fav)
            db.session.commit()
            return True   # 收藏成功

    @classmethod
    def is_favorited(cls, user_id, restaurant_id, list_name='我的最愛'):
        """判斷使用者是否已將該餐廳加入特定收藏清單"""
        return bool(cls.query.filter_by(user_id=user_id, restaurant_id=restaurant_id, list_name=list_name).first())

    @classmethod
    def get_user_favorites(cls, user_id, list_name=None):
        """獲取該使用者的收藏紀錄。如果指定 list_name，則僅篩選該名單；否則回傳全部。"""
        q = cls.query.filter_by(user_id=user_id)
        if list_name:
            q = q.filter_by(list_name=list_name)
        return q.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_user_lists(cls, user_id):
        """獲取該使用者已建立的自訂收藏清單名稱清單 (以確保至少有「我的最愛」)"""
        results = db.session.query(cls.list_name).filter_by(user_id=user_id).distinct().all()
        lists = [r[0] for r in results]
        if '我的最愛' not in lists:
            lists.insert(0, '我的最愛')
        return lists

    @classmethod
    def create_custom_list(cls, user_id, restaurant_id, list_name):
        """建立自訂名稱的口袋名單收藏紀錄"""
        if not list_name or list_name.strip() == '':
            list_name = '我的最愛'
        
        # 檢查是否已存在
        fav = cls.query.filter_by(user_id=user_id, restaurant_id=restaurant_id, list_name=list_name).first()
        if not fav:
            fav = cls(user_id=user_id, restaurant_id=restaurant_id, list_name=list_name)
            db.session.add(fav)
            db.session.commit()
        return fav

    def delete(self):
        """刪除單筆收藏"""
        db.session.delete(self)
        db.session.commit()
