from datetime import datetime
from app.models import db

# 餐廳與標籤的多對多關聯表
restaurant_tags = db.Table('restaurant_tags',
    db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurants.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    opening_hours = db.Column(db.String(100), nullable=True)
    landmark = db.Column(db.String(50), nullable=False, index=True) # 如：正門、東門、西門、便當街
    avg_rating = db.Column(db.Float, nullable=False, default=0.0)    # 平均美味星等
    avg_cp = db.Column(db.Float, nullable=False, default=0.0)        # 平均 CP 值
    latitude = db.Column(db.Float, nullable=True)                    # 緯度
    longitude = db.Column(db.Float, nullable=True)                   # 經度
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 關聯關係
    tags = db.relationship('Tag', secondary=restaurant_tags, backref=db.backref('restaurants', lazy='dynamic'))
    reviews = db.relationship('Review', backref='restaurant', lazy=True, cascade="all, delete-orphan")
    favorites = db.relationship('Favorite', backref='restaurant', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Restaurant {self.name}>'

    # --- CRUD & Filter Helper Methods ---
    @classmethod
    def create(cls, name, address, phone=None, opening_hours=None, landmark=None, tag_names=None, latitude=None, longitude=None):
        """建立餐廳資料，可選傳入標籤名稱列表與經緯度"""
        restaurant = cls(
            name=name,
            address=address,
            phone=phone,
            opening_hours=opening_hours,
            landmark=landmark,
            latitude=latitude,
            longitude=longitude
        )
        if tag_names:
            for t_name in tag_names:
                tag = Tag.get_or_create(t_name)
                restaurant.tags.append(tag)

        db.session.add(restaurant)
        db.session.commit()
        return restaurant

    @classmethod
    def get_by_id(cls, restaurant_id):
        """依據 ID 取得餐廳"""
        return cls.query.get(restaurant_id)

    @classmethod
    def get_all(cls, landmark=None, tag_names=None, query=None):
        """取得符合條件的餐廳列表 (支援關鍵字搜尋、地理位置篩選、多選痛點標籤篩選)"""
        q = cls.query
        
        # 關鍵字搜尋 (名稱或地址)
        if query:
            q = q.filter(db.or_(cls.name.like(f"%{query}%"), cls.address.like(f"%{query}%")))
            
        # 地理地標篩選
        if landmark:
            q = q.filter_by(landmark=landmark)
            
        # 多選痛點標籤篩選 (必須同時擁有所有指定的標籤)
        if tag_names:
            for t_name in tag_names:
                q = q.filter(cls.tags.any(Tag.name == t_name))
                
        return q.all()

    def update(self, name=None, address=None, phone=None, opening_hours=None, landmark=None, tag_names=None, latitude=None, longitude=None):
        """更新餐廳資料與標籤關係"""
        if name:
            self.name = name
        if address:
            self.address = address
        if phone is not None:
            self.phone = phone
        if opening_hours is not None:
            self.opening_hours = opening_hours
        if landmark:
            self.landmark = landmark
        if latitude is not None:
            self.latitude = latitude
        if longitude is not None:
            self.longitude = longitude
            
        if tag_names is not None:
            # 清空舊標籤，重新綁定新標籤
            self.tags.clear()
            for t_name in tag_names:
                tag = Tag.get_or_create(t_name)
                self.tags.append(tag)

        db.session.commit()
        return self

    @classmethod
    def update_averages(cls, restaurant_id):
        """重新計算該餐廳評論的平均美味度 (avg_rating) 與 CP 值 (avg_cp)"""
        from app.models.review import Review
        restaurant = cls.get_by_id(restaurant_id)
        if not restaurant:
            return None
            
        # 查詢所有該餐廳評論的評分
        reviews = Review.query.filter_by(restaurant_id=restaurant_id).all()
        if not reviews:
            restaurant.avg_rating = 0.0
            restaurant.avg_cp = 0.0
        else:
            total_rating = sum(r.rating for r in reviews)
            total_cp = sum(r.cp_rating for r in reviews)
            count = len(reviews)
            restaurant.avg_rating = round(total_rating / count, 1)
            restaurant.avg_cp = round(total_cp / count, 1)
            
        db.session.commit()
        return restaurant

    def delete(self):
        """刪除餐廳"""
        db.session.delete(self)
        db.session.commit()


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Tag {self.name}>'

    @classmethod
    def get_or_create(cls, name):
        """獲取或新增標籤"""
        tag = cls.query.filter_by(name=name).first()
        if not tag:
            tag = cls(name=name)
            db.session.add(tag)
            db.session.commit()
        return tag

    @classmethod
    def get_all(cls):
        """取得所有標籤"""
        return cls.query.all()
