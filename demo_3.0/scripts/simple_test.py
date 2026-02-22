"""简单测试脚本"""
import logging
import os

# 强制关闭所有SQLAlchemy日志
for logger_name in ['sqlalchemy', 'sqlalchemy.engine', 'sqlalchemy.dialects', 'sqlalchemy.pool']:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    logging.getLogger(logger_name).disabled = True

import sys
sys.path.insert(0, '.')

from src.services.route_planner import RoutePlanner

planner = RoutePlanner()

print('=== 测试: 湘潭火车站 -> 湘潭大学 ===')
for algo in ['dijkstra', 'astar', 'pso']:
    try:
        result = planner.plan_route('湘潭火车站', '湘潭大学', algo)
        if result['success']:
            path_len = len(result.get('path', []))
            cost = result.get('total_cost', 0)
            api_fallback = 'API' if result.get('using_api_fallback') else 'DB'
            print(f'{algo:10}: 节点={path_len:3d} 成本={cost:7.1f}m 来源={api_fallback}')
            if result.get('path') and len(result.get('path')) > 3:
                print(f'           路径: {result["path"][0]} -> {result["path"][1]} -> ... -> {result["path"][-1]}')
        else:
            error = result.get('error', 'Unknown')
            print(f'{algo:10}: 失败 - {str(error)[:50]}')
    except Exception as e:
        print(f'{algo:10}: 异常 - {str(e)[:50]}')

print('\n测试完成！')
