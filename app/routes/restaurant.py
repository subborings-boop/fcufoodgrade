from flask import Blueprint, render_template, request, abort, session
from app.models.restaurant import Restaurant, Tag
from app.models.review import Review, ReviewLike
from app.models.favorite import Favorite

restaurant_bp = Blueprint('restaurant', __name__)

# 定義常規校園地標列表，便於篩選介面選用
LANDMARKS = ['正門', '東門', '西門', '便當街', '西安街', '文華路']

@restaurant_bp.route('/')
def index():
    """
    美食評論網首頁
    - GET: 載入推薦的餐廳清單 (依據美味評星 avg_rating 與 CP值 avg_cp 排序的前 6 家餐廳)，
           並渲染 templates/restaurant/list.html 作為入口首頁。
    """
    # 預設首頁展示高評分餐廳
    restaurants = Restaurant.query.order_by(Restaurant.avg_rating.desc(), Restaurant.avg_cp.desc()).limit(6).all()
    all_tags = Tag.get_all()
    
    return render_template(
        'restaurant/list.html',
        restaurants=restaurants,
        landmarks=LANDMARKS,
        tags=all_tags,
        current_query='',
        current_landmark='',
        selected_tags=[]
    )

@restaurant_bp.route('/restaurants')
def list_restaurants():
    """
    餐廳列表與篩選頁面
    - GET: 接收 query (關鍵字)、landmark (校園區域地標)、tags (多選痛點標籤陣列)，
           進行複合篩選，並渲染 templates/restaurant/list.html 呈現結果。
    """
    query = request.args.get('query', '').strip()
    landmark = request.args.get('landmark', '').strip()
    # 獲取多重 tags 篩選條件
    selected_tags = request.args.getlist('tags')
    
    # 呼叫 Model 篩選
    restaurants = Restaurant.get_all(landmark=landmark, tag_names=selected_tags, query=query)
    all_tags = Tag.get_all()

    return render_template(
        'restaurant/list.html',
        restaurants=restaurants,
        landmarks=LANDMARKS,
        tags=all_tags,
        current_query=query,
        current_landmark=landmark,
        selected_tags=selected_tags
    )

@restaurant_bp.route('/restaurants/<int:id>')
def detail(id):
    """
    餐廳詳細資訊與評論列表頁面
    - GET: 依據 id 獲取餐廳詳情與所有評論。若餐廳不存在則回傳 404。
           若使用者已登入，檢查其收藏狀態、收藏清單與對每篇評論的按讚狀態，
           傳遞所有相關資料至 templates/restaurant/detail.html。
    """
    restaurant = Restaurant.get_by_id(id)
    if not restaurant:
        abort(404)

    # 獲取該餐廳的所有評論 (依時間倒序)
    reviews = Review.get_by_restaurant(id)

    # 登入狀態下獲取個人化資訊
    is_favorited = False
    liked_review_ids = set()
    user_lists = []
    
    if 'user_id' in session:
        user_id = session['user_id']
        is_favorited = Favorite.is_favorited(user_id, id)
        user_lists = Favorite.get_user_lists(user_id)
        
        # 查詢目前使用者已點讚的評論 ID 集合
        likes = ReviewLike.query.filter_by(user_id=user_id).all()
        liked_review_ids = {like.review_id for like in likes}

    return render_template(
        'restaurant/detail.html',
        restaurant=restaurant,
        reviews=reviews,
        is_favorited=is_favorited,
        liked_review_ids=liked_review_ids,
        user_lists=user_lists
    )
