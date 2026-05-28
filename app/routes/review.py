from flask import Blueprint, request, redirect, url_for, flash, session, jsonify, abort
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
            呼叫 Review.create 寫入資料庫並自動重新計算該餐廳平均分數，最後重導向回餐廳詳情頁。
    """
    restaurant = Restaurant.get_by_id(id)
    if not restaurant:
        abort(404)

    content = request.form.get('content', '').strip()
    rating_str = request.form.get('rating')
    cp_rating_str = request.form.get('cp_rating')

    # 基本欄位檢查
    if not content:
        flash('評論內容不可為空。', 'danger')
        return redirect(url_for('restaurant.detail', id=id))

    if not rating_str or not cp_rating_str:
        flash('請同時為「美味度」與「CP值」進行評分。', 'danger')
        return redirect(url_for('restaurant.detail', id=id))

    try:
        rating = int(rating_str)
        cp_rating = int(cp_rating_str)
        
        # 範圍檢查
        if not (1 <= rating <= 5) or not (1 <= cp_rating <= 5):
            raise ValueError()
    except ValueError:
        flash('評分星等必須介於 1 到 5 之間。', 'danger')
        return redirect(url_for('restaurant.detail', id=id))

    try:
        Review.create(
            user_id=session['user_id'],
            restaurant_id=id,
            content=content,
            rating=rating,
            cp_rating=cp_rating
        )
        flash('您的美食評論已成功發表！', 'success')
    except Exception as e:
        flash(f'發表評論失敗：{str(e)}', 'danger')

    return redirect(url_for('restaurant.detail', id=id))

@review_bp.route('/reviews/<int:review_id>/like', methods=['POST'])
@login_required
def toggle_like(review_id):
    """
    切換評論「有用」按讚狀態 (AJAX)
    - POST: 驗證使用者登入狀態，呼叫 ReviewLike.toggle 切換狀態，
            並呼叫 ReviewLike.get_like_count 取得最新按讚總數，回傳 JSON。
    """
    review = Review.get_by_id(review_id)
    if not review:
        return jsonify({'success': False, 'message': '找不到該評論。'}), 404

    try:
        liked = ReviewLike.toggle(user_id=session['user_id'], review_id=review_id)
        like_count = ReviewLike.get_like_count(review_id)
        return jsonify({
            'success': True,
            'liked': liked,
            'like_count': like_count
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@review_bp.route('/reviews/<int:review_id>/replies', methods=['POST'])
@login_required
def create_reply(review_id):
    """
    建立評論二級回覆留言
    - POST: 驗證使用者登入狀態，接收回覆 content，
            呼叫 ReviewReply.create 建立回覆，並重導向回對應的餐廳詳情頁面。
    """
    review = Review.get_by_id(review_id)
    if not review:
        abort(404)

    content = request.form.get('content', '').strip()
    if not content:
        flash('回覆留言內容不可為空。', 'danger')
        return redirect(url_for('restaurant.detail', id=review.restaurant_id))

    try:
        ReviewReply.create(
            review_id=review_id,
            user_id=session['user_id'],
            content=content
        )
        flash('回覆留言已成功發表！', 'success')
    except Exception as e:
        flash(f'發表回覆失敗：{str(e)}', 'danger')

    return redirect(url_for('restaurant.detail', id=review.restaurant_id))
