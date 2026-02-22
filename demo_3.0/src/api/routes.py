"""Flask API 路由模块"""

from flask import Blueprint, request, jsonify, render_template
from flask_cors import CORS
from typing import Dict, Any, List

from ..services.route_planner import get_route_planner
from ..config.settings import get_config

config = get_config()

# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 路由规划服务
route_planner = get_route_planner()


@api_bp.route('/algorithms/list', methods=['GET'])
def get_algorithms():
    """获取可用算法列表"""
    algorithms = []

    for algo_name in route_planner.get_available_algorithms():
        info = route_planner.get_algorithm_info(algo_name)
        if info:
            algorithms.append({
                'id': algo_name,
                'name': info['name'],
                'type': info['type'],
                'description': info['description']
            })

    return jsonify({
        'success': True,
        'data': algorithms
    })


@api_bp.route('/route/plan', methods=['POST'])
def plan_route():
    """
    使用指定算法规划路径

    请求体:
    {
        "start": "起点地址",
        "end": "终点地址",
        "algorithm": "dijkstra",
        "objectives": ["distance"]  # 可选
    }

    返回:
    {
        "success": true,
        "data": {
            "algorithm": "dijkstra",
            "path": [...],
            "total_cost": 1234.56,
            "metrics": {...},
            "map_file": "output/maps/..."
        }
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400

        start = data.get('start')
        end = data.get('end')
        algorithm = data.get('algorithm', 'dijkstra')
        objectives = data.get('objectives')

        # 验证必需参数
        if not start or not end:
            return jsonify({
                'success': False,
                'error': '起点和终点地址不能为空'
            }), 400

        # 调用路径规划服务
        result = route_planner.plan_route(start, end, algorithm, objectives)

        if result.get('success'):
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '路径规划失败')
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@api_bp.route('/route/compare', methods=['POST'])
def compare_routes():
    """
    使用多个算法对比规划路径

    请求体:
    {
        "start": "起点地址",
        "end": "终点地址",
        "algorithms": ["dijkstra", "pso"],  // 可选，默认所有算法
        "objectives": ["distance"]
    }

    返回:
    {
        "success": true,
        "data": {
            "results": {...},
            "best_algorithm": "dijkstra"
        }
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400

        start = data.get('start')
        end = data.get('end')
        algorithms = data.get('algorithms')
        objectives = data.get('objectives')

        # 验证必需参数
        if not start or not end:
            return jsonify({
                'success': False,
                'error': '起点和终点地址不能为空'
            }), 400

        # 调用对比服务
        result = route_planner.compare_algorithms(start, end, algorithms, objectives)

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@api_bp.route('/algorithm/info/<algorithm_name>', methods=['GET'])
def get_algorithm_info(algorithm_name: str):
    """获取指定算法的详细信息"""
    info = route_planner.get_algorithm_info(algorithm_name)

    if info:
        return jsonify({
            'success': True,
            'data': info
        })
    else:
        return jsonify({
            'success': False,
            'error': f'算法不存在: {algorithm_name}'
        }), 404


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'success': True,
        'data': {
            'app_name': config.app_name,
            'version': config.app_version,
            'status': 'running'
        }
    })


@api_bp.route('/map/<path:filename>', methods=['GET'])
def get_map(filename: str):
    """获取地图文件"""
    from flask import send_from_directory
    import os

    map_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'maps')
    return send_from_directory(map_dir, filename)
