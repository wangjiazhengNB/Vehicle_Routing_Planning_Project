# 🚦 多算法车辆路径规划系统

<div align="center">

**基于 Flask + 高德地图API + 多算法的智能路径规划系统**

展示从基础到完整功能的开发演进过程

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 项目简介

一个完整的车辆路径规划系统项目，经历了从模拟数据到真实API、从单一算法到多算法对比的完整演进过程。每个版本都保留了完整代码，可用于学习不同阶段的技术实现。

---

## 🗂️ 版本对比

| 版本 | 状态 | 核心特性 | 技术栈 | 推荐度 |
|------|:----:|----------|--------|:------:|
| **[demo_1.0](./demo_1.0/)** | 📦 已归档 | • 模拟路网数据<br>• Dijkstra算法<br>• 基础Web界面 | Flask + MySQL | ⭐⭐ |
| **[demo_2.0](./demo_2.0/)** | 📦 已归档 | • 高德地图API集成<br>• 地址解析<br>• 路径可视化 | Flask + 高德API | ⭐⭐⭐ |
| **[demo_3.0](./demo_3.0/)** | ✅ **当前版本** | • **三算法** (Dijkstra/A*/PSO)<br>• **途经点多路径**<br>• **智能缓存系统**<br>• **RESTful API** | Flask + 高德API + Folium | ⭐⭐⭐⭐⭐ |

---

## 🚀 快速开始

### 推荐使用 demo_3.0（最新完整版）

```bash
# 进入项目目录
cd Vehicle_Routing_Planning_Project/demo_3.0

# 安装依赖
pip install -r requirements.txt

# 配置高德API Key（编辑 config.yaml）
# amap.api_key: "YOUR_API_KEY"

# 启动应用
python run.py
```

访问 http://localhost:5000 查看Web界面

---

## 📊 版本演进历程

```
┌─────────────────────────────────────────────────────────────────┐
│                        项目演进时间线                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  demo_1.0                    demo_2.0                    demo_3.0 │
│  (2025-12)                   (2026-01)                   (2026-02)│
│     │                            │                            │    │
│     ▼                            ▼                            ▼    │
│  ┌──────┐                    ┌──────┐                    ┌──────┐│
│  │ 模拟 │                    │ API  │                    │ 多   ││
│  │ 数据 │                    │ 集成 │                    │ 算法 ││
│  │      │                    │      │                    │      ││
│  │ Dijkstra                  │ Dijkstra                  │ Dijkstra│
│  │                            │                            │ A*     │
│  │                            │                            │ PSO    │
│  └──────┘                    └──────┘                    └──────┘│
│                                                                  │
│  静态 road_network 表          高德地图API              途经点多路径│
│  14条模拟数据                  实时路网数据              POI搜索   │
│                                                                  │
│  基础功能                      地址解析                    智能缓存  │
│                                路径可视化                  RESTful API│
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 各版本详细说明

### demo_1.0 - 基础版

**适用场景**：学习 Dijkstra 算法基础实现

```bash
cd demo_1.0
python run.py
```

**特点**：
- 使用静态 MySQL 表存储路网数据（14条模拟道路）
- 纯 Dijkstra 最短路径算法
- 简单的 Web 界面
- 适合算法初学者

---

### demo_2.0 - API集成版

**适用场景**：学习地图API集成

```bash
cd demo_2.0
python run.py
```

**特点**：
- 集成高德地图API（驾车路径规划、地理编码）
- 实时获取真实路网数据
- Folium 地图可视化
- 地址自动解析和坐标转换

---

### demo_3.0 - 完整版 ✨

**适用场景**：生产环境使用、算法对比研究

```bash
cd demo_3.0
python run.py
```

**核心特性**：

| 特性 | 说明 |
|------|------|
| 🔀 **多路径规划** | 利用POI途经点技术生成不同路径 |
| 🧮 **三算法对比** | Dijkstra、A*、PSO 同时运行并对比 |
| 🎯 **多目标优化** | 综合考虑距离、拥堵、施工等因素 |
| 🗺️ **地图可视化** | 基于 Folium 的交互式地图 |
| 💾 **智能缓存** | 地址解析和路径结果双层缓存 |
| 🌐 **RESTful API** | 完整的 API 接口 |

**技术架构**：
```
前端层    →  HTML5 + CSS3 + JavaScript + Folium
后端层    →  Flask + Flask-CORS
算法层    →  Dijkstra │ A* │ PSO
数据层    →  高德地图API │ MySQL缓存 │ SQLAlchemy
```

---

## 🧮 算法对比

| 算法 | 时间复杂度 | 优化目标 | 特点 |
|------|-----------|----------|------|
| **Dijkstra** | O((V+E)logV) | 距离优先 | 保证全局最优 |
| **A*** | O(E+VlogV) | 距离+拥堵 | 启发式搜索，效率高 |
| **PSO** | O(iter×particles×V) | 多目标优化 | 全局搜索能力强 |

---

## 📁 项目结构

```
Vehicle_Routing_Planning_Project/
├── demo_1.0/              # 基础版（已归档）
│   ├── src/               # 源代码
│   ├── tests/             # 测试文件
│   └── README.md          # 版本文档
│
├── demo_2.0/              # API集成版（已归档）
│   ├── src/               # 源代码
│   ├── tests/             # 测试文件
│   └── README.md          # 版本文档
│
├── demo_3.0/              # 完整版（推荐）✨
│   ├── src/               # 源代码
│   │   ├── algorithms/    # 算法实现
│   │   ├── services/      # 业务服务
│   │   ├── api/           # RESTful API
│   │   ├── config/        # 配置模块
│   │   └── models/        # 数据模型
│   ├── templates/         # 前端模板
│   ├── static/            # 静态资源
│   ├── tests/             # 单元测试
│   ├── scripts/           # 工具脚本
│   ├── migrations/        # 数据库迁移
│   ├── config.yaml        # 配置文件
│   ├── requirements.txt   # Python依赖
│   ├── README.md          # 详细文档
│   ├── ROADMAP.md         # 开发路线图
│   └── CHANGELOG.md       # 更新日志
│
└── README.md              # 本文件（总览文档）
```

---

## 🛠️ 技术栈

| 层级 | demo_1.0 | demo_2.0 | demo_3.0 |
|------|----------|----------|----------|
| 前端 | HTML/JS | HTML/JS + Folium | HTML/JS + Folium |
| 后端 | Flask | Flask | Flask + Flask-CORS |
| 数据源 | MySQL 静态表 | 高德API | 高德API + MySQL缓存 |
| 算法 | Dijkstra | Dijkstra | Dijkstra + A* + PSO |
| 数据库 | SQLAlchemy | SQLAlchemy | SQLAlchemy |

---

## 🌐 API 接口

demo_3.0 提供完整的 RESTful API：

### 规划路径
```http
POST /api/route/plan
Content-Type: application/json

{
  "start": "湘潭大学",
  "end": "万达广场",
  "algorithm": "dijkstra"
}
```

### 对比算法
```http
POST /api/route/compare
```

### 获取算法列表
```http
GET /api/algorithms/list
```

详细API文档请查看 [demo_3.0/README.md](./demo_3.0/README.md)

---

## 🎯 应用场景

- **城市导航**：为用户提供多种路径选择，避开拥堵
- **物流配送**：多目标优化，综合考虑距离和成本
- **交通分析**：对比不同算法在相同场景下的表现
- **算法学习**：可视化学习最短路径算法原理

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 提交 Pull Request

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

[查看 demo_3.0 详细文档](./demo_3.0/README.md) • [开发路线图](./demo_3.0/ROADMAP.md)

</div>
