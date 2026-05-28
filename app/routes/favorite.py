from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.routes.auth import login_required
from app.models.favorite import Favorite
from app.models.restaurant import Restaurant

favorite_bp = Blueprint('favorite', __name__, url_prefix='/favorites')

@favorite_bp.route('', methods=['GET'])
@login_required
def list_favorites():
    """
    口袋名單與自訂收藏清單頁面
    - GET: 驗證使用者登入狀態，依據 query 參數 list_name 獲取特定名單內的收藏餐廳，
           載入所有使用者收藏名單清單以顯示分頁頁籤，渲染 templates/favorite/list.html。
    """
    pass

@favorite_bp.route('/toggle/<int:restaurant_id>', methods=['POST'])
@login_required
def toggle_favorite(restaurant_id):
    """
    切換餐廳收藏狀態 (AJAX)
    - POST: 驗證使用者登入狀態，接收 list_name 參數 (預設為 '我的最愛')，
            呼叫 Favorite.toggle 加入或取消該餐廳收藏，並回傳 JSON 結果。
    """
    pass

@favorite_bp.route('/list/create', methods=['POST'])
@login_required
def create_custom_list():
    """
    建立新自訂口袋名單並收藏餐廳
    - POST: 驗證使用者登入狀態，接收 restaurant_id 與自訂的 list_name，
            呼叫 Favorite.create_custom_list 建立收藏紀錄，並重導向回個人收藏頁或原請求頁。
    """
    pass
