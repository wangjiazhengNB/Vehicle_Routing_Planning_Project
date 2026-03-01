/**
 * 首页脚本
 */

// 平滑滚动
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href !== '#' && href.length > 1) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// 导航栏滚动效果
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 100) {
        navbar.style.boxShadow = '0 4px 20px rgba(33, 147, 176, 0.3)';
    } else {
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.08)';
    }

    lastScroll = currentScroll;
});

// 检查登录状态
function checkLoginStatus() {
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    const navActions = document.querySelector('.nav-actions');

    if (token) {
        // 已登录，更新导航栏
        const userInfo = localStorage.getItem('user_info') || sessionStorage.getItem('user_info');
        if (userInfo) {
            try {
                const user = JSON.parse(userInfo);
                navActions.innerHTML = `
                    <a href="/app" class="btn-enter">
                        进入系统
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="5" y1="12" x2="19" y2="12"/>
                            <polyline points="12,5 19,12 12,19"/>
                        </svg>
                    </a>
                    <div class="user-menu">
                        <span class="username">${user.username || '用户'}</span>
                        <button class="btn-logout" onclick="handleLogout()">退出</button>
                    </div>
                `;
            } catch (e) {
                console.error('解析用户信息失败:', e);
            }
        }
    }
}

// 退出登录
async function handleLogout() {
    try {
        const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');

        if (token) {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
        }
    } catch (error) {
        console.error('登出请求失败:', error);
    }

    // 清除本地存储
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('user_info');

    // 清除 cookie
    document.cookie = 'auth_token=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/';

    // 重新加载页面
    location.reload();
}

// 添加滚动动画
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const target = entry.target;

            // 移除初始状态类
            target.classList.remove('animate-enter');

            // 获取动画时长和延迟
            const duration = target.classList.contains('feature-card') ? 600 : 500;
            const delay = parseFloat(target.dataset.animDelay || 0);

            // 动画完成后清理所有行内样式
            setTimeout(() => {
                target.style.transition = '';
                target.style.opacity = '';
                target.style.transform = '';
            }, duration + delay * 1000);
        }
    });
}, observerOptions);

// 观察需要动画的元素
document.addEventListener('DOMContentLoaded', () => {
    checkLoginStatus();

    // 为特性卡片添加滚动动画
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        card.classList.add('animate-enter');
        card.dataset.animDelay = index * 0.1;
        card.style.transition = `opacity 0.6s ease, transform 0.6s ease ${index * 0.1}s`;
        observer.observe(card);
    });

    // 为算法项添加滚动动画
    const algorithmItems = document.querySelectorAll('.algorithm-item');
    algorithmItems.forEach((item, index) => {
        item.classList.add('animate-enter');
        item.dataset.animDelay = index * 0.15;
        item.style.transition = `opacity 0.5s ease, transform 0.5s ease ${index * 0.15}s`;
        observer.observe(item);
    });
});

// 添加动态样式
const style = document.createElement('style');
style.textContent = `
    .btn-enter {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 10px 24px;
        border-radius: 8px;
        background: var(--primary-gradient);
        color: white;
        font-weight: 500;
        transition: all 0.3s;
    }
    .btn-enter:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }
    .user-menu {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .username {
        padding: 8px 16px;
        background: rgba(102, 126, 234, 0.1);
        border-radius: 20px;
        font-size: 0.9rem;
        color: var(--primary-color);
    }
    .btn-logout {
        padding: 8px 16px;
        background: transparent;
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 8px;
        color: var(--text-gray);
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.3s;
    }
    .btn-logout:hover {
        border-color: var(--primary-color);
        color: var(--primary-color);
    }
`;
document.head.appendChild(style);
