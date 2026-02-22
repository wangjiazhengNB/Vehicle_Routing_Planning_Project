"""
临时图结构构建器

将高德API返回的polyline路径转换为可用于算法运行的图结构。
"""
from typing import Dict, List, Tuple, Optional
from ..algorithms.distance_utils import haversine_distance


class TemporaryGraphBuilder:
    """临时图构建器

    将高德API返回的路径数据转换为算法可用的图结构。
    """

    def __init__(self):
        """初始化图构建器"""
        self.next_node_id = 1  # 从1开始分配节点ID
        self.coord_to_node = {}  # 坐标到节点ID的映射 {(lat, lng): node_id}

    def build_graph_from_polyline(
        self,
        polyline_str: str,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float
    ) -> Tuple[Dict, Dict]:
        """从polyline字符串构建图结构

        Args:
            polyline_str: 高德API返回的polyline字符串 "lng,lat;lng,lat;..."
            start_lat, start_lng: 起点坐标
            end_lat, end_lng: 终点坐标

        Returns:
            (graph, node_coords)
            graph: 邻接表表示的图 {node_id: {neighbor_id: edge_info}}
            node_coords: 节点坐标 {node_id: (lat, lng)}
        """
        # 解析polyline
        points = self._parse_polyline(polyline_str)

        # 确保起点和终点被包含（即使不在polyline中）
        all_points = []

        # 添加起点
        start_coord = (round(start_lng, 6), round(start_lat, 6))
        all_points.append(start_coord)

        # 添加polyline中的点
        for lng, lat in points:
            coord = (round(lng, 6), round(lat, 6))
            if coord not in all_points:  # 避免重复
                all_points.append(coord)

        # 添加终点
        end_coord = (round(end_lng, 6), round(end_lat, 6))
        if end_coord not in all_points:
            all_points.append(end_coord)

        # 构建图
        graph = {}
        node_coords = {}

        # 重置节点ID计数器（每次构建都从1开始）
        self.next_node_id = 1
        self.coord_to_node = {}

        # 为每个点分配节点ID并构建图
        for i, (lng, lat) in enumerate(all_points):
            coord_key = (round(lat, 6), round(lng, 6))

            # 为新坐标分配节点ID
            if coord_key not in self.coord_to_node:
                node_id = self.next_node_id
                self.coord_to_node[coord_key] = node_id
                self.next_node_id += 1
            else:
                node_id = self.coord_to_node[coord_key]

            # 记录节点坐标
            node_coords[node_id] = (lat, lng)

            # 初始化邻接表
            if node_id not in graph:
                graph[node_id] = {}

        # 添加边（连接相邻节点）
        for i in range(len(all_points) - 1):
            lng1, lat1 = all_points[i]
            lng2, lat2 = all_points[i + 1]

            coord_key1 = (round(lat1, 6), round(lng1, 6))
            coord_key2 = (round(lat2, 6), round(lng2, 6))

            node_id1 = self.coord_to_node[coord_key1]
            node_id2 = self.coord_to_node[coord_key2]

            # 计算距离
            distance = haversine_distance(lng1, lat1, lng2, lat2)

            # 创建边信息
            edge_info = {
                'distance': distance,
                'congestion': 0.3,  # 默认拥堵指数
                'construction': 0  # 默认无施工
            }

            # 添加双向边（无向图）
            graph[node_id1][node_id2] = edge_info
            graph[node_id2][node_id1] = edge_info

        return graph, node_coords

    def build_graph_from_amap_response(
        self,
        amap_data: Dict
    ) -> Tuple[Dict, Dict, Dict]:
        """从高德API响应构建图

        Args:
            amap_data: 高德API返回的数据（简化格式或完整格式）

        Returns:
            (graph, node_coords, metadata)
            graph: 图结构
            node_coords: 节点坐标
            metadata: 元数据（距离、时间等）
        """
        # Handle simplified format from amap_service.get_driving_route()
        if 'coords' in amap_data:
            coords = amap_data.get('coords', [])
            if not coords:
                return {}, {}, {}

            # Build polyline from coords
            polyline_parts = []
            for lat, lng in coords:
                polyline_parts.append(f"{lng},{lat}")
            combined_polyline = ';'.join(polyline_parts)

            # Extract start and end from coords
            start_lat, start_lng = coords[0]
            end_lat, end_lng = coords[-1]

            # Build graph
            graph, node_coords = self.build_graph_from_polyline(
                combined_polyline,
                start_lat, start_lng,
                end_lat, end_lng
            )

            # Metadata
            metadata = {
                'distance': amap_data.get('distance', 0),
                'duration': amap_data.get('duration', 0),
                'polyline': combined_polyline
            }

            return graph, node_coords, metadata

        # Handle full Amap API response format
        route = amap_data.get('route', {})
        if not route:
            return {}, {}, {}

        paths = route.get('paths', [])
        if not paths:
            return {}, {}, {}

        path = paths[0]  # 使用第一条路径

        # 提取polyline（从steps中合并）
        polylines = []
        for step in path.get('steps', []):
            polyline = step.get('polyline', '')
            if polyline:
                polylines.append(polyline)

        combined_polyline = ';'.join(polylines)

        # 提取起点和终点坐标
        # 从polyline的第一个和最后一个点获取
        all_points = []
        for polyline in polylines:
            all_points.extend(self._parse_polyline(polyline))

        if not all_points:
            return {}, {}, {}

        start_lng, start_lat = all_points[0]
        end_lng, end_lat = all_points[-1]

        # 构建图
        graph, node_coords = self.build_graph_from_polyline(
            combined_polyline,
            start_lat, start_lng,
            end_lat, end_lng
        )

        # 元数据
        metadata = {
            'distance': path.get('distance', 0),
            'duration': path.get('duration', 0),
            'steps': path.get('steps', []),
            'polyline': combined_polyline
        }

        return graph, node_coords, metadata

    def _parse_polyline(self, polyline_str: str) -> List[Tuple[float, float]]:
        """解析polyline字符串为坐标点列表

        Args:
            polyline_str: "lng,lat;lng,lat;..." 格式的字符串

        Returns:
            [(lng, lat), ...] 坐标点列表
        """
        points = []
        for point_str in polyline_str.split(';'):
            point_str = point_str.strip()
            if point_str:
                try:
                    parts = point_str.split(',')
                    if len(parts) == 2:
                        lng, lat = map(float, parts)
                        points.append((lng, lat))
                except ValueError:
                    continue
        return points

    def build_multi_route_graph(self, routes_data: List[Dict]) -> Tuple[Dict, Dict, Dict]:
        """从多条路径构建有分支的图结构

        Args:
            routes_data: 高德API返回的多条路径数据列表，每条路径包含:
                - coords: 坐标列表 [(lat, lng), ...]
                - strategy: 策略ID (或 route_type)
                - route_type: 路线类型 (direct, waypoint_0, waypoint_1, etc.)
                - route_name: 路线名称
                - distance, duration 等

        Returns:
            (graph, node_coords, route_info)
            graph: 图结构（多条路径合并）
            node_coords: 节点坐标 {node_id: (lat, lng)}
            route_info: 每条路径的信息 {route_key: {'path': [...], 'congestion': ...}}
        """
        graph = {}
        node_coords = {}
        route_info = {}

        # 重置节点ID计数器
        self.next_node_id = 1
        self.coord_to_node = {}

        # 为每条路径分配节点ID并构建边
        for route_idx, route in enumerate(routes_data):
            coords = route["coords"]

            # 使用 route_type 或 strategy 作为唯一标识
            route_key = route.get('route_type', f"route_{route_idx}")
            strategy = route.get("strategy", route_idx)

            route_path = []

            # 为每个坐标点分配节点ID
            for lat, lng in coords:
                coord_key = (round(lat, 6), round(lng, 6))

                # 为新坐标分配节点ID
                if coord_key not in self.coord_to_node:
                    node_id = self.next_node_id
                    self.coord_to_node[coord_key] = node_id
                    node_coords[node_id] = (lat, lng)
                    self.next_node_id += 1
                else:
                    node_id = self.coord_to_node[coord_key]

                route_path.append(node_id)

                # 初始化邻接表
                if node_id not in graph:
                    graph[node_id] = {}

            # 添加路径内的边（使用策略相关的拥堵属性）
            # 绕行路线拥堵较低以鼓励算法选择
            if 'waypoint' in route_key:
                route_congestion = 0.15  # 绕行路线低拥堵
            elif 'direct' in route_key:
                route_congestion = 0.30  # 直达路线中等拥堵
            else:
                route_congestion = self._get_congestion_by_strategy(strategy)

            for i in range(len(route_path) - 1):
                u, v = route_path[i], route_path[i + 1]

                # 如果边不存在，创建新边
                if v not in graph[u]:
                    lat1, lng1 = node_coords[u]
                    lat2, lng2 = node_coords[v]
                    distance = haversine_distance(lng1, lat1, lng2, lat2)

                    edge_info = {
                        'distance': distance,
                        'congestion': route_congestion,
                        'construction': 0,
                        'strategy': strategy,
                        'route_type': route_key
                    }

                    # 添加双向边
                    graph[u][v] = edge_info
                    graph[v][u] = edge_info

            # 记录路径信息
            route_info[route_key] = {
                'path': route_path,
                'route_name': route.get('route_name', route.get('strategy_name', f'路线{route_idx}')),
                'distance': route.get('distance', 0),
                'duration': route.get('duration', 0),
                'congestion': route_congestion,
                'strategy': strategy
            }

        return graph, node_coords, route_info

    def _get_congestion_by_strategy(self, strategy: int) -> float:
        """根据策略分配拥堵指数

        不同策略模拟不同的交通状况，使算法可以选择不同路径
        """
        return {
            0: 0.15,  # 速度优先 - 低拥堵
            1: 0.30,  # 费用优先 - 中等拥堵
            2: 0.50,  # 距离优先 - 较高拥堵
            3: 0.60,  # 不走高速 - 高拥堵
            4: 0.20   # 躲避拥堵 - 低拥堵
        }.get(strategy, 0.30)

    def find_nearest_node_in_graph(
        self,
        graph: Dict,
        node_coords: Dict,
        target_lat: float,
        target_lng: float
    ) -> Optional[int]:
        """在图中查找距离目标坐标最近的节点

        Args:
            graph: 图结构
            node_coords: 节点坐标 {node_id: (lat, lng)}
            target_lat, target_lng: 目标坐标

        Returns:
            最近的节点ID，如果图为空返回None
        """
        if not node_coords:
            return None

        nearest_node = None
        min_distance = float('inf')

        for node_id, (lat, lng) in node_coords.items():
            dist = haversine_distance(target_lng, target_lat, lng, lat)
            if dist < min_distance:
                min_distance = dist
                nearest_node = node_id

        return nearest_node


# 全局实例
_graph_builder = None


def get_graph_builder() -> TemporaryGraphBuilder:
    """获取全局图构建器实例"""
    global _graph_builder
    if _graph_builder is None:
        _graph_builder = TemporaryGraphBuilder()
    return _graph_builder
