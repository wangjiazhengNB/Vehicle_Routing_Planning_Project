/**
 * 认证页面脚本
 */

const API_BASE = '/api/auth';
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_info';

/**
 * 设置 Cookie
 */
function setCookie(name, value, days = 7) {
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
}

/**
 * 删除 Cookie
 */
function deleteCookie(name) {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/`;
}

/**
 * 显示 Toast 消息
 */
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = toast.querySelector('.toast-message');

    // 移除之前的类型
    toast.classList.remove('success', 'error', 'warning');
    toast.classList.add(type);

    toastMessage.textContent = message;
    toast.classList.add('show');

    // 3秒后自动隐藏
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/**
 * 切换密码显示/隐藏
 */
function initPasswordToggle() {
    const toggleButtons = document.querySelectorAll('.toggle-password');

    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.dataset.target;
            const input = document.getElementById(targetId);
            const eyeOpen = this.querySelector('.eye-open');
            const eyeClosed = this.querySelector('.eye-closed');

            if (input.type === 'password') {
                input.type = 'text';
                eyeOpen.style.display = 'none';
                eyeClosed.style.display = 'block';
            } else {
                input.type = 'password';
                eyeOpen.style.display = 'block';
                eyeClosed.style.display = 'none';
            }
        });
    });
}

/**
 * 初始化标签切换
 */
function initTabSwitch() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const forms = document.querySelectorAll('.auth-form');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.dataset.tab;

            // 更新标签状态
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            // 切换表单
            forms.forEach(form => form.classList.remove('active'));

            if (targetTab === 'login') {
                document.getElementById('login-form').classList.add('active');
            } else if (targetTab === 'register') {
                document.getElementById('register-form').classList.add('active');
            }
        });
    });
}

/**
 * 登录处理
 */
async function handleLogin(event) {
    event.preventDefault();

    const loginField = document.getElementById('login-field').value.trim();
    const password = document.getElementById('login-password').value;
    const rememberMe = document.getElementById('remember-me').checked;

    // 验证输入
    if (!loginField || !password) {
        showToast('请填写完整的登录信息', 'error');
        return;
    }

    // 禁用提交按钮
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = '登录中...';

    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=utf-8'
            },
            body: JSON.stringify({
                login_field: loginField,
                password: password
            })
        });

        const result = await response.json();

        if (result.success) {
            // 保存令牌和用户信息
            const token = result.data.access_token;
            const userInfo = result.data.user;

            // 设置 cookie（用于后端验证）
            setCookie(TOKEN_KEY, token, rememberMe ? 30 : 1);

            if (rememberMe) {
                localStorage.setItem(TOKEN_KEY, token);
                localStorage.setItem(USER_KEY, JSON.stringify(userInfo));
            } else {
                sessionStorage.setItem(TOKEN_KEY, token);
                sessionStorage.setItem(USER_KEY, JSON.stringify(userInfo));
            }

            showToast('登录成功！正在跳转...', 'success');

            // 延迟跳转
            setTimeout(() => {
                // 获取 next 参数，如果有则跳转到指定页面
                const urlParams = new URLSearchParams(window.location.search);
                const nextPage = urlParams.get('next') || '/app';
                window.location.href = nextPage;
            }, 1000);
        } else {
            showToast(result.error || '登录失败', 'error');
        }
    } catch (error) {
        console.error('登录错误:', error);
        showToast('网络错误，请稍后重试', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

/**
 * 注册处理
 */
async function handleRegister(event) {
    event.preventDefault();

    const username = document.getElementById('register-username').value.trim();
    const email = document.getElementById('register-email').value.trim();
    const phone = document.getElementById('register-phone').value.trim();
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    const agreeTerms = document.getElementById('agree-terms').checked;

    // 验证用户名
    if (!username) {
        showToast('请输入用户名', 'error');
        return;
    }

    if (username.length < 2 || username.length > 20) {
        showToast('用户名长度应为2-20个字符', 'error');
        return;
    }

    // 允许中文、字母、数字、下划线、连字符
    const usernameRegex = /^[\u4e00-\u9fa5a-zA-Z0-9_-]+$/;
    if (!usernameRegex.test(username)) {
        showToast('用户名只能包含中文、字母、数字、下划线和连字符', 'error');
        return;
    }

    // 检查是否至少需要一个中文、字母或数字
    const hasValidChar = /[\u4e00-\u9fa5a-zA-Z0-9]/.test(username);
    if (!hasValidChar) {
        showToast('用户名至少需要一个中文、字母或数字', 'error');
        return;
    }

    // 验证邮箱
    if (email) {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailRegex.test(email)) {
            showToast('请输入有效的邮箱地址', 'error');
            return;
        }
    }

    // 验证手机号
    if (phone) {
        const phoneRegex = /^1[3-9]\d{9}$/;
        if (!phoneRegex.test(phone)) {
            showToast('请输入有效的手机号', 'error');
            return;
        }
    }

    // 至少需要邮箱或手机号之一
    if (!email && !phone) {
        showToast('请至少填写邮箱或手机号', 'error');
        return;
    }

    // 验证密码
    if (!password || password.length < 6) {
        showToast('密码长度不能少于6位', 'error');
        return;
    }

    if (password.length > 50) {
        showToast('密码长度不能超过50位', 'error');
        return;
    }

    // 验证确认密码
    if (password !== confirmPassword) {
        showToast('两次输入的密码不一致', 'error');
        return;
    }

    // 验证用户协议
    if (!agreeTerms) {
        showToast('请阅读并同意用户协议和隐私政策', 'error');
        return;
    }

    // 禁用提交按钮
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = '注册中...';

    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=utf-8'
            },
            body: JSON.stringify({
                username: username,
                password: password,
                email: email || undefined,
                phone: phone || undefined
            })
        });

        const result = await response.json();

        if (result.success) {
            // 自动登录
            const token = result.data.access_token;
            const userInfo = result.data.user;

            // 设置 cookie（用于后端验证）
            setCookie(TOKEN_KEY, token, 30);

            localStorage.setItem(TOKEN_KEY, token);
            localStorage.setItem(USER_KEY, JSON.stringify(userInfo));

            showToast('注册成功！正在跳转...', 'success');

            setTimeout(() => {
                window.location.href = '/app';
            }, 1000);
        } else {
            showToast(result.error || '注册失败', 'error');
        }
    } catch (error) {
        console.error('注册错误:', error);
        showToast('网络错误，请稍后重试', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

/**
 * 忘记密码处理
 */
async function handleForgotPassword(event) {
    event.preventDefault();

    const contact = document.getElementById('reset-contact').value.trim();

    if (!contact) {
        showToast('请输入邮箱或手机号', 'error');
        return;
    }

    // 禁用提交按钮
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = '发送中...';

    try {
        const response = await fetch(`${API_BASE}/password/reset/request`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=utf-8'
            },
            body: JSON.stringify({
                contact: contact
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast(result.message, 'success');
            // 切换回登录表单
            setTimeout(() => {
                document.querySelector('.tab-btn[data-tab="login"]').click();
            }, 2000);
        } else {
            showToast(result.error || '请求失败', 'error');
        }
    } catch (error) {
        console.error('请求错误:', error);
        showToast('网络错误，请稍后重试', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

/**
 * 返回首页
 */
function goToHome() {
    window.location.href = '/';
}

/**
 * 检查登录状态
 */
function checkLoginStatus() {
    const token = localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY);

    if (token) {
        // 如果有 token，跳转到应用页面
        window.location.href = '/app';
        return true;
    }
    return false;
}

/**
 * 页面初始化
 */
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否已登录
    if (checkLoginStatus()) {
        return;
    }

    // 初始化密码显示/隐藏切换
    initPasswordToggle();

    // 初始化标签切换
    initTabSwitch();

    // 登录表单提交
    document.getElementById('login-form').addEventListener('submit', handleLogin);

    // 注册表单提交
    document.getElementById('register-form').addEventListener('submit', handleRegister);

    // 忘记密码表单提交
    document.getElementById('forgot-form').addEventListener('submit', handleForgotPassword);

    // 忘记密码链接
    document.getElementById('forgot-password-link').addEventListener('click', function(e) {
        e.preventDefault();
        // 隐藏所有表单
        document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
        // 隐藏标签
        document.querySelector('.auth-tabs').style.display = 'none';
        // 显示忘记密码表单
        document.getElementById('forgot-form').classList.add('active');
    });

    // 返回登录按钮
    document.getElementById('back-to-login').addEventListener('click', function() {
        // 隐藏所有表单
        document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
        // 显示标签
        document.querySelector('.auth-tabs').style.display = 'flex';
        // 显示登录表单
        document.querySelector('.tab-btn[data-tab="login"]').click();
    });

    // 回车键处理
    document.getElementById('login-password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('login-form').dispatchEvent(new Event('submit'));
        }
    });

    document.getElementById('register-confirm-password').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('register-form').dispatchEvent(new Event('submit'));
        }
    });
});
