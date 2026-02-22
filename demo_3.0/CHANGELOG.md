# 📝 更新日志

所有重要版本变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## [3.0.0] - 2026-02-22

### 🎉 重大更新 - 全新架构

#### 新增
- **三种算法完整实现**
  - Dijkstra 最短路径算法
  - A* 启发式搜索算法
  - PSO 粒子群优化算法

- **高德地图API深度集成**
  - 驾车路径规划API
  - 地理编码/逆地理编码API
  - POI关键词搜索API
  - 途经点多路径规划

- **多路径规划技术**
  - 通过POI途经点生成差异化路径
  - 支持最多3个途经点的绕行路线
  - 多策略API数据融合

- **智能缓存系统**
  - 地址解析缓存（address_cache表）
  - 路径结果缓存（route_cache表）
  - 自动过期机制

- **多目标成本计算**
  - 距离因素 (distance)
  - 拥堵因素 (congestion)
  - 施工因素 (construction)
  - 可配置权重

- **Web可视化界面**
  - 响应式路径规划表单
  - 算法选择与对比功能
  - 实时结果展示

- **RESTful API**
  - `/api/route/plan` - 单算法路径规划
  - `/api/route/compare` - 多算法对比
  - `/api/algorithms/list` - 算法列表

- **Folium地图生成**
  - 路径可视化
  - 多路径对比展示
  - 地图文件导出

#### 变更
- **架构重构**
  - 从静态路网数据迁移到API实时数据
  - 移除 `road_network` 表依赖
  - 新增 `graph_builder` 服务构建临时图结构

- **算法优化**
  - Dijkstra: 优化为纯距离优先
  - A*: 引入拥堵因素
  - PSO: 综合三个因素的多目标优化

#### 文档
- 新增 `ROADMAP.md` 开发路线图
- 更新 `README.md` 完整项目文档
- 新增 `CHANGELOG.md` 版本更新日志
- 保留 `DATAGRIP_GUIDE.md` 数据库配置指南

#### 测试
- 新增 `test_dijkstra.py` - Dijkstra算法测试
- 新增 `test_astar.py` - A*算法测试
- 新增 `test_pso.py` - PSO算法测试
- 新增 `test_algorithm_comparison.py` - 算法对比测试

---

## [2.0.0] - 2026-01-XX

### 新增
- 高德地图API基础集成
- Dijkstra算法实现
- 基础Web界面

### 变更
- 从模拟数据迁移到真实地图数据

---

## [1.0.0] - 2025-12-XX

### 新增
- 项目初始化
- 模拟路网数据
- 基础Dijkstra实现
- 命令行测试接口

---

## 📅 计划中

### [3.1.0] - 算法优化
- PSO参数调优
- A*启发函数扩展
- 并行计算优化

### [3.2.0] - 功能增强
- 多点路径规划
- 实时交通数据集成
- 用户自定义途经点

### [4.0.0] - 系统升级
- 微服务架构
- Vue.js单页应用
- 更多算法支持（蚁群、遗传等）

---

<div align="center">

**查看完整开发计划**: [ROADMAP.md](ROADMAP.md)

</div>
