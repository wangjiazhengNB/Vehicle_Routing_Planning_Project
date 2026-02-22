"""测试路径规划功能"""
import requests
import json

API_BASE = 'http://127.0.0.1:5000/api'

def test_route_planning():
    """测试路径规划"""
    print("=" * 60)
    print("测试路径规划功能")
    print("=" * 60)

    # 测试湖南工程学院 -> 湘潭大学
    data = {
        "start": "湖南工程学院",
        "end": "湘潭大学",
        "algorithm": "dijkstra"
    }

    print(f"\n请求参数: {json.dumps(data, ensure_ascii=False)}")

    try:
        response = requests.post(
            f"{API_BASE}/route/plan",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

        result = response.json()
        print(f"\n响应状态码: {response.status_code}")

        if result.get("success"):
            print("路径规划成功!")
            print(f"算法: {result.get('data', {}).get('algorithm')}")
            print(f"总成本: {result.get('data', {}).get('total_cost')} 米")

            path = result.get('data', {}).get('path', [])
            print(f"路径节点数: {len(path)}")
            print(f"路径节点: {path}")

            metrics = result.get('data', {}).get('metrics', {})
            print(f"执行时间: {metrics.get('execution_time_ms')} 毫秒")
            print(f"访问节点: {metrics.get('nodes_visited')}")

            map_file = result.get('data', {}).get('map_file')
            if map_file:
                print(f"地图文件: {map_file}")
        else:
            print(f"路径规划失败: {result.get('error')}")

    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_route_planning()
