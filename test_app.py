import unittest
import json
from app import create_app, db
from app.models.user import User
from app.models.restaurant import Restaurant, Tag
from app.models.review import Review, ReviewLike

class TestFCUFoodGrade(unittest.TestCase):
    def setUp(self):
        """
        初始化測試環境，使用 SQLite 記憶體資料庫
        """
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': 'testing_secret_key_123',
            'WTF_CSRF_ENABLED': False  # 關閉 CSRF 便於測試
        })
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            # 建立基本測試資料
            self.user = User.create(username="測試生", email="d1112223@mail.fcu.edu.tw", password="password123")
            self.restaurant = Restaurant.create(
                name="測試餐廳",
                address="逢甲路100號",
                phone="04-123456",
                opening_hours="10:00 - 22:00",
                landmark="正門"
            )
            self.tag = Tag.get_or_create("平價")
            self.restaurant.tags.append(self.tag)
            db.session.commit()
            
            # 快取常規 ID
            self.user_id = self.user.id
            self.restaurant_id = self.restaurant.id

    def tearDown(self):
        """
        清理測試環境
        """
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_homepage_and_listing(self):
        """
        1. 測試首頁與餐廳列表讀取 (GET / 和 GET /restaurants)
        """
        # 首頁
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('逢甲美食評論網'.encode('utf-8'), response.data)

        # 餐廳列表
        response = self.client.get('/restaurants')
        self.assertEqual(response.status_code, 200)
        self.assertIn('測試餐廳'.encode('utf-8'), response.data)

        # 地標與標籤過濾
        response = self.client.get('/restaurants?landmark=正門&tags=平價')
        self.assertEqual(response.status_code, 200)
        self.assertIn('測試餐廳'.encode('utf-8'), response.data)

    def test_auth_flow(self):
        """
        2. 測試註冊、登入與登出流程
        """
        # 註冊非法信箱後綴（非逢甲信箱）應被攔截阻擋
        response = self.client.post('/auth/register', data={
            'username': '校外人士',
            'email': 'guest@gmail.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn('必須使用逢甲大學信箱'.encode('utf-8'), response.data)

        # 註冊合法逢甲信箱應成功
        response = self.client.post('/auth/register', data={
            'username': '新同學',
            'email': 'd1234567@mail.fcu.edu.tw',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn('註冊成功，請登入'.encode('utf-8'), response.data)

        # 使用剛註冊的帳號登入
        response = self.client.post('/auth/login', data={
            'email': 'd1234567@mail.fcu.edu.tw',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn('歡迎回來，新同學'.encode('utf-8'), response.data)

        # 登出
        response = self.client.post('/auth/logout', follow_redirects=True)
        self.assertIn('您已成功登出'.encode('utf-8'), response.data)

    def test_review_and_rating_averages(self):
        """
        3. 測試發表食記評論與自動星等平均更新
        """
        # 登入測試帳號
        self.client.post('/auth/login', data={
            'email': 'd1112223@mail.fcu.edu.tw',
            'password': 'password123'
        })

        # 發表第一篇評分 (美味 5, CP值 5)
        response = self.client.post(f'/restaurants/{self.restaurant_id}/reviews', data={
            'content': '便宜又美味，大推！',
            'rating': '5',
            'cp_rating': '5'
        }, follow_redirects=True)
        self.assertIn('您的美食評論已成功發表'.encode('utf-8'), response.data)
        self.assertIn('便宜又美味，大推'.encode('utf-8'), response.data)

        # 驗證資料庫中的餐廳平均分數已被更新
        with self.app.app_context():
            r = Restaurant.get_by_id(self.restaurant_id)
            self.assertEqual(r.avg_rating, 5.0)
            self.assertEqual(r.avg_cp, 5.0)

    def test_like_and_reply_interaction(self):
        """
        4. 測試評論有用按讚 (AJAX) 與二級留言回覆
        """
        # 登入
        self.client.post('/auth/login', data={
            'email': 'd1112223@mail.fcu.edu.tw',
            'password': 'password123'
        })

        # 建立一篇評論
        with self.app.app_context():
            rev = Review.create(
                user_id=self.user_id,
                restaurant_id=self.restaurant_id,
                content="測試內容",
                rating=4,
                cp_rating=4
            )
            review_id = rev.id

        # 點擊「這篇有用」 (AJAX)
        response = self.client.post(f'/reviews/{review_id}/like', headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertTrue(data['liked'])
        self.assertEqual(data['like_count'], 1)

        # 發表二級回覆
        response = self.client.post(f'/reviews/{review_id}/replies', data={
            'content': '真的，認同！'
        }, follow_redirects=True)
        self.assertIn('回覆留言已成功發表'.encode('utf-8'), response.data)
        self.assertIn('真的，認同'.encode('utf-8'), response.data)

    def test_favorites_and_custom_list(self):
        """
        5. 測試加入收藏與建立自訂名單
        """
        # 登入
        self.client.post('/auth/login', data={
            'email': 'd1112223@mail.fcu.edu.tw',
            'password': 'password123'
        })

        # 點擊加入收藏 (AJAX)
        response = self.client.post(f'/favorites/toggle/{self.restaurant_id}', headers={'X-Requested-With': 'XMLHttpRequest'}, json={
            'list_name': '我的最愛'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        self.assertTrue(data['favorited'])

        # 進入個人口袋名單頁面檢查
        response = self.client.get('/favorites')
        self.assertEqual(response.status_code, 200)
        self.assertIn('測試餐廳'.encode('utf-8'), response.data)

        # 建立自訂名單並收藏
        response = self.client.post('/favorites/list/create', data={
            'restaurant_id': str(self.restaurant_id),
            'list_name': '大一聚餐名單'
        }, follow_redirects=True)
        self.assertIn('大一聚餐名單'.encode('utf-8'), response.data)

    def test_create_restaurant_flow(self):
        """
        6. 測試新增店家流程
        """
        # 未登入時造訪，應重新導向至登入頁面
        response = self.client.get('/restaurants/new')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.headers['Location'])

        # 未登入時 POST 提交，應拒絕並重導向
        response = self.client.post('/restaurants/new', data={
            'name': '新店家',
            'address': '逢甲路200號',
            'landmark': '正門'
        })
        self.assertEqual(response.status_code, 302)

        # 登入測試帳號
        self.client.post('/auth/login', data={
            'email': 'd1112223@mail.fcu.edu.tw',
            'password': 'password123'
        })

        # 登入後造訪新增店家頁面應成功
        response = self.client.get('/restaurants/new')
        self.assertEqual(response.status_code, 200)
        self.assertIn('新增逢甲周邊店家'.encode('utf-8'), response.data)

        # 登入後 POST 提交合法資料
        response = self.client.post('/restaurants/new', data={
            'name': '大三元便當',
            'address': '文華路20號',
            'phone': '04-98765432',
            'opening_hours': '11:00 - 20:00',
            'landmark': '文華路',
            'tags': ['平價', '大份量']
        }, follow_redirects=True)
        
        # 驗證是否重導向至新店家的詳細資訊頁，且包含店家資訊
        self.assertIn('大三元便當'.encode('utf-8'), response.data)
        self.assertIn('已成功新增店家「大三元便當」'.encode('utf-8'), response.data)
        self.assertIn('文華路'.encode('utf-8'), response.data)
        self.assertIn('平價'.encode('utf-8'), response.data)
        self.assertIn('大份量'.encode('utf-8'), response.data)

        # POST 提交非法資料 (缺乏必填欄位)
        response = self.client.post('/restaurants/new', data={
            'name': '無效店家',
            'landmark': '正門'
        }, follow_redirects=True)
        self.assertIn('請填寫店家名稱、地址與所在的校區位置。'.encode('utf-8'), response.data)

if __name__ == '__main__':
    unittest.main()
