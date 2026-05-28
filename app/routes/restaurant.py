from flask import Blueprint, render_template, request, abort, session
from app.models.restaurant import Restaurant, Tag
from app.models.review import Review, ReviewLike
from app.models.favorite import Favorite

restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.route('/')
def index():
    """
    美食評論網首頁
    - GET: 載入推薦或熱門的餐廳清單 (按 avg_rating 排序的熱門餐廳)，
           並渲染 templates/restaurant/list.html 作為入口頁面。
    """
    pass

@restaurant_bp.route('/restaurants')
def list_restaurants():
    """
    餐廳列表與篩選頁面
    - GET: 接收 query (名稱關鍵字)、landmark (區域位置)、tags (多選標籤陣列)，
           呼叫 Restaurant.get_all 取得篩選結果，並渲染 templates/restaurant/list.html。
    """
    pass

@restaurant_bp.route('/restaurants/<int:id>')
def detail(id):
    """
    餐廳詳細資訊與評論列表頁面
    - GET: 依據 id 獲取餐廳詳情與所有評論。若餐廳不存在則回傳 404。
           若使用者已登入，檢查其收藏狀態與對每篇評論的按讚狀態，
           傳遞所有相關資料至 templates/restaurant/detail.html。
    """
    pass
