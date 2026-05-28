from flask import Blueprint, request, redirect, url_for, flash, session, jsonify
from app.routes.auth import login_required
from app.models.review import Review, ReviewLike, ReviewReply
from app.models.restaurant import Restaurant

review_bp = Blueprint('review', __name__)

@review_bp.route('/restaurants/<int:id>/reviews', methods=['POST'])
@login_required
def create_review(id):
    """
    建立餐廳評論與星等評分
    - POST: 驗證使用者登入狀態，接收 form 表單之 content (評論)、rating (美味度)、cp_rating (CP值)，
            呼叫 Review.create 寫入資料庫並觸發餐廳平均分數更新，
            最後重導向回 /restaurants/<id> 餐廳詳情頁。
    """
    pass

@review_bp.route('/reviews/<int:review_id>/like', methods=['POST'])
@login_required
def toggle_like(review_id):
    """
    切換評論「有用」按讚狀態 (AJAX)
    - POST: 驗證使用者登入狀態，呼叫 ReviewLike.toggle 切換狀態，
            並呼叫 ReviewLike.get_like_count 取得最新按讚總數，回傳 JSON。
    """
    pass

@review_bp.route('/reviews/<int:review_id>/replies', methods=['POST'])
@login_required
def create_reply(review_id):
    """
    建立評論二級回覆留言
    - POST: 驗證使用者登入狀態，接收回覆 content，
            呼叫 ReviewReply.create 建立回覆，並重導向回對應的餐廳詳情頁面。
    """
    pass
