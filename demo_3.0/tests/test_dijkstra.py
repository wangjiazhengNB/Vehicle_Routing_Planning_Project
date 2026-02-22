"""Dijkstra算法测试"""

import pytest
from src.algorithms.dijkstra import DijkstraAlgorithm, dijkstra, build_graph_from_edges


def test_dijkstra_basic():
    """测试Dijkstra基本功能"""
    # 创建测试图
    graph = {
        1: {2: {'distance': 10}, 3: {'distance': 5}},
        2: {4: {'distance': 1}},
        3: {2: {'distance': 3}, 4: {'distance': 9}},
        4: {}
    }

    algo = DijkstraAlgorithm()
    path, cost = algo.find_path(graph, 1, 4)

    assert len(path) > 0
    assert path[0] == 1
    assert path[-1] == 4
    assert cost > 0


def test_dijkstra_no_path():
    """测试没有路径的情况"""
    graph = {
        1: {2: {'distance': 10}},
        2: {},
        3: {4: {'distance': 5}},
        4: {}
    }

    algo = DijkstraAlgorithm()
    path, cost = algo.find_path(graph, 1, 4)

    assert len(path) == 0
    assert cost == float('inf')


def test_build_graph_from_edges():
    """测试从边列表构建图"""
    edges = [
        {'start_node_id': 1, 'end_node_id': 2, 'distance': 10, 'congestion': 0.5, 'construction': 0},
        {'start_node_id': 2, 'end_node_id': 3, 'distance': 5, 'congestion': 0.3, 'construction': 0},
    ]

    graph = build_graph_from_edges(edges, directed=True)

    assert 1 in graph
    assert 2 in graph
    assert 3 in graph
    assert 2 in graph[1]
    assert graph[1][2]['distance'] == 10


def test_dijkstra_convenience_function():
    """测试便捷函数"""
    graph = {
        1: {2: {'distance': 10}, 3: {'distance': 5}},
        2: {4: {'distance': 1}},
        3: {2: {'distance': 3}, 4: {'distance': 9}},
        4: {}
    }

    path, cost = dijkstra(graph, 1, 4)

    assert len(path) > 0
    assert cost > 0


def test_dijkstra_metrics():
    """测试算法指标"""
    graph = {
        1: {2: {'distance': 10}, 3: {'distance': 5}},
        2: {4: {'distance': 1}},
        3: {2: {'distance': 3}, 4: {'distance': 9}},
        4: {}
    }

    algo = DijkstraAlgorithm()
    path, cost = algo.find_path(graph, 1, 4)

    metrics = algo.get_metrics()

    assert 'algorithm' in metrics
    assert 'execution_time_ms' in metrics
    assert 'nodes_visited' in metrics
    assert metrics['algorithm'] == 'Dijkstra'
    assert metrics['execution_time_ms'] >= 0
    assert metrics['nodes_visited'] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
