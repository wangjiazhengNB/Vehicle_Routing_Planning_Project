// 前端主脚本

const API_BASE = '/api';

/**
 * 规划路径
 */
async function planRoute() {
    const startAddr = document.getElementById('start-addr').value.trim();
    const endAddr = document.getElementById('end-addr').value.trim();
    const algorithm = document.getElementById('algorithm-select').value;

    // 验证输入
    if (!startAddr || !endAddr) {
        showError('请输入起点和终点地址');
        return;
    }

    // 显示加载动画
    showLoading();

    try {
        const response = await fetch(`${API_BASE}/route/plan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=utf-8'
            },
            body: JSON.stringify({
                start: startAddr,
                end: endAddr,
                algorithm: algorithm
            })
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

    if (!startAddr || !endAddr) {
        showError('请输入起点和终点地址');
        return;
    }

    showLoading();

    try {
        const response = await fetch(`${API_BASE}/route/compare`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=utf-8'
            },
            body: JSON.stringify({
                start: startAddr,
                end: endAddr
            })
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
 * 显示规划结果
 */
function displayResult(data) {
    const resultSection = document.getElementById('result-section');
    const compareSection = document.getElementById('compare-section');

    // 隐藏对比区域
    compareSection.style.display = 'none';

    // 显示结果区域
    resultSection.style.display = 'block';

    // 更新结果信息
    document.getElementById('result-algorithm').textContent = data.algorithm;
    document.getElementById('result-distance').textContent =
        data.total_cost ? `${data.total_cost.toFixed(2)} 米` : '-';
    document.getElementById('result-cost').textContent =
        data.total_cost ? data.total_cost.toFixed(2) : '-';
    document.getElementById('result-time').textContent =
        data.metrics && data.metrics.execution_time_ms
            ? `${data.metrics.execution_time_ms.toFixed(2)} 毫秒`
            : '-';
    document.getElementById('result-nodes').textContent =
        data.metrics && data.metrics.nodes_visited
            ? data.metrics.nodes_visited
            : '-';

    // 显示地图
    const resultMap = document.getElementById('result-map');
    if (data.map_file) {
        // 提取文件名并使用正确的API路径
        const fileName = data.map_file.split(/[/\\]/).pop();
        const mapUrl = `${API_BASE}/map/${fileName}`;
        resultMap.innerHTML = `<iframe src="${mapUrl}" style="width:100%;height:400px;border:none;"></iframe>`;
    } else {
        resultMap.innerHTML = '<p class="error">地图生成失败</p>';
    }

    // 滚动到结果区域
    resultSection.scrollIntoView({ behavior: 'smooth' });
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
