"""
算法对比测试脚本 v3.0

功能：
1. 测试三种算法（Dijkstra/A*/PSO）在同一场景下的表现
2. 性能指标对比
3. 多目标优化对比
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.algorithms.dijkstra import DijkstraAlgorithm
from src.algorithms.astar import AStarAlgorithm
from src.algorithms.pso import PSOAlgorithm


class TestAlgorithmComparison:
    """算法对比测试类"""

    @pytest.fixture
    def sample_graph(self):
        """创建测试用的简单图结构"""
        # 节点坐标
        node_coords = {
            1: (27.860, 112.910),  # 湘潭火车站
            2: (27.848, 112.929),  # 湖南工程学院
            3: (27.904, 112.908),  # 湘潭大学
            4: (27.830, 112.930),  # 岳塘区政府
            5: (27.840, 112.925),  # 湘潭市中心医院
        }

        # 边列表（模拟道路网络）
        edges = [
            # 1 -> 其他节点
            (1, 2, {"distance": 2000, "congestion": 0.3, "construction": 0}),
            (1, 3, {"distance": 5000, "congestion": 0.4, "construction": 0}),
            (1, 4, {"distance": 3500, "congestion": 0.3, "construction": 0}),
            (1, 5, {"distance": 1500, "congestion": 0.2, "construction": 0}),

            # 2 -> 其他节点
            (2, 3, {"distance": 4500, "congestion": 0.3, "construction": 0}),
            (2, 4, {"distance": 1800, "congestion": 0.4, "construction": 0}),
            (2, 5, {"distance": 1200, "congestion": 0.3, "construction": 0}),

            # 3 -> 其他节点
            (3, 4, {"distance": 6000, "congestion": 0.3, "construction": 0}),
            (3, 5, {"distance": 5500, "congestion": 0.4, "construction": 0}),

            # 4 -> 5
            (4, 5, {"distance": 2000, "congestion": 0.3, "construction": 0}),
        ]

        # 构建邻接表
        graph = {}
        for start, end, info in edges:
            if start not in graph:
                graph[start] = {}
            graph[start][end] = info

            # 添加反向边（双向道路）
            if end not in graph:
                graph[end] = {}
            graph[end][start] = info

        return graph, node_coords

    def test_same_route_comparison(self, sample_graph):
        """测试1：同一路线三种算法对比"""
        graph, node_coords = sample_graph

        algorithms = {
            "Dijkstra": DijkstraAlgorithm(),
            "A*": AStarAlgorithm(heuristic='euclidean', node_coords=node_coords),
            "PSO": PSOAlgorithm(config={"population_size": 30, "max_iterations": 50})
        }

        results = {}
        start, end = 1, 4

        print("\n" + "=" * 60)
        print("测试1：同一路线算法对比 (节点1 -> 节点4)")
        print("=" * 60)

        for name, algo in algorithms.items():
            result = algo.find_path(graph, start, end, ['distance'])
            results[name] = result

            print(f"\n{name}:")
            print(f"  路径: {result.path}")
            print(f"  距离: {result.cost:.1f}m")
            print(f"  访问节点: {result.metrics.get('nodes_visited', 'N/A')}")
            print(f"  执行时间: {result.execution_time:.3f}ms")

        # 验证所有算法都找到路径
        for name, result in results.items():
            assert result.path is not None, f"{name} 未能找到路径"
            assert len(result.path) > 0, f"{name} 路径为空"

        # 验证Dijkstra和A*的距离应该相同（都是最短路径算法）
        dijkstra_cost = results["Dijkstra"].cost
        astar_cost = results["A*"].cost
        assert abs(dijkstra_cost - astar_cost) < 1, "Dijkstra和A*的距离应该相同"

    def test_performance_comparison(self, sample_graph):
        """测试2：性能指标对比"""
        graph, node_coords = sample_graph

        algorithms = {
            "Dijkstra": DijkstraAlgorithm(),
            "A*": AStarAlgorithm(heuristic='euclidean', node_coords=node_coords),
            "PSO": PSOAlgorithm(config={"population_size": 30, "max_iterations": 50})
        }

        print("\n" + "=" * 60)
        print("测试2：性能指标对比")
        print("=" * 60)

        # 多次运行取平均值
        runs = 5
        performance = {name: {"time": [], "nodes": []} for name in algorithms.keys()}

        for _ in range(runs):
            for name, algo in algorithms.items():
                result = algo.find_path(graph, 1, 4, ['distance'])
                performance[name]["time"].append(result.execution_time)
                performance[name]["nodes"].append(result.metrics.get('nodes_visited', 0))

        print(f"\n{'算法':<12} {'平均时间(ms)':<15} {'平均访问节点':<15}")
        print("-" * 50)

        for name, stats in performance.items():
            avg_time = sum(stats["time"]) / len(stats["time"])
            avg_nodes = sum(stats["nodes"]) / len(stats["nodes"])
            print(f"{name:<12} {avg_time:<15.3f} {avg_nodes:<15.1f}")

    def test_multi_objective_comparison(self, sample_graph):
        """测试3：多目标优化对比"""
        graph, node_coords = sample_graph

        # PSO支持多目标优化
        pso = PSOAlgorithm(config={"population_size": 50, "max_iterations": 100})

        objective_combinations = [
            (['distance'], "只考虑距离"),
            (['distance', 'congestion'], "距离+拥堵"),
            (['distance', 'congestion', 'construction'], "综合考虑"),
        ]

        print("\n" + "=" * 60)
        print("测试3：PSO多目标优化对比")
        print("=" * 60)

        for objectives, desc in objective_combinations:
            result = pso.find_path(graph, 1, 4, objectives)
            print(f"\n{desc}:")
            print(f"  路径: {result.path}")
            print(f"  成本: {result.cost:.1f}")


if __name__ == "__main__":
    # 直接运行此文件执行测试
    pytest.main([__file__, "-v", "-s"])
