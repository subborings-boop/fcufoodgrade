import functools
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    """
    驗證使用者是否登入的裝飾器。
    若未登入：
    - AJAX / JSON 請求：回傳 401 狀態碼與 JSON 格式錯誤訊息。
    - 一般頁面請求：閃現提示訊息，並重導向至登入頁面。
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': '請先登入後再進行此操作。'}), 401
            flash('請先登入後再進行此操作。', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    註冊頁面與提交註冊邏輯
    - GET: 渲染註冊表單 templates/auth/register.html。
    - POST: 接收表單欄位 (username, email, password, confirm_password)，
            檢查密碼一致性、信箱正則後綴與唯一性，成功後重導向至登入頁。
    """
    pass

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    登入頁面與提交登入邏輯
    - GET: 渲染登入表單 templates/auth/login.html。
    - POST: 接收並驗證信箱與密碼，驗證成功後將 user_id 與 username 寫入 session，
            並引導重導向至首頁或原請求之 `next` 頁面。
    """
    pass

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    登出邏輯
    - POST: 清空會話 (session.clear())，並重導向至首頁。
    """
    pass
