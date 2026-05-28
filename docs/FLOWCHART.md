# 系統流程圖與路由對照文件 (FLOWCHART.md) - 逢甲美食評論網

本文件視覺化呈現「逢甲美食評論網」的使用者操作路徑（User Flow）與系統內部資料傳遞序列（Sequence Diagram），並列出各功能之路由設計與 HTTP 方法對照表。

---

## 1. 使用者流程圖 (User Flow)

此流程圖描述未登入訪客與已登入逢甲學生在系統中的操作路徑與功能分流：

```mermaid
flowchart TD
    A([開啟網頁首頁]) --> B[首頁 - 餐廳推薦列表與搜尋]
    B --> C{使用者是否已登入？}
    
    %% 未登入訪客流向
    C -->|否| D[訪客模式]
    D --> E[瀏覽熱門餐廳與真實評論]
    D --> F[使用關鍵字與校園地理位置搜尋]
    D --> G[點擊註冊 / 登入]
    G --> H[填寫逢甲信箱註冊表單]
    H --> I{驗證是否為逢甲信箱後綴？<br>@fcu.edu.tw / @mail.fcu.edu.tw}
    I -->|否| H
    I -->|是| J[發送驗證並完成註冊與登入]
    J --> K[學生模式 (已登入)]

    %% 已登入學生流向
    C -->|是| K
    K --> L[使用痛點標籤進階篩選<br>平價/大份量/有插座/適合系聚]
    K --> M[查看餐廳詳細頁]
    M --> N[發表美食評論與給予CP值/美味度評分]
    M --> O[對他人評論進行按讚與留言互動]
    M --> P[點擊愛心加入個人收藏]
    K --> Q[進入個人名單管理中心]
    Q --> R[管理自訂口袋名單<br>如：歐趴糖清單、系聚備選]
```

---

## 2. 系統序列圖 (Sequence Diagram)

以下以核心功能「已登入學生發表評論與更新餐廳評分」為例，展示前端瀏覽器、後端 Flask 控制器、資料庫模型與 SQLite 之間的互動與資料流：

```mermaid
sequenceDiagram
    actor User as 逢甲學生
    participant Browser as 瀏覽器 (Client)
    participant Flask as Flask Route (Controller)
    participant Model as SQLAlchemy ORM (Model)
    participant DB as SQLite Database (DB)

    User->>Browser: 在餐廳詳情頁填寫評論、評分 (美味度/CP值) 並送出表單
    Browser->>Flask: POST /restaurants/<id>/reviews (攜帶 Session Cookie 與表單資料)
    
    Note over Flask: 1. 驗證 Session 登入狀態<br/>2. 進行表單欄位驗證與防 XSS 清洗
    
    Flask->>Model: 建立新評論物件 (Review)
    Model->>DB: INSERT INTO reviews (user_id, restaurant_id, rating, cp_rating, content)
    DB-->>Model: 寫入成功 (回傳 review_id)
    
    Note over Flask, Model: 重新計算該餐廳的平均美味度與平均 CP 值
    Flask->>Model: Restaurant.update_averages(restaurant_id)
    Model->>DB: SELECT AVG(rating), AVG(cp_rating) FROM reviews WHERE restaurant_id = ...
    DB-->>Model: 回傳平均計算數值
    Model->>DB: UPDATE restaurants SET avg_rating = ..., avg_cp = ... WHERE id = ...
    DB-->>Model: 更新餐廳平均分數成功
    
    Flask-->>Browser: 重導向 (Redirect 302) 至 /restaurants/<id>
    
    Browser->>Flask: GET /restaurants/<id>
    Flask->>Model: 查詢該餐廳更新後的資訊與評論清單
    Model->>DB: SELECT * FROM restaurants WHERE id = ...; SELECT * FROM reviews;
    DB-->>Model: 回傳最新餐廳與評論資料
    Flask->>Browser: Render restaurant/detail.html 并返回 HTML 串流
    Browser-->>User: 顯示新評論與重新計算後的餐廳平均星等
```

---

## 3. 功能路由對照表

以下為本專案規劃的所有端點（Endpoints）、支援的 HTTP 方法、以及對應的功能說明與權限限制：

| 功能模組 | 路由 (URL Path) | HTTP 方法 | 功能描述 | 權限要求 |
| :--- | :--- | :--- | :--- | :--- |
| **首頁與瀏覽** | `/` | GET | 首頁，展示推薦餐廳與關鍵字搜尋入口。 | 訪客 / 學生 |
| **會員管理** | `/auth/register` | GET / POST | 顯示註冊頁面 / 提交註冊資料（檢查逢甲信箱格式）。 | 訪客 |
| | `/auth/login` | GET / POST | 顯示登入頁面 / 提交登入憑證驗證。 | 訪客 |
| | `/auth/logout` | POST | 登出，清除 Session。 | 學生 |
| **餐廳管理** | `/restaurants` | GET | 餐廳列表頁，支援 query 參數進行區域與標籤篩選。 | 訪客 / 學生 |
| | `/restaurants/<int:id>` | GET | 餐廳詳情頁，展示餐廳資訊、平均 CP 值與評論清單。 | 訪客 / 學生 |
| **評論互動** | `/restaurants/<int:id>/reviews` | POST | 提交新評論與評分（美味度、CP值）。 | 學生 (需登入) |
| | `/reviews/<int:review_id>/like` | POST | 對某篇評論按讚（有用），非同步 AJAX 回傳最新按讚數。 | 學生 (需登入) |
| | `/reviews/<int:review_id>/replies` | POST | 對某篇評論發表回覆留言。 | 學生 (需登入) |
| **口袋名單** | `/favorites` | GET | 檢視個人已收藏的餐廳列表與自訂名單群組。 | 學生 (需登入) |
| | `/favorites/toggle/<int:restaurant_id>` | POST | 加入或取消收藏該餐廳，非同步 AJAX 回傳狀態。 | 學生 (需登入) |
| | `/favorites/list/create` | POST | 建立新的自訂分類口袋名單（如：宵夜特輯）。 | 學生 (需登入) |
