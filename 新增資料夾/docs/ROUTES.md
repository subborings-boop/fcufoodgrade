# 路由與頁面設計文件 (ROUTES.md) - 逢甲美食評論網

本文件詳細規劃「逢甲美食評論網」的 Flask 路由端點（Endpoints）、各頁面對應之 HTTP 方法、Jinja2 模板以及輸入/輸出邏輯，並提供對應的路由骨架定義，作為後續實作 Controller 層的準則。

---

## 1. 路由總覽表格

| 功能模組 | 功能 | HTTP 方法 | URL 路徑 | 對應模板 / 回傳值 | 說明 | 權限要求 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **首頁與瀏覽** | 首頁 (熱門與推薦) | `GET` | `/` | `restaurant/list.html` | 展示網站首頁與精選推薦餐廳 | 訪客 / 學生 |
| **會員管理** | 註冊頁面 | `GET` | `/auth/register` | `auth/register.html` | 顯示逢甲信箱註冊表單 | 訪客 |
| | 提交註冊資料 | `POST` | `/auth/register` | — (重導向 `/auth/login`) | 驗證信箱並建立使用者帳號 | 訪客 |
| | 登入頁面 | `GET` | `/auth/login` | `auth/login.html` | 顯示登入表單 | 訪客 |
| | 提交登入憑證 | `POST` | `/auth/login` | — (重導向 `/` 或來源頁) | 驗證密碼並記錄 Session 狀態 | 訪客 |
| | 登出 | `POST` | `/auth/logout` | — (重導向 `/`) | 清除 Session 登入狀態 | 學生 (已登入) |
| **餐廳管理** | 餐廳列表與搜尋 | `GET` | `/restaurants` | `restaurant/list.html` | 餐廳列表頁，支援搜尋與多標籤篩選 | 訪客 / 學生 |
| | 餐廳詳情 | `GET` | `/restaurants/<int:id>` | `restaurant/detail.html` | 顯示餐廳詳細資訊與評論列表 | 訪客 / 學生 |
| **評論互動** | 建立餐廳評論 | `POST` | `/restaurants/<int:id>/reviews` | — (重導向 `/restaurants/<id>`) | 提交對餐廳的雙重評分與評論內容 | 學生 (已登入) |
| | 評論有用按讚 | `POST` | `/reviews/<int:review_id>/like` | JSON (非同步 AJAX) | 切換對評論的按讚狀態，回傳按讚數 | 學生 (已登入) |
| | 發表評論回覆 | `POST` | `/reviews/<int:review_id>/replies` | — (重導向 `/restaurants/<id>`) | 發表對特定評論的二級留言 | 學生 (已登入) |
| **口袋名單** | 口袋名單專區 | `GET` | `/favorites` | `favorite/list.html` | 檢視個人所有收藏的餐廳與自訂名單 | 學生 (已登入) |
| | 切換收藏狀態 | `POST` | `/favorites/toggle/<int:restaurant_id>` | JSON (非同步 AJAX) | 新增/移除特定名單之收藏狀態 | 學生 (已登入) |
| | 建立自訂名單 | `POST` | `/favorites/list/create` | — (重導向 `/favorites`) | 建立新自訂分類清單並收藏指定餐廳 | 學生 (已登入) |

---

## 2. 各路由詳細說明

### 2.1 會員模組 (Auth Blueprint)

#### 1. 註冊頁面 `GET /auth/register`
*   **輸入**：無
*   **處理邏輯**：
    *   若使用者已登入，直接重導向至首頁 `/`。
    *   若未登入，渲染並回傳 `auth/register.html`。
*   **輸出**：HTML 頁面。
*   **錯誤處理**：無。

#### 2. 提交註冊 `POST /auth/register`
*   **輸入**：
    *   表單欄位：`username` (字串)、`email` (逢甲信箱格式字串)、`password` (字串)、`confirm_password` (字串)。
*   **處理邏輯**：
    *   檢查 `password` 與 `confirm_password` 是否一致，若不一致則拋出錯誤。
    *   呼叫 `User.create(username, email, password)`：
        *   內部驗證信箱後綴是否符合 `@fcu.edu.tw` 或 `@mail.fcu.edu.tw`。
        *   檢查使用者名稱與電子信箱是否重複。
    *   建立使用者成功後，利用 Flask `flash` 顯示註冊成功訊息，並重導向至 `/auth/login`。
*   **輸出**：重導向 `302 Redirect` 至 `/auth/login`。
*   **錯誤處理**：
    *   若格式不符或帳號重複，利用 `flash` 顯示詳細錯誤，並重新渲染 `auth/register.html` (表單保留原輸入欄位，密碼除外)。

#### 3. 登入頁面 `GET /auth/login`
*   **輸入**：無。
*   **處理邏輯**：
    *   若已登入，重導向至 `/`。
    *   若未登入，渲染 `auth/login.html`。
*   **輸出**：HTML 頁面。

#### 4. 提交登入 `POST /auth/login`
*   **輸入**：
    *   表單欄位：`email` (字串)、`password` (字串)。
*   **處理邏輯**：
    *   在 `User` 模型中查詢此信箱。
    *   呼叫 `user.check_password(password)` 驗證。
    *   驗證通過後，將 `session['user_id'] = user.id` 及 `session['username'] = user.username` 寫入。
    *   若有 `next` 參數則跳轉至 `next` 頁面，否則重導向至 `/`。
*   **輸出**：重導向 `302 Redirect` 至首頁或來源頁。
*   **錯誤處理**：
    *   若帳號不存在或密碼錯誤，`flash` 顯示「信箱或密碼錯誤」，重新渲染 `auth/login.html`。

#### 5. 登出 `POST /auth/logout`
*   **輸入**：無。
*   **權限要求**：已登入學生。
*   **處理邏輯**：
    *   呼叫 `session.clear()` 清除所有會話資料。
    *   重導向至 `/`。
*   **輸出**：重導向 `302 Redirect` 至 `/`。

---

### 2.2 餐廳模組 (Restaurant Blueprint)

#### 1. 首頁 `GET /`
*   **輸入**：無。
*   **處理邏輯**：
    *   查詢評分最高（`avg_rating` 排序）或最新建立的 6 間餐廳作為熱門推薦。
    *   獲取所有地標與標籤提供前端快速連結。
    *   渲染 `restaurant/list.html`。
*   **輸出**：HTML 頁面。

#### 2. 餐廳列表與篩選 `GET /restaurants`
*   **輸入**：
    *   查詢參數 (Query params)：
        *   `query` (關鍵字篩選餐廳名稱/地址)
        *   `landmark` (地標位置篩選，如正門、東門)
        *   `tags` (多選痛點標籤，傳遞陣列如 `tags=平價&tags=有插座`)
*   **處理邏輯**：
    *   呼叫 `Restaurant.get_all(landmark=landmark, tag_names=tags, query=query)`。
    *   載入所有 `Landmark`（校園位置）清單與 `Tag.get_all()` 用於邊欄篩選介面。
    *   渲染 `restaurant/list.html`，並向模板傳遞目前的篩選狀態。
*   **輸出**：HTML 頁面。

#### 3. 餐廳詳情 `GET /restaurants/<int:id>`
*   **輸入**：
    *   URL 參數：`id` (餐廳 ID)。
*   **處理邏輯**：
    *   呼叫 `Restaurant.get_by_id(id)`。若不存在則引發 `404` 錯誤。
    *   呼叫 `Review.get_by_restaurant(id)` 取得該餐廳的所有評論列表，包含評論的二級回覆（Replies）與按讚（Likes）。
    *   若使用者已登入：
        *   檢查該使用者是否已收藏此餐廳：`Favorite.is_favorited(user_id, id)`。
        *   對每筆評論，檢查該使用者是否已按讚：`ReviewLike.has_liked(user_id, review_id)`。
        *   獲取使用者已建立的自訂收藏名單：`Favorite.get_user_lists(user_id)`，用於收藏彈窗。
    *   渲染 `restaurant/detail.html`。
*   **輸出**：HTML 頁面。
*   **錯誤處理**：若餐廳 `id` 不存在，回傳 `404 Not Found` 頁面。

---

### 2.3 評論互動模組 (Review Blueprint)

#### 1. 建立餐廳評論 `POST /restaurants/<int:id>/reviews`
*   **輸入**：
    *   URL 參數：`id` (餐廳 ID)。
    *   表單欄位：`content` (文字內容)、`rating` (1-5 整數美味度)、`cp_rating` (1-5 整數 CP 值)。
*   **權限要求**：已登入學生。
*   **處理邏輯**：
    *   驗證評分參數是否在 1 到 5 之間。
    *   呼叫 `Review.create(user_id=session['user_id'], restaurant_id=id, content=content, rating=rating, cp_rating=cp_rating)`：
        *   將評論寫入資料庫。
        *   同時觸發 `Restaurant.update_averages(id)` 以重新計算該餐廳的 `avg_rating` 與 `avg_cp` 星等。
    *   重新導向至 `/restaurants/<id>`。
*   **輸出**：重導向 `302 Redirect` 至 `/restaurants/<id>`。
*   **錯誤處理**：
    *   若評分超出範圍或內容空白，`flash` 顯示錯誤，並重導向回該餐廳詳情頁。

#### 2. 評論有用按讚 `POST /reviews/<int:review_id>/like`
*   **輸入**：
    *   URL 參數：`review_id` (評論 ID)。
*   **權限要求**：已登入學生。
*   **處理邏輯**：
    *   若為非同步請求 (X-Requested-With 為 XMLHttpRequest 或 JSON 請求)：
        *   呼叫 `ReviewLike.toggle(user_id=session['user_id'], review_id=review_id)`。
        *   獲取最新的點讚總數：`ReviewLike.get_like_count(review_id)`。
        *   回傳 JSON 格式結果。
*   **輸出**：JSON 格式資料：
    ```json
    {
      "success": true,
      "liked": true,
      "like_count": 12
    }
    ```
*   **錯誤處理**：
    *   未登入：回傳 JSON `{"success": false, "message": "請先登入"}`，狀態碼 `401`。
    *   評論不存在：回傳 JSON `{"success": false, "message": "評論不存在"}`，狀態碼 `404`。

#### 3. 發表評論回覆 `POST /reviews/<int:review_id>/replies`
*   **輸入**：
    *   URL 參數：`review_id` (主評論 ID)。
    *   表單欄位：`content` (回覆內容文字)。
*   **權限要求**：已登入學生。
*   **處理邏輯**：
    *   檢查回覆內容是否空白。
    *   呼叫 `ReviewReply.create(review_id=review_id, user_id=session['user_id'], content=content)`。
    *   重導向至對應的餐廳詳情頁。
*   **輸出**：重導向 `302 Redirect` 至 `/restaurants/<restaurant_id>`。
*   **錯誤處理**：
    *   若內容為空，`flash` 顯示錯誤，重導向回餐廳詳情頁。

---

### 2.4 口袋名單模組 (Favorite Blueprint)

#### 1. 口袋名單專區 `GET /favorites`
*   **輸入**：
    *   查詢參數：`list_name` (可選，指定篩選特定的口袋名單名稱)。
*   **權限要求**：已登入學生。
*   **處理邏輯**：
    *   獲取該使用者已有的所有收藏清單名稱：`Favorite.get_user_lists(session['user_id'])`。
    *   預設 `list_name` 為使用者選擇的清單或 '我的最愛'。
    *   呼叫 `Favorite.get_user_favorites(user_id=session['user_id'], list_name=list_name)`。
    *   渲染 `favorite/list.html`。
*   **輸出**：HTML 頁面。

#### 2. 切換收藏狀態 `POST /favorites/toggle/<int:restaurant_id>`
*   **輸入**：
    *   URL 參數：`restaurant_id` (餐廳 ID)。
    *   JSON / 表單參數：`list_name` (可選，預設為 '我的最愛')。
*   **權限要求**：已登入學生。
*   **處理邏輯**：
    *   呼叫 `Favorite.toggle(user_id=session['user_id'], restaurant_id=restaurant_id, list_name=list_name)`。
    *   若原本已收藏，則將其移出並回傳 `False`；反之新增收藏並回傳 `True`。
*   **輸出**：JSON 格式資料：
    ```json
    {
      "success": true,
      "favorited": true,
      "message": "已成功加入收藏！"
    }
    ```
*   **錯誤處理**：
    *   未登入：回傳 `401 Unauthorized` JSON。

#### 3. 建立自訂名單與收藏 `POST /favorites/list/create`
*   **輸入**：
    *   表單欄位：`restaurant_id` (餐廳 ID)、`list_name` (自訂口袋名單名稱，如「期末歐趴聚餐」)。
*   **權限要求**：已登入學生。
*   **處理邏輯**：
    *   驗證自訂名單名稱是否合法（不可為空）。
    *   呼叫 `Favorite.create_custom_list(user_id=session['user_id'], restaurant_id=restaurant_id, list_name=list_name)`。
    *   重導向回前一頁（一般為餐廳詳情頁或個人收藏頁）。
*   **輸出**：重導向 `302 Redirect` 至來源頁面。

---

## 3. Jinja2 模板清單

所有的視圖頁面都將繼承 `templates/base.html`，並依據功能拆分為以下模組：

### 3.1 基礎骨架
*   `templates/base.html`
    *   **作用**：全域導覽列、頁尾、頁面容器、彈出通知訊息（Flash messages）與全域 CSS/JS 的引用。

### 3.2 會員模組
*   `templates/auth/login.html`
    *   **繼承**：`base.html`
    *   **內容**：使用者信箱、密碼登入表單，包含前往註冊頁的連結。
*   `templates/auth/register.html`
    *   **繼承**：`base.html`
    *   **內容**：使用者註冊表單，包含帳號、信箱（提示逢甲信箱）、密碼、密碼確認。

### 3.3 餐廳與瀏覽模組
*   `templates/restaurant/list.html`
    *   **繼承**：`base.html`
    *   **內容**：首頁與餐廳列表共用。左側為關鍵字、區域地標與痛點多選標籤的篩選面板；右側為餐廳列表卡片。卡片內展示：餐廳照片、名稱、區域、美味度/CP值雙重平均星等、標籤及快速收藏按鈕。
*   `templates/restaurant/detail.html`
    *   **繼承**：`base.html`
    *   **內容**：餐廳基本資料（地圖定位預留區、聯絡電話、營業時間等）與收藏控制按鈕；下方為評論發布區（僅登入可見，包含美味星等與 CP 星等拖曳選擇），以及歷史評論列表（展示發布者、評分、內文、有用點讚按鈕、二級回覆內容與回覆輸入框）。

### 3.4 個人收藏模組
*   `templates/favorite/list.html`
    *   **繼承**：`base.html`
    *   **內容**：自訂口袋名單標籤列（如：我的最愛、期末聚餐、消夜清單），切換分頁顯示該名單內收藏的餐廳列表卡片，並提供快速移除收藏的功能。

---

## 4. 路由骨架程式碼規劃

在 `app/routes/` 中，將建立以下檔案結構：

### 1. [__init__.py](file:///c:/Users/User/Desktop/fcufoodgrade/app/routes/__init__.py)
*   **職責**：集中導出所有 Blueprint 模組，方便 `app/__init__.py` 載入註冊。

### 2. [auth.py](file:///c:/Users/User/Desktop/fcufoodgrade/app/routes/auth.py)
*   **職責**：登入、註冊、登出與使用者登入狀態驗證裝飾器 `login_required`。

### 3. [restaurant.py](file:///c:/Users/User/Desktop/fcufoodgrade/app/routes/restaurant.py)
*   **職責**：首頁渲染、餐廳列表檢索、地理與標籤複合篩選、餐廳詳細頁資訊查詢。

### 4. [review.py](file:///c:/Users/User/Desktop/fcufoodgrade/app/routes/review.py)
*   **職責**：評論寫入、美味度與 CP 值評分、評論「有用」按讚與留言回覆。

### 5. [favorite.py](file:///c:/Users/User/Desktop/fcufoodgrade/app/routes/favorite.py)
*   **職責**：個人收藏清單展示、餐廳收藏狀態切換、自訂口袋名單名稱新增。
