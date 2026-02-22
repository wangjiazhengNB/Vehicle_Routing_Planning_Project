-- 创建路径缓存表
-- 用于缓存高德API返回的路径数据和算法结果

CREATE TABLE IF NOT EXISTS route_cache (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',

    -- 缓存键 (注意: VARCHAR(200)以避免索引长度限制)
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

    -- 图结构数据（序列化为JSON）
    graph_data LONGTEXT COMMENT '临时图结构(JSON格式)',
    node_mapping LONGTEXT COMMENT '节点ID映射关系(JSON)',

    -- 算法结果缓存（序列化为JSON）
    dijkstra_result TEXT COMMENT 'Dijkstra算法结果(JSON)',
    astar_result TEXT COMMENT 'A*算法结果(JSON)',
    pso_result TEXT COMMENT 'PSO算法结果(JSON)',

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后访问时间',
    access_count INT DEFAULT 1 COMMENT '访问次数',
    cache_hit_count INT DEFAULT 0 COMMENT '缓存命中次数',

    -- 索引 (使用前缀索引以避免长度限制)
    UNIQUE KEY uk_route (start_address(150), end_address(150)),
    INDEX idx_coords (start_lat, start_lng, end_lat, end_lng),
    INDEX idx_created (created_at),
    INDEX idx_access (access_count DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路径缓存表';
