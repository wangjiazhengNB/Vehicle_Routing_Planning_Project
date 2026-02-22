# 📦 DataGrip 数据库配置指南

> 本指南将一步一步教您如何使用 DataGrip 为项目配置 MySQL 数据库

---

## 📋 数据库说明

本项目使用 **MySQL 8.0+** 存储缓存数据，提高查询性能。

### 数据库表结构

| 表名 | 说明 | 用途 |
|------|------|------|
| `route_cache` | 路径缓存表 | 缓存高德API返回的路径数据和算法计算结果 |
| `address_cache` | 地址缓存表 | 缓存地址地理编码结果，减少API调用 |

**注意**: v3.0 版本不再使用静态的 `road_network` 表，路网数据通过高德地图API实时获取。

---

## 第1步：打开 DataGrip

### 1.1 启动 DataGrip
- 找到桌面的 DataGrip 图标并双击打开
- 或从开始菜单中找到 JetBrains DataGrip 并点击启动

### 1.2 创建/打开项目
- 首次启动会显示欢迎界面
- 点击 "New Project" 或 "Open" 创建/打开项目

---

## 第2步：创建 MySQL 数据库连接

### 2.1 打开数据库连接面板

在 DataGrip 右侧边栏找到：
```
📁 Databases
```
如果没有显示，点击菜单栏：
```
View → Tool Windows → Databases
```

### 2.2 添加新连接

在 `Databases` 面板左上角，找到 **+** 号按钮并点击

### 2.3 选择 MySQL

在下拉列表中选择 **MySQL**

### 2.4 配置连接信息

在弹出的窗口中填写以下信息：

| 字段 | 说明 | 示例 |
|------|------|--------|
| **Host** | MySQL服务器地址 | `localhost` |
| **Port** | MySQL端口号 | `3306` |
| **User** | MySQL用户名 | `root` |
| **Password** | MySQL密码 | 您的MySQL密码 |
| **Database** | 数据库名称 | 留空，稍后创建 |

**重要提示**：
- 如果您的 MySQL 用户名不是 `root`，请填入实际用户名
- 如果忘记了 MySQL 密码，可能需要重置

### 2.5 测试连接

点击 **"Test Connection"** 按钮：

- ✅ **成功**：会显示 "Succeeded"
- ❌ **失败**：会显示错误信息

**如果连接失败，检查以下内容**：
1. MySQL 服务是否已启动？
   - Windows + R → 输入 `services.msc`
   - 找到 MySQL 服务 → 右键 → 启动
2. 用户名和密码是否正确？
3. 端口是否正确？MySQL 默认端口是 `3306`
4. 防火墙是否拦截？

### 2.6 保存连接

测试成功后，点击 **"OK"** 保存连接

---

## 第3步：创建数据库

### 3.1 连接到 MySQL

在 `Databases` 面板中，找到刚才创建的 MySQL 连接
- 双击连接（或右键 → Connect）
- 等待连接成功
- 连接图标会变成 ✅ 绿色

### 3.2 打开 SQL 控制台

有几种方式打开 SQL 控制台：

**方式1**：快捷键
- 按 `Alt + Insert`（或 `Ctrl + Insert`）

**方式2**：右键菜单
- 在 MySQL 连接上右键
- 选择 **"New"** → **"Query Console"**

**方式3**：工具栏
- 点击工具栏的 **"+"** 图标
- 选择 **"New Query Console"**

### 3.3 创建数据库

在 SQL 控制台中输入以下命令：

```sql
-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS vrp_project
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

**说明**：
- `IF NOT EXISTS`：如果数据库已存在则不创建，避免报错
- `CHARACTER SET utf8mb4`：使用 utf8mb4 字符集，支持中文和 emoji
- `COLLATE utf8mb4_unicode_ci`：使用 Unicode 排序规则

### 3.4 执行 SQL 命令

点击工具栏的 **绿色运行按钮** ▶ 或按 `Ctrl + Enter`

✅ **成功标志**：
- 底部消息窗口显示 "1 row affected" 或类似信息
- 没有红色错误信息

### 3.5 刷新数据库列表

在 `Databases` 面板中：
- 点击刷新按钮 🔄（或按 `F5`）
- 现在应该能看到 `vrp_project` 数据库

---

## 第4步：创建数据表

### 方式1：使用 Python 脚本（推荐）

在命令行中执行：

```bash
cd G:\Vehicle_Routing_Planning_Project\demo_3.0
python scripts/create_route_cache_table.py
```

脚本会自动创建以下表：
- `route_cache` - 路径缓存表
- `address_cache` - 地址缓存表

### 方式2：手动执行 SQL 脚本

#### 4.1 创建 route_cache 表

```sql
USE vrp_project;

-- 路径缓存表
CREATE TABLE IF NOT EXISTS route_cache (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',

    -- 缓存键
    start_address VARCHAR(200) NOT NULL COMMENT '起点地址',
    end_address VARCHAR(200) NOT NULL COMMENT '终点地址',
    start_lat DECIMAL(10, 7) NOT NULL COMMENT '起点纬度',
    start_lng DECIMAL(10, 7) NOT NULL COMMENT '起点经度',
    end_lat DECIMAL(10, 7) NOT NULL COMMENT '终点纬度',
    end_lng DECIMAL(10, 7) NOT NULL COMMENT '终点经度',

    -- 原始路径数据（高德API返回）
    raw_polyline TEXT COMMENT '原始polyline数据',
    total_distance DECIMAL(10, 2) COMMENT '总距离(米)',
    estimated_duration INT COMMENT '预估时间(秒)',

    -- 图结构数据
    graph_data LONGTEXT COMMENT '临时图结构(JSON)',
    node_mapping LONGTEXT COMMENT '节点ID映射关系(JSON)',

    -- 算法结果缓存
    dijkstra_result TEXT COMMENT 'Dijkstra结果(JSON)',
    astar_result TEXT COMMENT 'A*结果(JSON)',
    pso_result TEXT COMMENT 'PSO结果(JSON)',

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后访问时间',
    access_count INT DEFAULT 1 COMMENT '访问次数',
    cache_hit_count INT DEFAULT 0 COMMENT '缓存命中次数',

    -- 索引
    UNIQUE KEY uk_route (start_address(150), end_address(150)),
    INDEX idx_coords (start_lat, start_lng, end_lat, end_lng),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路径缓存表';
```

#### 4.2 创建 address_cache 表

```sql
USE vrp_project;

-- 地址缓存表
CREATE TABLE IF NOT EXISTS address_cache (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',

    -- 地址信息
    address VARCHAR(200) NOT NULL COMMENT '地址文本',
    longitude DECIMAL(10, 7) NOT NULL COMMENT '经度',
    latitude DECIMAL(10, 7) NOT NULL COMMENT '纬度',
    formatted_address VARCHAR(500) COMMENT '格式化地址',

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后访问时间',
    access_count INT DEFAULT 1 COMMENT '访问次数',

    -- 索引
    UNIQUE KEY uk_address (address(150)),
    INDEX idx_coords (longitude, latitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='地址缓存表';
```

---

## 第5步：验证数据库创建成功

### 5.1 查看数据库结构

在 `Databases` 面板中展开：

```
📦 vrp_project
  📁 Tables
    📄 route_cache
    📄 address_cache
```

### 5.2 查看表结构

**方式1**：在表上右键 → 选择 **"Modify Table"**

**方式2**：使用 SQL 查询
```sql
-- 查看 route_cache 表结构
DESCRIBE route_cache;

-- 查看 address_cache 表结构
DESCRIBE address_cache;
```

### 5.3 测试插入数据

```sql
-- 测试插入地址缓存
INSERT INTO address_cache (address, longitude, latitude, formatted_address)
VALUES ('湘潭大学', 112.9152, 27.8792, '湖南省湘潭市雨湖区湘潭大学');

-- 查询测试
SELECT * FROM address_cache;
```

---

## 第6步：配置项目连接信息

### 6.1 打开配置文件

在 DataGrip 中打开：`G:\Vehicle_Routing_Planning_Project\demo_3.0\config.yaml`

### 6.2 检查数据库配置

找到 `database` 部分：

```yaml
database:
  host: "localhost"
  port: 3306
  user: "root"      # ← 确认这个用户名
  password: ""       # ← 如果有密码，填在这里
  database: "vrp_project"
  charset: "utf8mb4"
  pool_size: 10
  max_overflow: 20
```

### 6.3 修改配置（如果需要）

根据您的 MySQL 设置修改：
- `user`：改成您的 MySQL 用户名
- `password`：如果设置了密码，填入密码

保存文件（Ctrl + S）

---

## 🐛 常见问题

### 问题1：MySQL 连接不上

**错误信息**：`Communications link failure`

**解决方法**：

1. 检查 MySQL 服务状态
   - Windows + R → 输入 `services.msc`
   - 找到 MySQL 服务
   - 确保状态是"正在运行"

2. 检查 MySQL 端口
   ```sql
   -- 在 MySQL 命令行中查看端口
   SHOW VARIABLES LIKE 'port';
   ```

3. 检查防火墙
   - 临时关闭防火墙测试
   - 或添加 MySQL 端口（默认 3306）到允许列表

### 问题2：忘记 MySQL 密码

**解决方法**：

1. 停止 MySQL 服务
2. 以管理员身份打开命令行
3. 切换到 MySQL 的 bin 目录
   ```bash
   cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"
   ```
4. 跳过权限验证启动 MySQL
   ```bash
   mysqld --console --skip-grant-tables --shared-memory
   ```
5. 新开一个命令行窗口，连接 MySQL 并重置密码
   ```bash
   mysql -u root
   USE mysql;
   UPDATE user SET authentication_string = '' WHERE user = 'root';
   FLUSH PRIVILEGES;
   ```
6. 重启 MySQL 服务

### 问题3：中文字符乱码

**错误现象**：插入中文后显示为问号或乱码

**解决方法**：
```sql
-- 查看当前字符集
SHOW VARIABLES LIKE 'character%';

-- 应该确保是 utf8mb4
```

---

## ✅ 完成检查清单

完成以上步骤后，您应该能够：

- [ ] 成功连接到 MySQL 数据库
- [ ] 看到 `vrp_project` 数据库
- [ ] 数据库中有两个表：`route_cache`、`address_cache`
- [ ] 能执行 SQL 查询并看到结果
- [ ] `config.yaml` 中的数据库配置正确

---

## 🎯 下一步

数据库配置完成后：

1. 返回 [README.md](README.md) 继续执行"快速开始"步骤
2. 启动 Flask 应用
3. 访问 Web 界面

---

## 📖 数据库管理常用命令

```sql
-- 查看所有数据库
SHOW DATABASES;

-- 使用数据库
USE vrp_project;

-- 查看所有表
SHOW TABLES;

-- 查看表结构
DESCRIBE route_cache;

-- 查看表数据
SELECT * FROM route_cache LIMIT 10;

-- 查看缓存统计
SELECT
    COUNT(*) as total_routes,
    SUM(cache_hit_count) as total_hits,
    AVG(cache_hit_count) as avg_hits
FROM route_cache;

-- 清空缓存表
TRUNCATE TABLE route_cache;
TRUNCATE TABLE address_cache;

-- 删除表
DROP TABLE IF EXISTS route_cache;
DROP TABLE IF EXISTS address_cache;
```

---

**需要帮助？**

如果在任何步骤遇到问题，请：
1. 截图当前的 DataGrip 界面
2. 复制错误信息
3. 在项目仓库提交 Issue

**祝您配置顺利！** 🎉
