from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
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
    user_id = session['user_id']
    list_name = request.args.get('list_name', '我的最愛').strip()
    
    # 獲取所有清單名稱 (為確保至少有預設的 '我的最愛')
    user_lists = Favorite.get_user_lists(user_id)
    
    # 若指定的清單名稱不在使用者清單中，預設選取第一個清單
    if list_name not in user_lists and user_lists:
        list_name = user_lists[0]

    # 獲取該清單內所有的收藏紀錄
    favorites = Favorite.get_user_favorites(user_id, list_name)

    return render_template(
        'favorite/list.html',
        favorites=favorites,
        user_lists=user_lists,
        current_list=list_name
    )

@favorite_bp.route('/toggle/<int:restaurant_id>', methods=['POST'])
@login_required
def toggle_favorite(restaurant_id):
    """
    切換餐廳收藏狀態 (AJAX)
    - POST: 驗證使用者登入狀態，接收 list_name 參數 (預設為 '我的最愛')，
            呼叫 Favorite.toggle 加入或取消該餐廳收藏，並回傳 JSON 結果。
    """
    restaurant = Restaurant.get_by_id(restaurant_id)
    if not restaurant:
        return jsonify({'success': False, 'message': '找不到該餐廳。'}), 404

    # 支援 JSON 或是傳統 Form POST 傳入的 list_name
    list_name = '我的最愛'
    if request.is_json:
        data = request.get_json() or {}
        list_name = data.get('list_name', '我的最愛')
    else:
        list_name = request.form.get('list_name', '我的最愛')

    list_name = list_name.strip()
    if not list_name:
        list_name = '我的最愛'

    try:
        favorited = Favorite.toggle(user_id=session['user_id'], restaurant_id=restaurant_id, list_name=list_name)
        message = '已加入收藏！' if favorited else '已取消收藏。'
        return jsonify({
            'success': True,
            'favorited': favorited,
            'message': message
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@favorite_bp.route('/list/create', methods=['POST'])
@login_required
def create_custom_list():
    """
    建立新自訂口袋名單並收藏餐廳
    - POST: 驗證使用者登入狀態，接收 restaurant_id 與自訂的 list_name，
            呼叫 Favorite.create_custom_list 建立收藏紀錄，並重導向回個人收藏頁或原請求頁。
    """
    restaurant_id_str = request.form.get('restaurant_id')
    list_name = request.form.get('list_name', '').strip()

    if not restaurant_id_str or not list_name:
        flash('餐廳與清單名稱不可為空。', 'danger')
        return redirect(url_for('favorite.list_favorites'))

    try:
        restaurant_id = int(restaurant_id_str)
    except ValueError:
        abort(400)

    restaurant = Restaurant.get_by_id(restaurant_id)
    if not restaurant:
        abort(404)

    try:
        Favorite.create_custom_list(
            user_id=session['user_id'],
            restaurant_id=restaurant_id,
            list_name=list_name
        )
        flash(f'已成功將「{restaurant.name}」加入自訂口袋名單「{list_name}」！', 'success')
    except Exception as e:
        flash(f'建立自訂口袋名單失敗：{str(e)}', 'danger')

    # 回到我的口袋名單專區，並顯示該新清單
    return redirect(url_for('favorite.list_favorites', list_name=list_name))
