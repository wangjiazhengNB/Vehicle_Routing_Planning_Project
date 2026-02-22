"""快速测试路径规划功能"""
import logging
import sys
import os

# 强制关闭所有SQLAlchemy日志
for logger_name in ['sqlalchemy', 'sqlalchemy.engine', 'sqlalchemy.dialects', 'sqlalchemy.pool']:
    logging.getLogger(logger_name).setLevel(logging.CRITICAL)
    logging.getLogger(logger_name).disabled = True

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.services.route_planner import RoutePlanner

def main():
    print("=" * 60)
    print("快速测试路径规划功能")
    print("=" * 60)

    planner = RoutePlanner()

    # 测试用例
    test_cases = [
        ("湘潭火车站", "湘潭大学"),
        ("湖南工程学院", "湘潭大学"),
    ]

    algorithms = ["dijkstra", "astar"]

    for start, end in test_cases:
        print(f"\n测试: {start} -> {end}")
        print("-" * 60)

        for algo in algorithms:
            result = planner.plan_route(start, end, algo)

            status = "[OK]" if result['success'] else "[FAIL]"
            print(f"{status} {algo:10} - ", end="")

            if result['success']:
                path_len = len(result.get('path', []))
                cost = result.get('total_cost', 0)
                api_fallback = "API" if result.get('using_api_fallback') else "DB"
                print(f"节点:{path_len:3d} 成本:{cost:7.1f}m 来源:{api_fallback}")
            else:
                error = result.get('error', 'Unknown')[:50]
                print(f"错误: {error}")

if __name__ == "__main__":
    main()
