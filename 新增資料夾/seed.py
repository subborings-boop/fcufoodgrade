import os
from app import create_app
from app.models import db
from app.models.user import User
from app.models.restaurant import Restaurant, Tag
from app.models.review import Review

def seed_database():
    app = create_app()
    with app.app_context():
        # 清空資料庫
        db.drop_all()
        db.create_all()
        print("資料表已重新建立。")

        # 1. 建立測試使用者 (符合逢甲信箱)
        print("正在建立測試使用者...")
        u1 = User.create(username="小明", email="d1234567@o365.fcu.edu.tw", password="password")
        u2 = User.create(username="小華", email="d7654321@o365.fcu.edu.tw", password="password")
        u3 = User.create(username="美食家", email="t0000001@o365.fcu.edu.tw", password="password")

        # 2. 建立常用標籤
        print("正在建立標籤...")
        t_cheap = Tag.get_or_create("平價")
        t_big = Tag.get_or_create("大份量")
        t_seats = Tag.get_or_create("適合久坐")
        t_plug = Tag.get_or_create("有插座")
        t_group = Tag.get_or_create("適合系聚")

        # 3. 建立餐廳資料
        print("正在建立餐廳...")
        r1 = Restaurant.create(
            name="逢甲溫家地瓜球",
            address="台中市西屯區文華路99-2號",
            phone="0912-345-678",
            opening_hours="16:00 - 01:00 (週二公休)",
            landmark="文華路",
            tag_names=["平價"],
            latitude=24.178652,
            longitude=120.645014
        )

        r2 = Restaurant.create(
            name="激旨燒鳥 (逢甲總店)",
            address="台中市西屯區文華路150巷26號",
            phone="04-2451-8666",
            opening_hours="17:00 - 00:30",
            landmark="西安街",
            tag_names=["適合系聚", "有插座"],
            latitude=24.180479,
            longitude=120.645479
        )

        r3 = Restaurant.create(
            name="刁民酸菜魚 (福星店)",
            address="台中市西屯區福星路459號",
            phone="04-2452-2777",
            opening_hours="11:30 - 02:00",
            landmark="正門",
            tag_names=["適合系聚", "大份量"],
            latitude=24.179374,
            longitude=120.646305
        )

        r4 = Restaurant.create(
            name="校園角落咖啡館",
            address="台中市西屯區文華路100號 (積學堂旁)",
            phone="04-2451-7250",
            opening_hours="08:00 - 21:00",
            landmark="正門",
            tag_names=["適合久坐", "有插座", "平價"],
            latitude=24.179049,
            longitude=120.648041
        )

        # 4. 建立美食評論
        print("正在建立評論...")
        Review.create(
            user_id=u1.id,
            restaurant_id=r1.id,
            content="地瓜球外酥內軟，剛炸好超級香！每次下課來買都要排隊，是平價又好吃的小點心！",
            rating=5,
            cp_rating=5
        )

        Review.create(
            user_id=u2.id,
            restaurant_id=r2.id,
            content="氣氛超級棒的串燒店，很適合和社團組員聚會，有插座可以用電腦，但點餐人很多需要等一下。",
            rating=4,
            cp_rating=3
        )

        Review.create(
            user_id=u3.id,
            restaurant_id=r3.id,
            content="酸菜魚真的很大一盆！大份量沒話說，又酸又辣超級過癮，非常適合帶系上的學弟妹一起來聚餐！",
            rating=5,
            cp_rating=4
        )

        Review.create(
            user_id=u1.id,
            restaurant_id=r4.id,
            content="這家咖啡館就開在積學堂旁邊，非常安靜，座位旁邊都有插座，讀書累了還可以吃片鬆餅，CP 值非常高！",
            rating=4,
            cp_rating=5
        )

        Review.create(
            user_id=u2.id,
            restaurant_id=r4.id,
            content="很適合討論報告的地方，飲料很大杯，但尖峰時間座位比較不好搶。",
            rating=4,
            cp_rating=4
        )

        print("資料庫 Seed 成功！")

if __name__ == '__main__':
    seed_database()
