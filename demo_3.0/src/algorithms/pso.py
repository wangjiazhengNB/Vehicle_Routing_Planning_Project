"""
PSO粒子群优化算法实现

粒子群优化（Particle Swarm Optimization, PSO）是一种基于群体智能的优化算法，
通过模拟鸟群觅食的行为来寻找最优解。

在路径规划中，每个粒子代表一条可能的路径，通过迭代优化找到最优路径。
"""
import time
import random
from typing import List, Tuple, Dict, Optional

from .base import PathAlgorithm
from .cost_calculator import CostCalculator


class PSOAlgorithm(PathAlgorithm):
    """粒子群优化路径规划算法

    算法特点：
    1. 全局搜索能力强，不易陷入局部最优
    2. 参数较少，易于实现
    3. 适用于复杂的组合优化问题

    参数说明：
    - population_size: 种群大小（粒子数量）
    - max_iterations: 最大迭代次数
    - inertia_weight: 惯性权重，控制粒子保持原速度的程度
    - cognitive_weight: 认知权重，控制粒子向个体历史最优移动的程度
    - social_weight: 社会权重，控制粒子向全局最优移动的程度
    """

    def __init__(self, config: Dict = None):
        """
        初始化PSO算法

        Args:
            config: 配置字典，包含以下参数（可选，有默认值）：
                - population_size: 种群大小，默认50
                - max_iterations: 最大迭代次数，默认100
                - inertia_weight: 惯性权重，默认0.7
                - cognitive_weight: 认知权重，默认1.5
                - social_weight: 社会权重，默认1.5
        """
        super().__init__("PSO")
        config = config or {}
        self.population_size = config.get('population_size', 50)
        self.max_iterations = config.get('max_iterations', 100)
        self.w = config.get('inertia_weight', 0.7)
        self.c1 = config.get('cognitive_weight', 1.5)
        self.c2 = config.get('social_weight', 1.5)

        self.convergence_history = []  # 收敛历史记录
        self.reset_metrics()

    def find_path(self, graph: Dict, start: int, end: int,
                  objectives: List[str] = None, weights: Dict = None) -> Tuple[List[int], float]:
        """
        使用PSO算法寻找最优路径

        Args:
            graph: 图结构，邻接表表示 {node_id: {neighbor_id: edge_info}}
            start: 起点节点ID
            end: 终点节点ID
            objectives: 优化目标列表
            weights: 各目标的权重字典

        Returns:
            (path, cost) 路径和总成本
        """
        start_time = time.time()

        # 特殊情况处理
        if start == end:
            return [start], 0.0

        # 如果没有提供权重且使用多目标优化，使用默认权重
        if weights is None and objectives is not None and len(objectives) > 1:
            weights = CostCalculator.DEFAULT_WEIGHTS.copy()

        # 1. 初始化种群
        particles = self._initialize_population(graph, start, end)
        global_best_path = None
        global_best_fitness = float('inf')

        # 2. 迭代优化
        for iteration in range(self.max_iterations):
            iteration_best_fitness = float('inf')

            # 评估所有粒子
            for particle in particles:
                fitness = self._evaluate_fitness(particle, graph, objectives, weights)

                # 更新个体最优
                if fitness < particle.best_fitness:
                    particle.best_path = particle.path.copy()
                    particle.best_fitness = fitness

                # 更新全局最优
                if fitness < global_best_fitness:
                    global_best_path = particle.path.copy()
                    global_best_fitness = fitness

                # 记录本次迭代的最优值
                if fitness < iteration_best_fitness:
                    iteration_best_fitness = fitness

            # 记录收敛历史
            self.convergence_history.append(iteration_best_fitness)

            # 更新粒子位置（变异操作）
            self._update_particles(particles, global_best_path, graph)

            # 记录访问的节点数
            self.last_nodes_visited += len(particles)

            # 提前终止：如果连续多次迭代没有改进
            if iteration > 10 and len(set(self.convergence_history[-10:])) == 1:
                break

        # 记录执行时间
        self.last_execution_time = (time.time() - start_time) * 1000

        if global_best_path:
            return global_best_path, global_best_fitness
        return [], float('inf')

    def _initialize_population(self, graph: Dict, start: int, end: int) -> List['Particle']:
        """
        初始化粒子种群

        使用随机游走生成初始路径，增加种群多样性。

        Args:
            graph: 图结构
            start: 起点节点ID
            end: 终点节点ID

        Returns:
            粒子列表
        """
        particles = []

        # 生成多样化的初始种群
        # 30%使用最短路径优先策略，70%使用随机游走
        for i in range(self.population_size):
            if i < self.population_size * 0.3:
                path = self._greedy_path(graph, start, end)
            else:
                path = self._random_walk(graph, start, end)

            # 确保路径有效
            if not path or path[-1] != end:
                path = [start, end]

            particle = Particle(path)
            particles.append(particle)

        return particles

    def _greedy_path(self, graph: Dict, start: int, end: int) -> List[int]:
        """
        使用贪婪策略生成路径（选择最短边）

        Args:
            graph: 图结构
            start: 起点节点ID
            end: 终点节点ID

        Returns:
            路径节点列表
        """
        if start == end:
            return [start]

        path = [start]
        visited = {start}
        current = start

        max_steps = len(graph) * 2

        for _ in range(max_steps):
            if current == end:
                break

            neighbors = list(graph.get(current, {}).keys())
            unvisited = [n for n in neighbors if n not in visited]

            if not unvisited:
                break

            # 选择距离最短的未访问邻居
            best_neighbor = min(unvisited, key=lambda n: graph[current][n].get('distance', float('inf')))

            path.append(best_neighbor)
            visited.add(best_neighbor)
            current = best_neighbor

        return path if path[-1] == end else [start, end]

    def _random_walk(self, graph: Dict, start: int, end: int) -> List[int]:
        """
        使用随机游走生成路径

        Args:
            graph: 图结构
            start: 起点节点ID
            end: 终点节点ID

        Returns:
            路径节点列表
        """
        if start == end:
            return [start]

        path = [start]
        visited = {start}
        current = start

        max_steps = len(graph) * 3  # 允许更多步数以探索

        for _ in range(max_steps):
            if current == end:
                break

            neighbors = list(graph.get(current, {}).keys())

            if not neighbors:
                break

            # 随机选择下一个节点，优先选择未访问的
            unvisited = [n for n in neighbors if n not in visited]
            if unvisited and random.random() > 0.1:  # 90%概率选择未访问
                next_node = random.choice(unvisited)
            else:
                next_node = random.choice(neighbors)

            path.append(next_node)
            visited.add(next_node)
            current = next_node

        # 如果未到达终点，尝试直接连接
        if path[-1] != end and end in graph.get(current, {}):
            path.append(end)

        return path if path[-1] == end else [start, end]

    def _evaluate_fitness(self, particle: 'Particle', graph: Dict,
                         objectives: List[str] = None, weights: Dict = None) -> float:
        """
        评估粒子的适应度（路径成本）

        Args:
            particle: 粒子对象
            graph: 图结构
            objectives: 优化目标列表
            weights: 各目标的权重字典

        Returns:
            适应度值（越小越好）
        """
        if not particle.path or len(particle.path) < 2:
            return float('inf')

        total_cost = 0

        for i in range(len(particle.path) - 1):
            u, v = particle.path[i], particle.path[i + 1]

            # 检查边是否存在
            if v not in graph.get(u, {}):
                return float('inf')

            edge_info = graph[u][v]

            # 计算边成本
            if objectives and len(objectives) > 1:
                edge_cost = CostCalculator.calculate_edge_cost(edge_info, objectives, weights)
            else:
                edge_cost = edge_info.get('distance', float('inf'))

            total_cost += edge_cost

        particle.fitness = total_cost
        return total_cost

    def _update_particles(self, particles: List['Particle'],
                         global_best_path: List[int], graph: Dict):
        """
        更新粒子位置

        在路径规划问题中，"速度"概念不太适用，
        这里使用交叉和变异操作来更新粒子路径。

        Args:
            particles: 粒子列表
            global_best_path: 全局最优路径
            graph: 图结构
        """
        for particle in particles:
            # 基于惯性：有一定概率保持原路径
            if random.random() < self.w * 0.8:
                continue

            # 认知学习：与个体最优交叉
            if random.random() < self.c1 * 0.1:
                new_path = self._crossover(particle.path, particle.best_path, graph)
                if new_path:
                    particle.path = new_path

            # 社会学习：与全局最优交叉
            if random.random() < self.c2 * 0.1 and global_best_path is not None:
                new_path = self._crossover(particle.path, global_best_path, graph)
                if new_path:
                    particle.path = new_path

            # 变异：随机改变路径
            if random.random() < 0.05:
                particle.path = self._mutate(particle.path, graph)

    def _crossover(self, path1: List[int], path2: List[int], graph: Dict) -> Optional[List[int]]:
        """
        路径交叉操作（增强版）

        Args:
            path1: 路径1
            path2: 路径2
            graph: 图结构

        Returns:
            新路径，如果交叉失败则返回None
        """
        # 增强的路径有效性检查
        if path1 is None or path2 is None:
            return None
        if len(path1) < 2 or len(path2) < 2:
            return None
        # 检查路径的起点和终点是否一致（才能进行交叉）
        if path1[0] != path2[0] or path1[-1] != path2[-1]:
            return None

        # 找到两条路径的公共节点（排除起点和终点）
        common_nodes = set(path1) & set(path2) - {path1[0], path1[-1]}

        if not common_nodes:
            return None

        # 随机选择一个公共节点作为交叉点
        crossover_node = random.choice(list(common_nodes))

        # 获取交叉点在两条路径中的位置
        try:
            idx1 = path1.index(crossover_node)
            idx2 = path2.index(crossover_node)
        except ValueError:
            return None

        # 拼接路径
        new_path = path1[:idx1] + path2[idx2:]

        # 验证新路径的有效性
        if self._validate_path(new_path, graph):
            return new_path

        return None

    def _mutate(self, path: List[int], graph: Dict) -> List[int]:
        """
        路径变异操作

        随机改变路径中的一个片段。

        Args:
            path: 原路径
            graph: 图结构

        Returns:
            变异后的路径
        """
        if len(path) < 3:
            return path

        # 随机选择变异位置
        start_idx = random.randint(0, len(path) - 2)
        end_idx = random.randint(start_idx + 1, len(path) - 1)

        start_node = path[start_idx]
        end_node = path[end_idx]

        # 在两个节点之间生成新路径
        new_segment = self._random_walk(graph, start_node, end_node)

        # 替换原有片段
        new_path = path[:start_idx] + new_segment + path[end_idx:]

        return new_path if self._validate_path(new_path, graph) else path

    def _validate_path(self, path: List[int], graph: Dict) -> bool:
        """
        验证路径的有效性

        Args:
            path: 路径
            graph: 图结构

        Returns:
            路径是否有效
        """
        if not path:
            return False

        # 检查每一条边是否存在
        for i in range(len(path) - 1):
            if path[i + 1] not in graph.get(path[i], {}):
                return False

        return True

    def get_metrics(self) -> Dict:
        """
        获取算法执行指标

        Returns:
            指标字典
        """
        metrics = {
            "algorithm": self.name,
            "execution_time_ms": round(self.last_execution_time, 3),
            "nodes_visited": self.last_nodes_visited,
            "iterations": self.max_iterations,
            "population_size": self.population_size,
            "parameters": {
                "inertia_weight": self.w,
                "cognitive_weight": self.c1,
                "social_weight": self.c2
            }
        }

        # 添加收敛信息（如果有的话）
        if self.convergence_history:
            metrics["convergence_info"] = {
                "final_fitness": self.convergence_history[-1],
                "improved_iterations": sum(1 for i in range(1, len(self.convergence_history))
                                        if self.convergence_history[i] < self.convergence_history[i-1])
            }

        return metrics

    def reset_metrics(self):
        """重置执行指标"""
        super().reset_metrics()
        self.convergence_history = []


class Particle:
    """粒子类

    代表路径规划问题中的一条候选路径。
    """

    def __init__(self, path: List[int]):
        """
        初始化粒子

        Args:
            path: 路径节点列表
        """
        self.path = path
        self.best_path = path.copy()  # 个体历史最优路径
        self.best_fitness = float('inf')  # 个体历史最优适应度
        self.fitness = float('inf')  # 当前适应度

    def __repr__(self):
        return (f"<Particle(path={self.path[:5]}{'...' if len(self.path) > 5 else ''}, "
                f"fitness={self.fitness:.2f})>")


# 便捷函数
def pso(graph: Dict, start: int, end: int,
         objectives: List[str] = None, weights: Dict = None, config: Dict = None) -> Tuple[List[int], float]:
    """
    PSO算法的便捷函数

    Args:
        graph: 图结构
        start: 起点节点ID
        end: 终点节点ID
        objectives: 优化目标列表
        weights: 各目标的权重字典
        config: 配置字典

    Returns:
        (path, cost) 路径和成本
    """
    algo = PSOAlgorithm(config)
    return algo.find_path(graph, start, end, objectives, weights)
