"""成本计算模块

提供单目标和多目标路径成本计算功能
"""

from typing import List, Dict, Tuple
from .distance_utils import calculate_distance


class CostCalculator:
    """成本计算器

    支持单目标和多目标路径成本计算
    """

    # 默认权重配置
    DEFAULT_WEIGHTS = {
        'distance': 0.5,      # 距离权重
        'congestion': 0.3,   # 拥堵权重
        'construction': 0.2  # 施工权重
    }

    @staticmethod
    def calculate_edge_cost(edge_info: Dict, objectives: List[str] = None,
                           weights: Dict[str, float] = None) -> float:
        """
        计算单条边的成本

        Args:
            edge_info: 边信息字典，包含 'distance', 'congestion', 'construction' 等字段
            objectives: 优化目标列表，默认为 ['distance']
            weights: 各目标的权重配置

        Returns:
            边的成本
        """
        if objectives is None:
            objectives = ['distance']

        if weights is None:
            weights = CostCalculator.DEFAULT_WEIGHTS.copy()

        # 只计算指定目标的成本
        total_cost = 0.0
        for obj in objectives:
            cost = CostCalculator._get_objective_cost(edge_info, obj)
            weight = weights.get(obj, 1.0)
            total_cost += cost * weight

        return total_cost

    @staticmethod
    def calculate_path_cost(path: List[int], graph: Dict, objectives: List[str] = None,
                          weights: Dict[str, float] = None) -> float:
        """
        计算路径的总成本

        Args:
            path: 路径节点列表 [node1, node2, ..., nodeN]
            graph: 图结构 {node_id: {neighbor_id: edge_info}}
            objectives: 优化目标列表，默认为 ['distance']
            weights: 各目标的权重配置

        Returns:
            路径的总成本
        """
        if len(path) < 2:
            return 0.0

        if objectives is None:
            objectives = ['distance']

        total_cost = 0.0
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]

            # 获取边信息
            if u not in graph or v not in graph[u]:
                raise ValueError(f"图中不存在边 {u} -> {v}")

            edge_info = graph[u][v]
            edge_cost = CostCalculator.calculate_edge_cost(
                edge_info, objectives, weights
            )
            total_cost += edge_cost

        return total_cost

    @staticmethod
    def calculate_path_distance(path: List[int], graph: Dict) -> float:
        """
        计算路径的总距离

        Args:
            path: 路径节点列表
            graph: 图结构

        Returns:
            路径的总距离（米）
        """
        return CostCalculator.calculate_path_cost(path, graph, ['distance'])

    @staticmethod
    def calculate_multi_objective_cost(path: List[int], graph: Dict,
                                      weights: Dict[str, float] = None) -> Tuple[float, Dict]:
        """
        计算路径的多目标成本和各分项成本

        Args:
            path: 路径节点列表
            graph: 图结构
            weights: 各目标的权重配置

        Returns:
            (total_cost, detail_costs)
            total_cost: 加权总成本
            detail_costs: 各分项成本 {'distance': ..., 'congestion': ..., 'construction': ...}
        """
        if weights is None:
            weights = CostCalculator.DEFAULT_WEIGHTS.copy()

        detail_costs = {
            'distance': 0.0,
            'congestion': 0.0,
            'construction': 0.0
        }

        # 计算加权总成本 - 使用 calculate_edge_cost 确保与算法内部一致
        total_cost = 0.0
        objectives = list(weights.keys())

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge_info = graph[u][v]

            # 记录原始值（用于显示）
            detail_costs['distance'] += float(edge_info.get('distance', 0))
            detail_costs['congestion'] += float(edge_info.get('congestion', 0))
            detail_costs['construction'] += float(edge_info.get('construction', 0))

            # 使用 calculate_edge_cost 计算加权成本（与算法内部一致）
            edge_cost = CostCalculator.calculate_edge_cost(edge_info, objectives, weights)
            total_cost += edge_cost

        return total_cost, detail_costs

    @staticmethod
    def _get_objective_cost(edge_info: Dict, objective: str) -> float:
        """
        获取单个目标的成本

        Args:
            edge_info: 边信息字典
            objective: 目标名称 ('distance', 'congestion', 'construction')

        Returns:
            该目标的成本
        """
        if objective == 'distance':
            # 确保返回float类型
            return float(edge_info.get('distance', 0))
        elif objective == 'congestion':
            # 拥堵成本 = 拥堵指数 × 距离
            congestion = float(edge_info.get('congestion', 0))
            distance = float(edge_info.get('distance', 0))
            return congestion * distance
        elif objective == 'construction':
            # 施工成本 = 施工惩罚 × 距离
            construction = float(edge_info.get('construction', 0))
            distance = float(edge_info.get('distance', 0))
            # 施工惩罚系数
            penalty = 5.0 if construction > 0 else 0
            return penalty * distance
        else:
            raise ValueError(f"未知的目标: {objective}")


def calculate_total_cost(route_data: List[Dict], weights: Dict[str, float] = None) -> float:
    """
    计算路由总成本（兼容 demo_1.0 的格式）

    Args:
        route_data: 路由数据列表，每个元素是包含 distance, congestion, construction 的字典
        weights: 权重配置

    Returns:
        总成本
    """
    if weights is None:
        weights = CostCalculator.DEFAULT_WEIGHTS.copy()

    total_cost = 0.0
    for segment in route_data:
        distance = segment.get('distance', 0)
        congestion = segment.get('congestion', 0)
        construction = segment.get('construction', 0)

        # 施工惩罚
        construction_cost = 5 if construction == 1 else 0

        total_cost += (
            distance * weights['distance'] +
            congestion * weights['congestion'] +
            construction_cost * weights['construction']
        )

    return total_cost
