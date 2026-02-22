"""算法基类模块"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Optional


class PathAlgorithm(ABC):
    """路径规划算法基类

    所有路径规划算法都应该继承这个基类，并实现抽象方法。
    这样可以方便地扩展新的算法，并统一算法接口。
    """

    def __init__(self, name: str):
        """
        初始化算法

        Args:
            name: 算法名称
        """
        self.name = name
        self.last_execution_time = 0.0  # 上次执行时间（毫秒）
        self.last_nodes_visited = 0      # 上次访问节点数

    @abstractmethod
    def find_path(self, graph: Dict, start: int, end: int,
                  objectives: List[str] = None) -> Tuple[List[int], float]:
        """
        寻找路径

        Args:
            graph: 图结构，邻接表表示 {node_id: {neighbor_id: edge_data}}
                   edge_data 是一个字典，包含 'distance', 'congestion', 'construction' 等字段
            start: 起点节点ID
            end: 终点节点ID
            objectives: 优化目标列表，如 ['distance', 'congestion', 'construction']
                       默认为 ['distance']，即只考虑距离

        Returns:
            (path_nodes, total_cost)
            path_nodes: 路径节点列表 [start, ..., end]
            total_cost: 路径总成本
        """
        pass

    @abstractmethod
    def get_metrics(self) -> Dict:
        """
        获取算法执行指标

        Returns:
            指标字典，包含:
            - algorithm: 算法名称
            - execution_time_ms: 执行时间（毫秒）
            - nodes_visited: 访问的节点数
            以及其他算法特定的指标
        """
        pass

    def reset_metrics(self):
        """重置执行指标"""
        self.last_execution_time = 0.0
        self.last_nodes_visited = 0

    def __repr__(self):
        return f"<PathAlgorithm(name='{self.name}')>"


class AlgorithmResult:
    """算法结果类

    封装算法执行的结果，方便统一处理
    """

    def __init__(self, algorithm_name: str, path: List[int], cost: float, metrics: Dict):
        """
        初始化结果

        Args:
            algorithm_name: 算法名称
            path: 路径节点列表
            cost: 路径总成本
            metrics: 算法执行指标
        """
        self.algorithm_name = algorithm_name
        self.path = path
        self.cost = cost
        self.metrics = metrics
        self.success = len(path) > 0

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'algorithm': self.algorithm_name,
            'path': self.path,
            'cost': self.cost,
            'metrics': self.metrics,
            'success': self.success,
            'path_length': len(self.path)
        }

    def __repr__(self):
        return (f"<AlgorithmResult(algorithm='{self.algorithm_name}', "
                f"cost={self.cost:.2f}, nodes={len(self.path)}, "
                f"success={self.success})>")
