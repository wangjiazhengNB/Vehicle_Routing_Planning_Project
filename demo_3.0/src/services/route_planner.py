"""路径规划服务

算法调度器，统一管理多种路径规划算法
"""

from typing import Dict, Any, List, Optional
import json

from ..algorithms.dijkstra import DijkstraAlgorithm, build_graph_from_edges
from ..algorithms.pso import PSOAlgorithm
from ..algorithms.astar import AStarAlgorithm
from ..algorithms.cost_calculator import CostCalculator
from ..config.settings import get_config
from ..services.amap_service import get_amap_service
from ..services.map_service import get_map_service
from .graph_builder import get_graph_builder
from .route_cache_service import get_route_cache_service


config = get_config()


class RoutePlanner:
    """路径规划服务 - 算法调度器

    统一管理多种路径规划算法，提供一致的接口
    """

    def __init__(self):
        """初始化路径规划服务"""
        # 注册算法
        self.algorithms = {
            "dijkstra": DijkstraAlgorithm(),
            "pso": PSOAlgorithm(config.get('algorithms.pso', {})),
            "astar": AStarAlgorithm(
                heuristic=config.get('algorithms.astar.heuristic', 'euclidean')
            ),
        }

        # 初始化服务
        self.amap_service = get_amap_service()
        self.map_service = get_map_service()

        # 新架构：临时图构建器和缓存服务
        self.graph_builder = get_graph_builder()
        self.cache_service = get_route_cache_service()

        # 成本权重配置
        self.cost_weights = config.cost_weights

    def plan_route(self, start_addr: str, end_addr: str,
                  algorithm: str = "dijkstra",
                  objectives: List[str] = None) -> Dict[str, Any]:
        """
        使用指定算法规划路径

        Args:
            start_addr: 起点地址
            end_addr: 终点地址
            algorithm: 算法名称 (dijkstra/pso/astar)
            objectives: 优化目标列表，默认为 ['distance']

        Returns:
            规划结果字典，包含:
            - success: 是否成功
            - algorithm: 使用的算法
            - path: 路径节点列表
            - total_cost: 总成本
            - metrics: 算法执行指标
            - map_file: 地图文件路径
            - error: 错误信息（如果有）
        """
        try:
            # 1. 地址解析
            start_coords = self.amap_service.get_coordinates(start_addr)
            end_coords = self.amap_service.get_coordinates(end_addr)

            if not start_coords or not end_coords:
                return {
                    "success": False,
                    "error": "地址解析失败，请检查地址是否正确"
                }

            start_coords_tuple = (start_coords[0], start_coords[1])  # (lng, lat)
            end_coords_tuple = (end_coords[0], end_coords[1])        # (lng, lat)

            # 2. 检查缓存（新架构：优先使用缓存）
            cached_data = self.cache_service.get_cached_route(
                start_addr, end_addr, start_coords_tuple, end_coords_tuple
            )

            if cached_data and cached_data.get(algorithm + '_result'):
                # 从缓存返回结果
                return self._format_cached_result(cached_data, algorithm, start_addr, end_addr)

            # 3. 缓存未命中，调用高德API获取多条路径（直达+途经点绕行）
            routes_data = self.amap_service.get_multiple_routes_with_waypoints(
                start_coords_tuple, end_coords_tuple
            )

            if not routes_data:
                return {
                    "success": False,
                    "error": "高德API路径获取失败"
                }

            # 4. 构建多路径图结构（从多条路径合并）
            graph, node_coords, route_info = self.graph_builder.build_multi_route_graph(routes_data)

            if not graph:
                return {
                    "success": False,
                    "error": "无法从API数据构建图结构"
                }

            # 保存route_info用于调试
            metadata = {
                'routes_count': len(routes_data),
                'route_info': route_info
            }

            # 5. 确定起点和终点节点ID
            start_node = self.graph_builder.find_nearest_node_in_graph(
                graph, node_coords,
                start_coords[1], start_coords[0]  # lat, lng
            )
            end_node = self.graph_builder.find_nearest_node_in_graph(
                graph, node_coords,
                end_coords[1], end_coords[0]      # lat, lng
            )

            if start_node is None or end_node is None:
                return {
                    "success": False,
                    "error": "无法在图中找到起点或终点节点"
                }

            # 6. 运行所有算法（即使只需要一个，也运行全部以备缓存）
            all_results = {}
            for algo_name in ['dijkstra', 'astar', 'pso']:
                algo = self.algorithms[algo_name]

                # A*需要坐标
                if algo_name == 'astar':
                    algo.set_node_coordinates(node_coords)

                # 设置算法目标和权重
                algorithm_objectives = {
                    'dijkstra': ['distance'],
                    'astar': ['distance', 'congestion'],
                    'pso': ['distance', 'congestion', 'construction']
                }

                algorithm_weights = {
                    'dijkstra': {'distance': 1.0},
                    'astar': {'distance': 0.7, 'congestion': 0.3},
                    'pso': {'distance': 0.5, 'congestion': 0.3, 'construction': 0.2}
                }

                objectives = algorithm_objectives.get(algo_name, ['distance'])
                weights = algorithm_weights.get(algo_name, None)

                # 运行算法
                path, cost = algo.find_path(graph, start_node, end_node, objectives, weights)

                all_results[algo_name] = {
                    'path': path,
                    'cost': cost,
                    'metrics': algo.get_metrics()
                }

            # 7. 保存到缓存（多路径格式）
            # 构造兼容的响应格式
            cache_response = {
                'coords': routes_data[0]['coords'] if routes_data else [],
                'distance': sum(r['distance'] for r in routes_data) if routes_data else 0,
                'duration': sum(r['duration'] for r in routes_data) if routes_data else 0,
                'route': {
                    'paths': [{
                        'distance': r['distance'],
                        'duration': r['duration'],
                        'steps': [],
                        'polyline': r.get('polyline', '')
                    } for r in routes_data]
                } if routes_data else {}
            }

            self.cache_service.save_route_cache(
                start_addr, end_addr,
                start_coords_tuple, end_coords_tuple,
                cache_response,
                graph, node_coords,
                all_results
            )

            # 8. 获取请求的算法结果
            result = all_results[algorithm]
            path = result['path']
            cost = result['cost']

            # 9. 计算总成本
            algorithm_objectives = {
                'dijkstra': ['distance'],
                'astar': ['distance', 'congestion'],
                'pso': ['distance', 'congestion', 'construction']
            }
            algorithm_weights = {
                'dijkstra': {'distance': 1.0},
                'astar': {'distance': 0.7, 'congestion': 0.3},
                'pso': {'distance': 0.5, 'congestion': 0.3, 'construction': 0.2}
            }
            objectives = algorithm_objectives.get(algorithm, ['distance'])
            weights = algorithm_weights.get(algorithm, None)

            if objectives and len(objectives) > 1:
                total_cost, detail_costs = CostCalculator.calculate_multi_objective_cost(
                    path, graph, weights
                )
            else:
                total_cost = CostCalculator.calculate_path_distance(path, graph)
                detail_costs = None

            # 10. 生成地图（包含路径线）
            route_coords = []
            if len(path) > 0:
                for node_id in path:
                    if node_id in node_coords:
                        node_lat, node_lng = node_coords[node_id]
                        route_coords.append([float(node_lat), float(node_lng)])

            map_file = self.map_service.generate_route_map(
                start_info=(start_coords[0], start_coords[1], start_addr),
                end_info=(end_coords[0], end_coords[1], end_addr),
                route_coords=route_coords if route_coords else None
            )

            # 11. 保存结果到数据库（历史记录）
            if len(path) > 0:
                from ..models.route_result import RouteResult
                from ..config.database import get_session

                session = get_session()
                try:
                    route_result = RouteResult(
                        start_address=start_addr,
                        end_address=end_addr,
                        algorithm=algorithm,
                        route_nodes=path,
                        total_distance=CostCalculator.calculate_path_distance(path, graph),
                        total_cost=cost,
                        execution_time=result['metrics']['execution_time_ms']
                    )
                    session.add(route_result)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    print(f"保存结果到数据库失败: {e}")
                finally:
                    session.close()

            # 12. 返回结果
            return {
                "success": True,
                "algorithm": algorithm,
                "path": path,
                "total_cost": float(total_cost),
                "detail_costs": detail_costs,
                "metrics": result['metrics'],
                "map_file": map_file,
                "start_coords": start_coords[:2],
                "end_coords": end_coords[:2],
                "from_cache": False,
                "route_coords_count": len(route_coords)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _format_cached_result(self, cached_data: Dict, algorithm: str,
                             start_addr: str, end_addr: str) -> Dict[str, Any]:
        """格式化缓存结果并返回

        Args:
            cached_data: 缓存数据
            algorithm: 请求的算法名称
            start_addr: 起点地址
            end_addr: 终点地址

        Returns:
            格式化后的结果字典
        """
        import json

        # 获取算法结果
        algo_result_key = algorithm + '_result'
        algo_result_str = cached_data.get(algo_result_key)

        if not algo_result_str:
            return {
                "success": False,
                "error": f"缓存中未找到{algorithm}算法的结果"
            }

        # 反序列化算法结果
        try:
            algo_result = json.loads(algo_result_str) if isinstance(algo_result_str, str) else algo_result_str
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "缓存数据解析失败"
            }

        path = algo_result.get('path', [])

        # 反序列化图数据以获取节点坐标
        route_coords = []
        graph_data_str = cached_data.get('graph_data')
        if graph_data_str and path:
            try:
                graph_data = json.loads(graph_data_str) if isinstance(graph_data_str, str) else graph_data_str
                node_coords = graph_data.get('node_coords', {})

                # 构建路径坐标列表 - 修复节点ID类型不匹配问题
                for node_id in path:
                    # 尝试整数键和字符串键（JSON反序列化后键变成字符串）
                    if node_id in node_coords:
                        lat, lng = node_coords[node_id]
                    elif str(node_id) in node_coords:
                        lat, lng = node_coords[str(node_id)]
                    else:
                        continue
                    route_coords.append([float(lat), float(lng)])
            except (json.JSONDecodeError, TypeError) as e:
                print(f"解析缓存图数据失败: {e}")

        # 生成地图（使用缓存数据）
        map_file = None
        try:
            start_coords = (
                cached_data.get('start_lng', 0),
                cached_data.get('start_lat', 0)
            )
            end_coords = (
                cached_data.get('end_lng', 0),
                cached_data.get('end_lat', 0)
            )

            if route_coords:
                map_file = self.map_service.generate_route_map(
                    start_info=(start_coords[0], start_coords[1], start_addr),
                    end_info=(end_coords[0], end_coords[1], end_addr),
                    route_coords=route_coords
                )
        except Exception as e:
            print(f"生成地图失败: {e}")

        # 计算 detail_costs（从缓存数据重新计算）
        detail_costs = None
        if graph_data_str and path:
            try:
                graph_data = json.loads(graph_data_str) if isinstance(graph_data_str, str) else graph_data_str
                graph = graph_data.get('graph', {})
                if graph:
                    # 根据算法类型使用不同的权重
                    algorithm_weights = {
                        'dijkstra': {'distance': 1.0},
                        'astar': {'distance': 0.7, 'congestion': 0.3},
                        'pso': {'distance': 0.5, 'congestion': 0.3, 'construction': 0.2}
                    }
                    weights = algorithm_weights.get(algorithm, {'distance': 1.0})

                    # 计算各分项成本
                    dc = {'distance': 0.0, 'congestion': 0.0, 'construction': 0.0}
                    for i in range(len(path) - 1):
                        u, v = str(path[i]), str(path[i + 1])  # 使用字符串键
                        if u in graph and v in graph[u]:
                            edge = graph[u][v]
                            dc['distance'] += float(edge.get('distance', 0))
                            dc['congestion'] += float(edge.get('congestion', 0))
                            dc['construction'] += float(edge.get('construction', 0))
                    detail_costs = dc
            except Exception as e:
                print(f"计算detail_costs失败: {e}")

        return {
            "success": True,
            "algorithm": algorithm,
            "path": path,
            "total_cost": float(algo_result.get('cost', 0)),
            "detail_costs": detail_costs,
            "metrics": algo_result.get('metrics', {}),
            "map_file": map_file,
            "start_coords": [cached_data.get('start_lng', 0), cached_data.get('start_lat', 0)],
            "end_coords": [cached_data.get('end_lng', 0), cached_data.get('end_lat', 0)],
            "from_cache": True,
            "route_coords_count": len(route_coords)
        }

    def compare_algorithms(self, start_addr: str, end_addr: str,
                          algorithms: List[str] = None,
                          objectives: List[str] = None) -> Dict[str, Any]:
        """
        使用多个算法对比规划路径

        Args:
            start_addr: 起点地址
            end_addr: 终点地址
            algorithms: 要对比的算法列表，默认为所有可用算法
            objectives: 优化目标列表

        Returns:
            对比结果字典
        """
        if algorithms is None:
            algorithms = list(self.algorithms.keys())

        results = {}

        for algo_name in algorithms:
            result = self.plan_route(start_addr, end_addr, algo_name, objectives)
            results[algo_name] = result

        return {
            "success": True,
            "results": results,
            "best_algorithm": self._find_best_algorithm(results)
        }

    def _find_best_algorithm(self, results: Dict[str, Dict]) -> Optional[str]:
        """找出成本最低的算法"""
        best_algo = None
        best_cost = float('inf')

        for algo_name, result in results.items():
            if result.get("success") and "total_cost" in result:
                cost = result["total_cost"]
                if cost < best_cost:
                    best_cost = cost
                    best_algo = algo_name

        return best_algo

    def get_available_algorithms(self) -> List[str]:
        """获取可用算法列表"""
        return list(self.algorithms.keys())

    def get_algorithm_info(self, algorithm: str) -> Optional[Dict[str, Any]]:
        """获取指定算法的信息"""
        if algorithm not in self.algorithms:
            return None

        algo = self.algorithms[algorithm]
        return {
            "name": algo.name,
            "type": algorithm,
            "description": self._get_algorithm_description(algorithm)
        }

    def _get_algorithm_description(self, algorithm: str) -> str:
        """获取算法描述"""
        descriptions = {
            "dijkstra": "Dijkstra最短路径算法，适用于非负权重图，保证找到最优解",
            "pso": "粒子群优化算法，适用于复杂优化问题，可能收敛到局部最优",
            "astar": "A*启发式搜索算法，结合实际距离估计，效率较高"
        }
        return descriptions.get(algorithm, "未知算法")


# 全局服务实例
_route_planner = None


def get_route_planner() -> RoutePlanner:
    """获取全局路径规划服务实例"""
    global _route_planner
    if _route_planner is None:
        _route_planner = RoutePlanner()
    return _route_planner
