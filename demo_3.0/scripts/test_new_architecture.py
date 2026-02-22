"""Test new architecture with cache and temporary graph builder"""
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.services.route_planner import get_route_planner

def test_route_planning():
    """Test the new architecture"""
    print("=" * 70)
    print("Testing New Architecture: Cache + Amap API + Temporary Graph")
    print("=" * 70)

    planner = get_route_planner()

    # Test addresses
    start_addr = "湘潭火车站"
    end_addr = "湘潭大学"

    algorithms = ['dijkstra', 'astar', 'pso']

    print("\n" + "=" * 70)
    print("First Call (Cache Miss - Should call Amap API)")
    print("=" * 70)

    first_results = {}
    for algo in algorithms:
        print(f"\n--- Testing {algo.upper()} ---")
        start_time = time.time()

        result = planner.plan_route(
            start_addr=start_addr,
            end_addr=end_addr,
            algorithm=algo
        )

        elapsed = (time.time() - start_time) * 1000  # ms

        if result.get('success'):
            print(f"  Success: {result.get('success')}")
            print(f"  From Cache: {result.get('from_cache', False)}")
            print(f"  Path Length: {len(result.get('path', []))} nodes")
            print(f"  Total Cost: {result.get('total_cost', 0):.2f}")
            print(f"  Route Coords: {result.get('route_coords_count', 0)} points")
            print(f"  Execution Time: {result.get('metrics', {}).get('execution_time_ms', 0):.2f}ms")
            print(f"  API Response Time: {elapsed:.0f}ms")
            first_results[algo] = result
        else:
            print(f"  Error: {result.get('error')}")

    print("\n" + "=" * 70)
    print("Second Call (Cache Hit - Should be fast)")
    print("=" * 70)

    second_results = {}
    for algo in algorithms:
        print(f"\n--- Testing {algo.upper()} ---")
        start_time = time.time()

        result = planner.plan_route(
            start_addr=start_addr,
            end_addr=end_addr,
            algorithm=algo
        )

        elapsed = (time.time() - start_time) * 1000  # ms

        if result.get('success'):
            print(f"  Success: {result.get('success')}")
            print(f"  From Cache: {result.get('from_cache', False)}")
            print(f"  Path Length: {len(result.get('path', []))} nodes")
            print(f"  Total Cost: {result.get('total_cost', 0):.2f}")
            print(f"  API Response Time: {elapsed:.0f}ms")
            second_results[algo] = result
        else:
            print(f"  Error: {result.get('error')}")

    print("\n" + "=" * 70)
    print("Algorithm Comparison")
    print("=" * 70)

    for algo in algorithms:
        if algo in first_results:
            r1 = first_results[algo]
            cost = r1.get('total_cost', 0)
            path_len = len(r1.get('path', []))
            print(f"  {algo.upper():8} - Cost: {cost:10.2f}, Path: {path_len} nodes")

    print("\n" + "=" * 70)
    print("Cache Statistics")
    print("=" * 70)

    cache_service = planner.cache_service
    stats = cache_service.get_cache_stats()
    print(f"  Total Entries: {stats.get('total_entries', 0)}")
    print(f"  Total Hits: {stats.get('total_hits', 0)}")
    print(f"  Hit Rate: {stats.get('hit_rate', 0):.1%}")

if __name__ == '__main__':
    try:
        test_route_planning()
        print("\n[OK] Test completed successfully!")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
