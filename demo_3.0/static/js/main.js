// 前端主脚本

const API_BASE = '/api';
const TOKEN_KEY = 'auth_token';
const USER_KEY = 'user_info';

// 全局状态
let waypointCount = 0;
let trafficSettings = {
    construction: [],
    congestion: [],
    closure: []
};
let selectedVehicleType = 'normal';

/**
 * 检查登录状态
 */
function checkLoginStatus() {
    const token = localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY);
    const userInfo = localStorage.getItem(USER_KEY) || sessionStorage.getItem(USER_KEY);

    if (token && userInfo) {
        try {
            const user = JSON.parse(userInfo);
            showLoggedInState(user);
            return true;
        } catch (e) {
            console.error('解析用户信息失败:', e);
            clearAuth();
            return false;
        }
    }

    showGuestState();
    return false;
}

/**
 * 显示已登录状态
 */
function showLoggedInState(user) {
    const guestArea = document.getElementById('guest-area');
    const loggedInArea = document.getElementById('logged-in-area');
    const usernameDisplay = document.getElementById('username-display');

    if (guestArea) guestArea.style.display = 'none';
    if (loggedInArea) loggedInArea.style.display = 'flex';
    if (usernameDisplay) usernameDisplay.textContent = user.username || '用户';
}

/**
 * 显示未登录状态
 */
function showGuestState() {
    const guestArea = document.getElementById('guest-area');
    const loggedInArea = document.getElementById('logged-in-area');

    if (guestArea) guestArea.style.display = 'flex';
    if (loggedInArea) loggedInArea.style.display = 'none';
}

/**
 * 清除认证信息
 */
function clearAuth() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USER_KEY);
    // 清除 cookie
    document.cookie = 'auth_token=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/';
}

/**
 * 登出处理
 */
async function handleLogout() {
    try {
        const token = localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY);

        if (token) {
            await fetch(`${API_BASE}/auth/logout`, {
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
    clearAuth();

    // 跳转到首页
    window.location.href = '/';
}

/**
 * 显示 Toast 消息
 */
function showToast(message, type = 'info') {
    // 创建 toast 元素
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        min-width: 300px;
        padding: 16px 20px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        animation: slideInRight 0.3s ease;
        border-left: 4px solid ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
    `;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="color: #333; font-size: 0.95rem;">${message}</span>
        </div>
    `;

    document.body.appendChild(toast);

    // 3秒后移除
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

/**
 * 获取认证令牌
 */
function getAuthToken() {
    return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY);
}

/**
 * 带认证的 API 请求
 */
async function authFetch(url, options = {}) {
    const token = getAuthToken();

    if (token) {
        options.headers = options.headers || {};
        options.headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, options);

    // 如果返回401，说明令牌过期，清除认证信息
    if (response.status === 401) {
        clearAuth();
        showGuestState();
    }

    return response;
}

/**
 * 规划路径
 */
async function planRoute() {
    const startAddr = document.getElementById('start-addr').value.trim();
    const endAddr = document.getElementById('end-addr').value.trim();
    const algorithm = document.getElementById('algorithm-select').value;
    const waypoints = getAllWaypoints();

    // 获取车辆类型
    const vehicleType = document.querySelector('input[name="vehicle-type"]:checked').value;

    // 获取优化目标
    const objectives = Array.from(document.querySelectorAll('input[name="objective"]:checked'))
        .map(cb => cb.value);

    // 验证输入
    if (!startAddr || !endAddr) {
        showError('请输入起点和终点地址');
        return;
    }

    if (waypoints.length === 0 && vehicleType === 'delivery') {
        showError('配送车辆请至少添加一个途经点');
        return;
    }

    // 显示加载动画
    showLoading();

    try {
        // 构建请求参数（为后端预留）
        const requestData = {
            start: startAddr,
            end: endAddr,
            algorithm: algorithm,
            vehicle_type: vehicleType,
            waypoints: waypoints.length > 0 ? waypoints : undefined,
            objectives: objectives.length > 0 ? objectives : ['distance'],
            traffic_settings: trafficSettings
        };

        const response = await fetch(`${API_BASE}/route/plan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=utf-8'
            },
            body: JSON.stringify(requestData)
        });

        // 检查HTTP状态码
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (result.success) {
            displayResult(result.data);
        } else {
            showError(result.error || '路径规划失败');
        }
    } catch (error) {
        console.error('路径规划错误:', error);
        showError(`网络错误: ${error.message}`);
    } finally {
        hideLoading();
    }
}

/**
 * 对比算法
 */
async function compareAlgorithms() {
    const startAddr = document.getElementById('start-addr').value.trim();
    const endAddr = document.getElementById('end-addr').value.trim();
    const waypoints = getAllWaypoints();
    const vehicleType = document.querySelector('input[name="vehicle-type"]:checked').value;

    if (!startAddr || !endAddr) {
        showError('请输入起点和终点地址');
        return;
    }

    showLoading();

    try {
        const requestData = {
            start: startAddr,
            end: endAddr,
            vehicle_type: vehicleType,
            waypoints: waypoints.length > 0 ? waypoints : undefined,
            traffic_settings: trafficSettings
        };

        const response = await fetch(`${API_BASE}/route/compare`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=utf-8'
            },
            body: JSON.stringify(requestData)
        });

        // 检查HTTP状态码
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (result.success) {
            displayCompareResult(result.data);
        } else {
            showError(result.error || '算法对比失败');
        }
    } catch (error) {
        console.error('算法对比错误:', error);
        showError(`网络错误: ${error.message}`);
    } finally {
        hideLoading();
    }
}

/**
 * 显示规划结果 - 跳转到结果页面
 */
function displayResult(data) {
    // 添加途经点数据
    data.waypoints = getAllWaypoints();

    // 将结果数据编码为 URL 参数并跳转
    const encodedData = encodeURIComponent(JSON.stringify(data));
    window.location.href = `/result?data=${encodedData}`;
}

/**
 * 显示对比结果
 */
function displayCompareResult(data) {
    const resultSection = document.getElementById('result-section');
    const compareSection = document.getElementById('compare-section');
    const compareTable = document.getElementById('compare-table');

    // 隐藏结果区域
    resultSection.style.display = 'none';

    // 显示对比区域
    compareSection.style.display = 'block';

    // 构建对比表格
    let tableHTML = '<table><thead><tr><th>算法</th><th>总成本</th><th>执行时间</th><th>访问节点</th><th>状态</th></tr></thead><tbody>';

    const results = data.results || {};
    const bestAlgorithm = data.best_algorithm;

    for (const [algoName, algoResult] of Object.entries(results)) {
        const isBest = algoName === bestAlgorithm;
        const rowClass = isBest ? 'best-algorithm' : '';
        const status = algoResult.success ? '成功' : '失败';

        tableHTML += `
            <tr class="${rowClass}">
                <td>${algoName}${isBest ? ' ⭐' : ''}</td>
                <td>${algoResult.total_cost ? algoResult.total_cost.toFixed(2) : '-'}</td>
                <td>${algoResult.metrics && algoResult.metrics.execution_time_ms
                    ? `${algoResult.metrics.execution_time_ms.toFixed(2)} ms`
                    : '-'}</td>
                <td>${algoResult.metrics && algoResult.metrics.nodes_visited
                    ? algoResult.metrics.nodes_visited
                    : '-'}</td>
                <td>${status}</td>
            </tr>
        `;
    }

    tableHTML += '</tbody></table>';
    compareTable.innerHTML = tableHTML;

    // 滚动到对比区域
    compareSection.scrollIntoView({ behavior: 'smooth' });
}

/**
 * 清除结果
 */
function clearResults() {
    document.getElementById('result-section').style.display = 'none';
    document.getElementById('compare-section').style.display = 'none';
    document.getElementById('start-addr').value = '';
    document.getElementById('end-addr').value = '';
}

/**
 * 显示加载动画
 */
function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

/**
 * 隐藏加载动画
 */
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

/**
 * 显示错误信息
 */
function showError(message) {
    const errorElement = document.getElementById('error-message');
    document.getElementById('error-text').textContent = message;
    errorElement.style.display = 'block';

    // 3秒后自动隐藏
    setTimeout(() => {
        hideError();
    }, 3000);
}

/**
 * 隐藏错误信息
 */
function hideError() {
    document.getElementById('error-message').style.display = 'none';
}

/**
 * 页面加载时初始化
 */
document.addEventListener('DOMContentLoaded', () => {
    // 检查登录状态
    checkLoginStatus();

    // 绑定登出按钮
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }

    // 加载可用算法列表
    loadAlgorithms();

    // 绑定回车键事件
    document.getElementById('start-addr').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            document.getElementById('end-addr').focus();
        }
    });

    document.getElementById('end-addr').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            planRoute();
        }
    });
});

// ==================== 新增功能函数 ====================

/**
 * 清除输入框
 */
function clearInput(inputId) {
    document.getElementById(inputId).value = '';
}

/**
 * 添加途经点
 */
function addWaypoint() {
    waypointCount++;
    const waypointsList = document.getElementById('waypoints-list');

    const waypointItem = document.createElement('div');
    waypointItem.className = 'waypoint-item';
    waypointItem.id = `waypoint-${waypointCount}`;
    waypointItem.innerHTML = `
        <div class="waypoint-number">${waypointCount}</div>
        <input type="text" class="waypoint-input" id="waypoint-${waypointCount}"
               placeholder="途经点地址" autocomplete="off">
        <div class="waypoint-actions">
            <button class="btn-waypoint-up" onclick="moveWaypoint(${waypointCount}, -1)">↑</button>
            <button class="btn-waypoint-down" onclick="moveWaypoint(${waypointCount}, 1)">↓</button>
            <button class="btn-waypoint-remove" onclick="removeWaypoint(${waypointCount})">✕</button>
        </div>
    `;

    waypointsList.appendChild(waypointItem);
}

/**
 * 移除途经点
 */
function removeWaypoint(id) {
    const waypoint = document.getElementById(`waypoint-${id}`);
    if (waypoint) {
        waypoint.remove();
        renumberWaypoints();
    }
}

/**
 * 移动途经点顺序
 */
function moveWaypoint(id, direction) {
    const waypointsList = document.getElementById('waypoints-list');
    const items = Array.from(waypointsList.children);
    const currentIndex = items.findIndex(item => item.id === `waypoint-${id}`);

    if (currentIndex === -1) return;

    const newIndex = currentIndex + direction;
    if (newIndex < 0 || newIndex >= items.length) return;

    waypointsList.insertBefore(items[newIndex], items[currentIndex]);
    renumberWaypoints();
}

/**
 * 重新编号
 */
function renumberWaypoints() {
    const items = document.querySelectorAll('.waypoint-item');
    items.forEach((item, index) => {
        const numberEl = item.querySelector('.waypoint-number');
        numberEl.textContent = index + 1;
    });
}

/**
 * 获取所有途经点
 */
function getAllWaypoints() {
    const waypointInputs = document.querySelectorAll('.waypoint-input');
    return Array.from(waypointInputs)
        .map(input => input.value.trim())
        .filter(val => val !== '');
}

/**
 * 显示路况设置模态框
 */
function showTrafficSettings() {
    document.getElementById('traffic-modal').style.display = 'flex';
}

/**
 * 关闭路况模态框
 */
function closeTrafficModal() {
    document.getElementById('traffic-modal').style.display = 'none';
}

/**
 * 添加路况项
 */
function addTrafficItem(type) {
    const listId = `${type}-list`;
    const list = document.getElementById(listId);

    const itemId = Date.now();
    const item = document.createElement('div');
    item.className = 'traffic-item';
    item.id = `traffic-${type}-${itemId}`;
    item.dataset.type = type;
    item.dataset.id = itemId;

    if (type === 'construction') {
        item.innerHTML = `
            <input type="text" placeholder="路段名称或地址" class="traffic-from">
            <input type="date" placeholder="截止日期" class="traffic-date">
            <button class="btn-waypoint-remove" onclick="removeTrafficItem('${type}', ${itemId})">✕</button>
        `;
    } else if (type === 'congestion') {
        item.innerHTML = `
            <input type="text" placeholder="路段名称或地址" class="traffic-from">
            <select class="traffic-level">
                <option value="light">轻度拥堵</option>
                <option value="moderate">中度拥堵</option>
                <option value="heavy">重度拥堵</option>
            </select>
            <button class="btn-waypoint-remove" onclick="removeTrafficItem('${type}', ${itemId})">✕</button>
        `;
    } else {
        item.innerHTML = `
            <input type="text" placeholder="路段名称或地址" class="traffic-from">
            <input type="date" placeholder="开放日期" class="traffic-date">
            <button class="btn-waypoint-remove" onclick="removeTrafficItem('${type}', ${itemId})">✕</button>
        `;
    }

    list.appendChild(item);
}

/**
 * 移除路况项
 */
function removeTrafficItem(type, id) {
    const item = document.getElementById(`traffic-${type}-${id}`);
    if (item) {
        item.remove();
    }
}

/**
 * 保存路况设置
 */
function saveTrafficSettings() {
    trafficSettings.construction = [];
    trafficSettings.congestion = [];
    trafficSettings.closure = [];

    // 收集施工路段
    document.querySelectorAll('#construction-list .traffic-item').forEach(item => {
        trafficSettings.construction.push({
            location: item.querySelector('.traffic-from').value.trim(),
            date: item.querySelector('.traffic-date').value
        });
    });

    // 收集拥堵路段
    document.querySelectorAll('#congestion-list .traffic-item').forEach(item => {
        trafficSettings.congestion.push({
            location: item.querySelector('.traffic-from').value.trim(),
            level: item.querySelector('.traffic-level').value
        });
    });

    // 收集封闭路段
    document.querySelectorAll('#closure-list .traffic-item').forEach(item => {
        trafficSettings.closure.push({
            location: item.querySelector('.traffic-from').value.trim(),
            date: item.querySelector('.traffic-date').value
        });
    });

    closeTrafficModal();
    showToast('路况设置已保存', 'success');
}

/**
 * 重置路况设置
 */
function resetTrafficSettings() {
    document.getElementById('construction-list').innerHTML = '';
    document.getElementById('congestion-list').innerHTML = '';
    document.getElementById('closure-list').innerHTML = '';
    trafficSettings = {
        construction: [],
        congestion: [],
        closure: []
    };
    showToast('路况设置已重置', 'info');
}

/**
 * 显示算法信息
 */
async function showAlgorithmInfo() {
    const algorithm = document.getElementById('algorithm-select').value;

    try {
        const response = await fetch(`${API_BASE}/algorithm/info/${algorithm}`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (result.success) {
            const info = result.data;
            document.getElementById('algorithm-info-content').innerHTML = `
                <div class="algorithm-detail">
                    <h3>${info.name}算法</h3>
                    <p class="algorithm-desc">${info.description}</p>
                    <div class="algorithm-meta">
                        <p><strong>算法类型:</strong> ${info.type}</p>
                    </div>
                </div>
            `;
            document.getElementById('algorithm-info-modal').style.display = 'flex';
        }
    } catch (error) {
        console.error('获取算法信息错误:', error);
        showToast('无法获取算法信息', 'error');
    }
}

/**
 * 关闭算法信息模态框
 */
function closeAlgorithmModal() {
    document.getElementById('algorithm-info-modal').style.display = 'none';
}

/**
 * Toast 提示
 */
function showToast(message, type = 'info') {
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.innerHTML = `
        <span class="toast-message">${message}</span>
    `;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2193b0'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 2000;
        animation: slideInRight 0.3s ease;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * 加载可用算法列表
 */
async function loadAlgorithms() {
    try {
        const response = await fetch(`${API_BASE}/algorithms/list`);
        const result = await response.json();

        if (result.success) {
            const select = document.getElementById('algorithm-select');
            select.innerHTML = '';

            result.data.forEach(algo => {
                const option = document.createElement('option');
                option.value = algo.id;
                option.textContent = algo.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载算法列表失败:', error);
    }
}
