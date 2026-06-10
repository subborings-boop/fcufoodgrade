// main.js - 逢甲美食評論網 前端非同步互動邏輯

document.addEventListener('DOMContentLoaded', () => {
    // 1. 自動淡出閃現訊息 (Flash Messages)
    const alerts = document.querySelectorAll('.alert-custom');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // 2. 非同步按讚有用功能 (Review Useful Likes)
    const likeButtons = document.querySelectorAll('.btn-like-review');
    likeButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const reviewId = button.getAttribute('data-review-id');
            if (!reviewId) return;

            try {
                const response = await fetch(`/reviews/${reviewId}/like`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.status === 401) {
                    alert('請先登入後再進行此操作。');
                    window.location.href = `/auth/login?next=${window.location.pathname}`;
                    return;
                }

                if (!response.ok) throw new Error('Network response was not ok');

                const data = await response.json();
                if (data.success) {
                    // 更新點讚次數顯示
                    const countSpan = button.querySelector('.like-count');
                    if (countSpan) countSpan.textContent = data.like_count;

                    // 切換按鈕的視覺樣式
                    if (data.liked) {
                        button.classList.add('liked');
                        button.classList.remove('btn-outline-custom');
                        button.classList.add('btn-primary-custom');
                    } else {
                        button.classList.remove('liked');
                        button.classList.add('btn-outline-custom');
                        button.classList.remove('btn-primary-custom');
                    }
                } else {
                    alert(data.message || '點讚失敗。');
                }
            } catch (err) {
                console.error('Error toggling like:', err);
                alert('點讚失敗，請稍後再試。');
            }
        });
    });

    // 3. 非同步收藏切換功能 (Favorite Toggle)
    const favButtons = document.querySelectorAll('.btn-toggle-favorite');
    favButtons.forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const restaurantId = button.getAttribute('data-restaurant-id');
            const listName = button.getAttribute('data-list-name') || '我的最愛';
            if (!restaurantId) return;

            try {
                const response = await fetch(`/favorites/toggle/${restaurantId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ list_name: listName })
                });

                if (response.status === 401) {
                    alert('請先登入後再進行此操作。');
                    window.location.href = `/auth/login?next=${window.location.pathname}`;
                    return;
                }

                if (!response.ok) throw new Error('Network response was not ok');

                const data = await response.json();
                if (data.success) {
                    // 切換愛心圖示 (若使用 SVG 或 FontAwesome)
                    const icon = button.querySelector('i');
                    if (icon) {
                        if (data.favorited) {
                            icon.classList.remove('bi-heart');
                            icon.classList.add('bi-heart-fill');
                            button.classList.add('favorited');
                        } else {
                            icon.classList.remove('bi-heart-fill');
                            icon.classList.add('bi-heart');
                            button.classList.remove('favorited');
                        }
                    }
                    
                    // 如果是在收藏清單頁面，取消收藏後直接移除該卡片
                    if (window.location.pathname === '/favorites' && !data.favorited) {
                        const card = button.closest('.col');
                        if (card) {
                            card.style.transition = 'all 0.5s ease';
                            card.style.transform = 'scale(0.8)';
                            card.style.opacity = '0';
                            setTimeout(() => {
                                card.remove();
                                // 如果完全沒有收藏，顯示空狀態提示
                                const container = document.querySelector('.favorites-grid');
                                if (container && container.children.length === 0) {
                                    location.reload();
                                }
                            }, 500);
                        }
                    }
                } else {
                    alert(data.message || '操作失敗。');
                }
            } catch (err) {
                console.error('Error toggling favorite:', err);
                alert('操作失敗，請稍後再試。');
            }
        });
    });

    // 4. Dark/Light Theme Toggle
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeToggleIcon = document.getElementById('theme-toggle-icon');

    function updateToggleIcon(theme) {
        if (!themeToggleIcon) return;
        if (theme === 'light') {
            themeToggleIcon.className = 'bi bi-sun-fill';
        } else {
            themeToggleIcon.className = 'bi bi-moon-stars-fill';
        }
    }

    // Initialize toggle icon based on active theme
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    updateToggleIcon(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const activeTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = activeTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateToggleIcon(newTheme);
        });
    }
});
