"""Dijkstra最短路径算法实现"""

import heapq
import time
from typing import List, Tuple, Dict, Optional

from .base import PathAlgorithm, AlgorithmResult
from .cost_calculator import CostCalculator


class DijkstraAlgorithm(PathAlgorithm):
    """Dijkstra最短路径算法

    使用优先队列实现的经典Dijkstra算法，用于寻找图中最短路径。
    适用于非负权重的有向图或无向图。
    """

    def __init__(self):
        """初始化Dijkstra算法"""
        super().__init__("Dijkstra")
        self.reset_metrics()

    def find_path(self, graph: Dict, start: int, end: int,
                  objectives: List[str] = None, weights: Dict = None) -> Tuple[List[int], float]:
        """
        使用Dijkstra算法寻找最短路径

        Args:
            graph: 图结构，邻接表表示 {node_id: {neighbor_id: edge_info}}
                   edge_info 包含 'distance', 'congestion', 'construction' 等字段
            start: 起点节点ID
            end: 终点节点ID
            objectives: 优化目标列表，默认为 ['distance']（最短距离）
                       Dijkstra默认优化距离，但可以通过自定义成本函数优化其他目标
            weights: 各目标的权重字典

        Returns:
            (path, cost)
            path: 路径节点列表 [start, ..., end]，如果找不到路径则为空列表
            cost: 路径总成本
        """
        start_time = time.time()

        # 如果没有提供权重且使用多目标优化，使用默认权重
        if weights is None and objectives is not None and len(objectives) > 1:
            weights = CostCalculator.DEFAULT_WEIGHTS.copy()

        # 初始化
        distances = {node: float('inf') for node in graph}
        distances[start] = 0
        previous = {node: None for node in graph}
        visited = set()

        # 优先队列 (cost, node)
        pq = [(0, start)]

        # 如果指定了多个目标，使用成本计算器
        use_cost_calculator = objectives is not None and len(objectives) > 1

        while pq:
            current_cost, current_node = heapq.heappop(pq)

            # 跳过已访问节点
            if current_node in visited:
                continue

            visited.add(current_node)
            self.last_nodes_visited += 1

            # 到达终点，提前退出
            if current_node == end:
                break

            # 遍历邻居
            for neighbor, edge_info in graph.get(current_node, {}).items():
                if neighbor in visited:
                    continue

                # 计算新成本
                if use_cost_calculator:
                    # 使用成本计算器计算边成本
                    edge_cost = CostCalculator.calculate_edge_cost(
                        edge_info, objectives, weights
                    )
                else:
                    # 默认使用距离
                    edge_cost = edge_info.get('distance', float('inf'))

                new_cost = current_cost + edge_cost

                # 如果找到更短的路径
                if new_cost < distances[neighbor]:
                    distances[neighbor] = new_cost
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (new_cost, neighbor))

        # 记录执行时间
        self.last_execution_time = (time.time() - start_time) * 1000  # 毫秒

        # 构建路径
        path = self._reconstruct_path(previous, start, end)
        total_cost = distances[end]

        return path, total_cost

    def _reconstruct_path(self, previous: Dict, start: int, end: int) -> List[int]:
        """
        从previous字典重构路径

        Args:
            previous: 前驱节点字典 {node_id: previous_node_id}
            start: 起点节点ID
            end: 终点节点ID

        Returns:
            路径节点列表，如果找不到路径则为空列表
        """
        if previous[end] is None and start != end:
            return []  # 无路径

        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        return path

    def get_metrics(self) -> Dict:
        """
        获取算法执行指标

        Returns:
            指标字典，包含:
            - algorithm: 算法名称
            - execution_time_ms: 执行时间（毫秒）
            - nodes_visited: 访问的节点数
        """
        return {
            "algorithm": self.name,
            "execution_time_ms": round(self.last_execution_time, 3),
            "nodes_visited": self.last_nodes_visited
        }

    def reset_metrics(self):
        """重置执行指标"""
        super().reset_metrics()
        self.last_execution_time = 0.0
        self.last_nodes_visited = 0

    def find_path_with_result(self, graph: Dict, start: int, end: int,
                             objectives: List[str] = None) -> AlgorithmResult:
        """
        寻找路径并返回AlgorithmResult对象

        Args:
            graph: 图结构
            start: 起点节点ID
            end: 终点节点ID
            objectives: 优化目标列表

        Returns:
            AlgorithmResult对象
        """
        path, cost = self.find_path(graph, start, end, objectives)
        return AlgorithmResult(self.name, path, cost, self.get_metrics())


# 便捷函数
def dijkstra(graph: Dict, start: int, end: int,
             objectives: List[str] = None, weights: Dict = None) -> Tuple[List[int], float]:
    """
    Dijkstra算法的便捷函数

    Args:
        graph: 图结构
        start: 起点节点ID
        end: 终点节点ID
        objectives: 优化目标列表
        weights: 各目标的权重字典

    Returns:
        (path, cost) 路径和成本
    """
    algo = DijkstraAlgorithm()
    return algo.find_path(graph, start, end, objectives, weights)


def build_graph_from_edges(edges: List[Dict], directed: bool = False) -> Dict:
    """
    从边列表构建图

    Args:
        edges: 边列表，每个元素是包含 start_node_id, end_node_id, distance 等字段的字典
        directed: 是否为有向图，默认为无向图

    Returns:
        邻接表表示的图 {node_id: {neighbor_id: edge_info}}
    """
    graph = {}

    for edge in edges:
        start = edge['start_node_id']
        end = edge['end_node_id']

        # 创建节点
        if start not in graph:
            graph[start] = {}
        if end not in graph:
            graph[end] = {}

        # 添加正向边
        graph[start][end] = {
            'distance': edge.get('distance', float('inf')),
            'congestion': edge.get('congestion', 0.5),
            'construction': edge.get('construction', 0)
        }

        # 如果是无向图，添加反向边
        if not directed:
            graph[end][start] = {
                'distance': edge.get('distance', float('inf')),
                'congestion': edge.get('congestion', 0.5),
                'construction': edge.get('construction', 0)
            }

    return graph
