# 🚦 多算法车辆路径规划系统

<div align="center">

**基于 Flask + 高德地图API + 多算法的智能路径规划系统**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Dijkstra算法](docs/dijkstra.md) • [A*算法](docs/astar.md) • [PSO算法](docs/pso.md) • [API文档](docs/api.md)

</div>

---

## 📖 项目简介

一个完整的多算法车辆路径规划系统，支持 **Dijkstra**、**A***、**PSO** 三种算法的路径规划与对比分析。系统利用高德地图API获取实时路网数据，通过途经点技术实现多路径规划，为不同场景提供最优路径选择。

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🔀 **多路径规划** | 利用POI途经点技术生成不同路径供算法选择 |
| 🧮 **三算法对比** | Dijkstra、A*、PSO 三种算法同时运行并对比结果 |
| 🎯 **多目标优化** | 综合考虑距离、拥堵、施工等多个因素 |
| 🗺️ **地图可视化** | 基于 Folium 的交互式路径地图展示 |
| 📊 **结果分析** | 详细的路径对比数据和重叠度分析 |
| 🌐 **RESTful API** | 完整的 API 接口支持第三方集成 |
| 💾 **智能缓存** | 地址解析和路径结果缓存，提升响应速度 |
| 🔐 **用户认证系统** | 完整的登录/注册功能，Token 验证，记住我 |
| 🎨 **优化前端界面** | 蓝色主题统一，响应式布局，结果页面优化 |

### 🎯 应用场景

- **城市导航**：为用户提供多种路径选择，避开拥堵
- **物流配送**：多目标优化，综合考虑距离和成本
- **交通分析**：对比不同算法在相同场景下的表现
- **算法学习**：可视化学习最短路径算法原理

---

## 🛠️ 技术栈

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层                                │
│  HTML5 + CSS3 + JavaScript + Folium地图                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        后端层                                │
│  Flask + Flask-CORS + PyYAML                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        算法层                                │
│  Dijkstra  │  A*(A-Star)  │  PSO(粒子群优化)               │
│  距离优先  │  拥堵感知    │  多目标优化                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                        数据层                                │
│  高德地图API  │  MySQL(缓存)  │  SQLAlchemy                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
demo_3.0/
├── src/                          # 源代码目录
│   ├── algorithms/               # 算法核心实现
│   │   ├── dijkstra.py          # Dijkstra最短路径算法
│   │   ├── astar.py             # A*启发式搜索算法
│   │   ├── pso.py               # PSO粒子群优化算法
│   │   ├── cost_calculator.py   # 多目标成本计算
│   │   └── distance_utils.py    # 距离计算工具
│   ├── services/                 # 业务服务层
│   │   ├── amap_service.py      # 高德地图API封装
│   │   ├── graph_builder.py     # 路网图构建
│   │   ├── route_planner.py     # 路径规划核心服务
│   │   ├── route_cache_service.py # 路径缓存服务
│   │   └── map_service.py       # 地图生成服务
│   ├── api/                      # RESTful API
│   │   └── routes.py            # Flask路由定义
│   ├── config/                   # 配置模块
│   │   ├── settings.py          # 配置加载
│   │   └── database.py          # 数据库连接
│   ├── models/                   # 数据模型
│   │   ├── route_result.py      # 路径结果模型
│   │   └── address_cache.py     # 地址缓存模型
│   ├── db/                       # 数据库操作
│   │   └── base.py              # 数据库基类
│   └── utils/                    # 工具函数
│       └── logger.py            # 日志工具
├── templates/                    # 前端模板
│   └── index.html               # Web界面
├── static/                       # 静态资源
│   ├── css/style.css            # 样式文件
│   └── js/main.js               # 前端脚本
├── tests/                        # 单元测试
│   ├── test_dijkstra.py         # Dijkstra测试
│   ├── test_astar.py            # A*测试
│   ├── test_pso.py              # PSO测试
│   └── test_algorithm_comparison.py # 算法对比测试
├── scripts/                      # 工具脚本
│   ├── test_new_architecture.py # 新架构测试
│   ├── test_precise_locations.py # 精确位置测试
│   ├── test_route_planning.py   # 路径规划测试
│   ├── reset_database.py        # 数据库重置
│   └── create_route_cache_table.py # 缓存表创建
├── migrations/                   # 数据库迁移
│   └── create_route_cache_table.sql
├── app.py                        # Flask应用工厂
├── run.py                        # 应用启动入口
├── config.yaml                   # 配置文件
├── requirements.txt              # Python依赖
├── README.md                     # 项目文档
├── ROADMAP.md                    # 开发路线图
└── DATAGRIP_GUIDE.md             # 数据库配置指南
```

---

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+
- **MySQL**: 8.0+
- **高德地图API Key**: [免费申请](https://lbs.amap.com/)

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/Vehicle_Routing_Planning_Project.git
cd Vehicle_Routing_Planning_Project/demo_3.0
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 激活虚拟环境（Linux/Mac）
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

创建数据库（推荐使用 DataGrip，详见 [DATAGRIP_GUIDE.md](DATAGRIP_GUIDE.md)）：

```sql
CREATE DATABASE IF NOT EXISTS vrp_project
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

执行迁移脚本创建缓存表：

```bash
python scripts/create_route_cache_table.py
```

### 5. 配置高德API

编辑 `config.yaml`，填入你的高德API Key：

```yaml
amap:
  api_key: "YOUR_AMAP_API_KEY"  # 替换为你的API Key
  base_url: "https://restapi.amap.com"
```

### 6. 启动应用

```bash
python run.py
```

访问 [http://localhost:5000](http://localhost:5000) 查看Web界面

---

## 📚 API 文档

### 1. 规划路径

```http
POST /api/route/plan
Content-Type: application/json

{
  "start": "湘潭大学",
  "end": "万达广场",
  "algorithm": "dijkstra"
}
```

**响应示例：**

```json
{
  "success": true,
  "algorithm": "dijkstra",
  "path": [1, 5, 8, 12, 15],
  "total_distance": 5234.5,
  "total_cost": 5234.5,
  "execution_time": 0.023
}
```

### 2. 对比算法

```http
POST /api/route/compare
Content-Type: application/json

{
  "start": "湘潭大学",
  "end": "万达广场"
}
```

**响应示例：**

```json
{
  "success": true,
  "results": {
    "dijkstra": { "path": [...], "cost": 5234.5 },
    "astar": { "path": [...], "cost": 5380.2 },
    "pso": { "path": [...], "cost": 5410.8 }
  },
  "comparison": {
    "overlap_dijkstra_astar": "85%",
    "overlap_dijkstra_pso": "72%"
  }
}
```

### 3. 获取算法列表

```http
GET /api/algorithms/list
```

---

## 🧪 运行测试

```bash
# 运行所有测试
pytest

# 运行特定算法测试
pytest tests/test_dijkstra.py -v
pytest tests/test_astar.py -v
pytest tests/test_pso.py -v

# 运行算法对比测试
pytest tests/test_algorithm_comparison.py -v

# 生成测试覆盖率报告
pytest --cov=src --cov-report=html
```

---

## 🧮 算法说明

### Dijkstra 算法

| 属性 | 说明 |
|------|------|
| **类型** | 经典最短路径算法 |
| **时间复杂度** | O((V + E) log V) |
| **优化目标** | 距离 (distance: 1.0) |
| **特点** | 保证找到全局最优解 |
| **适用场景** | 距离优先、追求最短路径 |

### A* (A-Star) 算法

| 属性 | 说明 |
|------|------|
| **类型** | 启发式搜索算法 |
| **时间复杂度** | O(E + V log V) |
| **优化目标** | 距离 + 拥堵 (distance: 0.7, congestion: 0.3) |
| **特点** | 结合启发函数，搜索效率高 |
| **适用场景** | 需要避让拥堵的路径规划 |

### PSO (粒子群优化) 算法

| 属性 | 说明 |
|------|------|
| **类型** | 群智能优化算法 |
| **时间复杂度** | O(iterations × particles × V) |
| **优化目标** | 距离 + 拥堵 + 施工 (distance: 0.5, congestion: 0.3, construction: 0.2) |
| **特点** | 多目标优化，全局搜索能力强 |
| **适用场景** | 复杂多目标优化问题 |

---

## ⚙️ 配置说明

配置文件：`config.yaml`

```yaml
# 数据库配置
database:
  host: "localhost"
  port: 3306
  user: "root"
  password: ""
  database: "vrp_project"

# 高德地图API配置
amap:
  api_key: "YOUR_API_KEY"
  timeout: 10

# Flask配置
flask:
  host: "127.0.0.1"
  port: 5000
  debug: true

# 算法配置
algorithms:
  dijkstra:
    weight_distance: 1.0
  astar:
    weight_distance: 0.7
    weight_congestion: 0.3
  pso:
    weight_distance: 0.5
    weight_congestion: 0.3
    weight_construction: 0.2
    particles: 30
    iterations: 50
```

---

## 🗺️ 核心技术点

### 1. 途经点多路径规划

系统利用高德地图API的途经点（waypoints）功能，在同一起终点间生成多条不同路径：

```
起点 → 直达路线 → 终点        (推荐策略)
起点 → 途经点A → 终点         (绕行策略1)
起点 → 途经点B → 终点         (绕行策略2)
```

### 2. 多目标成本计算

```python
total_cost = distance * weight_distance +
             congestion * weight_congestion +
             construction * weight_construction
```

### 3. 智能缓存机制

- **地址缓存**: 缓存地理编码结果，减少API调用
- **路径缓存**: 缓存算法计算结果，提升重复查询速度

---

## 📊 效果展示

### 路径对比示例

| 算法 | 距离(m) | 成本 | 耗时(ms) | 与Dijkstra重叠 |
|------|---------|------|----------|----------------|
| Dijkstra | 5,234 | 5,234 | 23 | - |
| A* | 5,380 | 4,850 | 18 | 85% |
| PSO | 5,410 | 4,720 | 156 | 72% |

---

## 🚀 未来计划

以下功能已完成前端界面实现，后端集成将在后续版本中逐步完善：

### 🚗 车辆类型选择

| 功能 | 状态 | 说明 |
|------|------|------|
| 普通车辆 | ✅ 前端完成 | 标准车辆路径规划，距离优先 |
| 配送车辆 | ✅ 前端完成 | 考虑配送点，途经点优先 |
| 非机动车 | ✅ 前端完成 | 考虑非机动车道（如自行车），距离和时间优化 |

### 📍 途经点管理

| 功能 | 状态 | 说明 |
|------|------|------|
| 途经点输入 | ✅ 前端完成 | 支持动态添加/删除/排序途经点 |
| 途经点API | 🔄 计划中 | 后端将完善途经点参数处理逻辑 |

### 🎯 多目标优化

| 目标 | 状态 | 说明 |
|------|------|------|
| 最短距离 | ✅ 已支持 | 优化路径总距离 |
| 最短时间 | ✅ 前端完成 | 后端将集成实时交通数据计算预计时间 |
| 最低成本 | ✅ 前端完成 | 后端将支持不同车辆类型的成本模型 |

### 🚧 路况自定义

| 路况类型 | 状态 | 说明 |
|------|------|------|
| 施工路段 | ✅ 前端完成 | 后端将基于施工数据调整路径权重 |
| 道路拥堵 | ✅ 前端完成 | 后端将集成实时路况API，动态调整拥堵系数 |
| 封闭路段 | ✅ 前端完成 | 后端将支持封闭路段的路径禁用 |

### 🔐 用户账户功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 基础认证 | ✅ 已实现 | 登录/注册/登出，Token 管理 |
| 密码重置 | ✅ 前端完成 | 后端将集成邮件/短信验证 |
| 历史记录 | 🔄 计划中 | 后端将支持保存用户规划历史 |
| 个人设置 | 🔄 计划中 | 用户偏好设置（默认车辆、默认算法等） |

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📜 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

---

## 📮 联系方式

- **作者**: 汪嘉正
- **学校**: 湘潭大学
- **位置**: 湖南省湘潭市雨湖区

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐️ Star 支持一下！**

[ roadmap](ROADMAP.md) • [api文档](docs/api.md) • [更新日志](CHANGELOG.md)

</div>
