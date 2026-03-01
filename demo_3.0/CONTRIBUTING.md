# 贡献指南

感谢你考虑为车辆路径规划项目做出贡献！我们欢迎所有形式的贡献。

---

## 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [报告问题](#报告问题)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交信息规范](#提交信息规范)

---

## 行为准则

- 尊重所有贡献者
- 保持讨论建设性
- 欢迎新手提问

---

## 如何贡献

### 贡献类型

- 报告 Bug
- 讨论代码状态
- 提交修复
- 提出新功能
- 成为维护者

---

## 报告问题

### 报告 Bug

在创建 Issue 前，请确认：

- [ ] 已搜索现有 Issue，避免重复
- [ ] 准备好复现步骤
- [ ] 收集相关环境信息

**Bug 报告模板：**

\`\`\`markdown
### 问题描述
简要描述问题

### 复现步骤
1. 步骤一
2. 步骤二
3. 步骤三

### 期望行为
描述应该发生什么

### 实际行为
描述实际发生了什么

### 环境信息
- OS: [如 Windows 11]
- Python 版本: [如 3.11]
- 项目版本: [如 v3.0]
\`\`\`

### 提交新功能

在提交功能建议前，请考虑：

- [ ] 该功能是否适合本项目
- [ ] 是否已有类似功能
- [ ] 描述使用场景和预期效果

---

## 开发流程

### 1. Fork 项目

点击项目右上角的 Fork 按钮

### 2. 克隆到本地

\`\`\`bash
git clone https://github.com/YOUR_USERNAME/Vehicle_Routing_Planning_Project.git
cd Vehicle_Routing_Planning_Project/demo_3.0
\`\`\`

### 3. 创建分支

\`\`\`bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
\`\`\`

分支命名规范：
- `feature/功能名称` - 新功能
- `fix/问题描述` - Bug 修复
- `docs/文档内容` - 文档更新
- `refactor/重构内容` - 代码重构
- `style/样式调整` - 代码风格修改
- `test/测试内容` - 测试相关
- `chore/杂项` - 构建过程或工具变动

### 4. 安装依赖

\`\`\`bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
\`\`\`

### 5. 进行开发

- 遵循项目代码规范
- 添加必要的测试
- 更新相关文档

### 6. 提交更改

\`\`\`bash
git add .
git commit -m "feat: 添加XXX功能"
\`\`\`

### 7. 推送到远程

\`\`\`bash
git push origin feature/your-feature-name
\`\`\`

### 8. 创建 Pull Request

1. 访问原项目页面
2. 点击 "New Pull Request"
3. 选择你的分支
4. 填写 PR 描述模板

**Pull Request 标题格式：**
- `[Feature] 功能描述`
- `[Fix] Bug 描述`
- `[Docs] 文档更新`
- `[Refactor] 重构描述`

---

## 代码规范

### Python 代码规范

遵循 [PEP 8](https://pep8.org/) 规范：

\`\`\`python
# 好的示例
def calculate_distance(point1: tuple, point2: tuple) -> float:
    """计算两点之间的距离"""
    return ((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)**0.5

# 避免这样
def calc(p1, p2):
    return ((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)**0.5
\`\`\`

### JavaScript 代码规范

\`\`\`javascript
// 好的示例
async function planRoute(start, end, algorithm) {
  try {
    const response = await fetch('/api/route/plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ start, end, algorithm })
    });
    return await response.json();
  } catch (error) {
    console.error('路径规划失败:', error);
  }
}

// 避免这样
async function pr(s,e,a){
  let r=await fetch('/api/route/plan',{
    method:'POST',
    body:JSON.stringify({start:s,end:e,algorithm:a})
  });
  return await r.json();
}
\`\`\`

### 代码注释

- 复杂逻辑必须添加注释
- 函数使用文档字符串
- 注释解释"为什么"而非"是什么"

---

## 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

### 格式

\`\`\`
<type>(<scope>): <subject>

<body>

<footer>
\`\`\`

### Type 类型

| Type | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响功能）|
| `refactor` | 重构（不是新功能也不是修复）|
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `chore` | 构建过程或工具变动 |
| `revert` | 回滚提交 |

### 示例

\`\`\`bash
feat(algorithm): 添加A*算法支持

- 实现A*算法核心逻辑
- 添加启发式函数计算
- 更新算法列表

Closes #123
\`\`\`

\`\`\`bash
fix(api): 修复路径规划接口参数验证问题

修复了当起点或终点为空时未返回400错误的问题
\`\`\`

\`\`\`bash
docs: 更新README安装说明

- 添加Windows环境安装步骤
- 补充依赖版本信息
\`\`\`

---

## 测试

提交代码前请确保：

- [ ] 代码能正常运行
- [ ] 没有语法错误或警告
- [ ] 新功能有对应的测试
- [ ] 所有测试通过

---

## 文档

如果修改了功能，请同步更新：
- README.md
- API 文档
- 代码注释

---

## 审查流程

1. 提交 PR 后，维护者会进行代码审查
2. 根据反馈进行修改
3. 审查通过后会合并到主分支
4. 请保持耐心，维护者可能需要时间处理

---

## 获取帮助

如有疑问，欢迎：
- 提交 Issue
- 加入讨论区
- 联系维护者

---

再次感谢你的贡献！
