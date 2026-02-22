"""
A*启发式搜索算法实现

A*算法是一种高效的路径搜索算法，结合了Dijkstra算法的完备性和
启发式搜索的高效性。它使用启发式函数来估计从当前节点到终点的代价，
从而大大减少需要探索的节点数量。

算法特点：
1. 当启发式函数可采纳（不高于实际代价）时，保证找到最优解
2. 搜索效率通常比Dijkstra高很多
3. 需要额外的节点坐标信息用于启发式计算
"""
import heapq
import time
from typing import List, Tuple, Dict, Optional
from math import radians, cos

from .base import PathAlgorithm
from .cost_calculator import CostCalculator
from .distance_utils import haversine_distance


class AStarAlgorithm(PathAlgorithm):
    """A*启发式搜索算法

    A*算法使用 f(n) = g(n) + h(n) 的评估函数：
    - g(n): 从起点到节点n的实际代价
    - h(n): 从节点n到终点的启发式估计代价
    - f(n): 节点n的总评估代价

    参数说明：
    - heuristic: 启发式函数类型，支持：
        * 'haversine': 使用Haversine公式计算球面距离（最准确）
        * 'euclidean': 使用欧几里得距离（计算较快）
        * 'manhattan': 使用曼哈顿距离（城市道路适用）
    """

    def __init__(self, heuristic: str = 'euclidean', node_coords: Dict = None):
        """
        初始化A*算法

        Args:
            heuristic: 启发式函数类型，默认 'euclidean'
            node_coords: 节点坐标字典 {node_id: (lat, lng)}
                        如果不提供，需要在 find_path 前调用 set_node_coordinates
        """
        super().__init__("A*")
        self.heuristic_type = heuristic
        self.node_coords = node_coords or {}
        self.reset_metrics()

    def set_node_coordinates(self, node_coords: Dict[int, Tuple[float, float]]):
        """
        设置节点坐标

        A*算法需要节点坐标来计算启发式代价。这个方法可以在算法运行前调用，
        以便从外部（如NodeMapper）获取节点坐标。

        Args:
            node_coords: 节点坐标字典 {node_id: (lat, lng)}
        """
        self.node_coords = node_coords

    def find_path(self, graph: Dict, start: int, end: int,
                  objectives: List[str] = None, weights: Dict = None) -> Tuple[List[int], float]:
        """
        使用A*算法寻找最优路径

        Args:
            graph: 图结构，邻接表表示 {node_id: {neighbor_id: edge_info}}
            start: 起点节点ID
            end: 终点节点ID
            objectives: 优化目标列表
            weights: 各目标的权重配置（可选）

        Returns:
            (path, cost) 路径和总成本
        """
        start_time = time.time()

        # 特殊情况处理
        if start == end:
            return [start], 0.0

        if start not in graph or end not in graph:
            return [], float('inf')

        # 如果没有提供weights且是多目标优化，使用默认权重
        if weights is None and objectives is not None and len(objectives) > 1:
            weights = CostCalculator.DEFAULT_WEIGHTS.copy()

        # 初始化g_score（从起点到各节点的实际代价）
        g_scores = {node: float('inf') for node in graph}
        g_scores[start] = 0

        # 初始化f_score（总评估代价）
        f_scores = {node: float('inf') for node in graph}
        f_scores[start] = self._heuristic(start, end)

        # 优先队列：存储 (f_score, node)
        # 使用最小堆来获取f_score最小的节点
        open_set = [(f_scores[start], start)]
        # 用于快速查找节点是否在open_set中
        open_set_nodes = {start}

        # 记录路径：came_from[node] = 前驱节点
        came_from = {}
        # 初始化起点的前驱节点为None
        came_from[start] = None

        # 是否使用多目标成本
        use_cost_calculator = objectives is not None and len(objectives) > 1

        # 主循环
        while open_set:
            # 获取f_score最小的节点
            current_f, current = heapq.heappop(open_set)

            # 如果节点不在open_set_nodes中，说明已被处理过
            if current not in open_set_nodes:
                continue
            open_set_nodes.remove(current)

            # 到达终点，重构路径并返回
            if current == end:
                self.last_execution_time = (time.time() - start_time) * 1000
                path = self._reconstruct_path(came_from, start, end)
                return path, g_scores[end]

            # 更新访问节点计数
            self.last_nodes_visited += 1

            # 遍历当前节点的所有邻居
            for neighbor, edge_info in graph.get(current, {}).items():
                # 计算边成本
                if use_cost_calculator:
                    edge_cost = CostCalculator.calculate_edge_cost(edge_info, objectives, weights)
                else:
                    edge_cost = edge_info.get('distance', float('inf'))

                # 计算通过当前节点到达邻居的代价
                tentative_g = g_scores[current] + edge_cost

                # 如果找到了更短的路径
                if tentative_g < g_scores[neighbor]:
                    # 更新路径
                    came_from[neighbor] = current
                    # 更新g_score
                    g_scores[neighbor] = tentative_g
                    # 计算f_score
                    h_score = self._heuristic(neighbor, end)
                    f_scores[neighbor] = tentative_g + h_score

                    # 如果邻居不在open_set中，加入
                    if neighbor not in open_set_nodes:
                        heapq.heappush(open_set, (f_scores[neighbor], neighbor))
                        open_set_nodes.add(neighbor)

        # 无法到达终点
        self.last_execution_time = (time.time() - start_time) * 1000
        return [], float('inf')

    def _heuristic(self, node: int, end: int) -> float:
        """
        计算启发式代价

        启发式函数 h(n) 估计从节点n到终点的代价。
        为了保证A*算法的可采纳性（找到最优解），
        启发式函数必须不能高估实际代价。

        Args:
            node: 当前节点ID
            end: 终点节点ID

        Returns:
            启发式代价估计值
        """
        # 如果节点坐标不可用，返回0（退化为Dijkstra）
        if node not in self.node_coords or end not in self.node_coords:
            return 0

        lat1, lng1 = float(self.node_coords[node][0]), float(self.node_coords[node][1])
        lat2, lng2 = float(self.node_coords[end][0]), float(self.node_coords[end][1])

        # 根据配置的启发式类型计算
        if self.heuristic_type == 'haversine':
            # Haversine距离：球面上两点间的大圆距离
            return haversine_distance(lng1, lat1, lng2, lat2)
        elif self.heuristic_type == 'euclidean':
            # 欧几里得距离：直线距离近似
            # 将经纬度差转换为米（粗略估计）
            lat_diff = (lat2 - lat1) * 111000  # 1度纬度约111km
            lng_diff = (lng2 - lng1) * 111000 * cos(radians(lat1))  # 添加cos(lat)因子考虑纬度影响
            return (lat_diff ** 2 + lng_diff ** 2) ** 0.5
        else:  # manhattan
            # 曼哈顿距离：折线距离
            lat_diff = abs(lat2 - lat1) * 111000
            lng_diff = abs(lng2 - lng1) * 111000
            return lat_diff + lng_diff

    def _reconstruct_path(self, came_from: Dict, start: int, end: int) -> List[int]:
        """
        从came_from字典重构路径

        Args:
            came_from: 前驱节点字典
            start: 起点节点ID
            end: 终点节点ID

        Returns:
            路径节点列表
        """
        if end not in came_from and start != end:
            return []

        # 从终点回溯到起点
        path = [end]
        current = end
        while current != start:
            current = came_from[current]
            path.append(current)

        # 反转得到正向路径
        path.reverse()
        return path

    def get_metrics(self) -> Dict:
        """
        获取算法执行指标

        Returns:
            指标字典
        """
        return {
            "algorithm": self.name,
            "execution_time_ms": round(self.last_execution_time, 3),
            "nodes_visited": self.last_nodes_visited,
            "heuristic": self.heuristic_type
        }

    def reset_metrics(self):
        """重置执行指标"""
        super().reset_metrics()
        self.last_execution_time = 0.0
        self.last_nodes_visited = 0


# 便捷函数
def astar(graph: Dict, start: int, end: int,
           objectives: List[str] = None, weights: Dict = None, heuristic: str = 'euclidean',
           node_coords: Dict = None) -> Tuple[List[int], float]:
    """
    A*算法的便捷函数

    Args:
        graph: 图结构
        start: 起点节点ID
        end: 终点节点ID
        objectives: 优化目标列表
        weights: 各目标的权重配置
        heuristic: 启发式函数类型
        node_coords: 节点坐标字典

    Returns:
        (path, cost) 路径和成本
    """
    algo = AStarAlgorithm(heuristic, node_coords)
    return algo.find_path(graph, start, end, objectives, weights)
