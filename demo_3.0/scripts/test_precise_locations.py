"""Test precise location routing within Hunan province

This script tests path planning with precise geographic locations
within the same region in Hunan province, using POI search and waypoints.
"""
import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.services.route_planner import get_route_planner
from src.services.amap_service import get_amap_service


def test_precise_location_routing():
    """Test routing with precise locations in Hunan province"""
    print("=" * 70)
    print("Precise Location Routing Test (Hunan Province)")
    print("=" * 70)

    # Test cases with precise locations in Xiangtan City, Hunan
    test_cases = [
        {
            'start': '湘潭市岳塘区书院路38号',
            'end': '湘潭市雨湖区车站路',
            'description': '精确地址测试: 岳塘区到雨湖区'
        },
        {
            'start': '湘潭市岳塘区建设南路',
            'end': '湘潭市雨湖区解放北路',
            'description': '不同区域测试: 建设南路到解放北路'
        },
        {
            'start': '湘潭市岳塘区万达广场',
            'end': '湘潭市雨湖区步步高广场',
            'description': '商业区测试: 万达到步步高'
        }
    ]

    planner = get_route_planner()
    amap_service = get_amap_service()

    algorithms = ['dijkstra', 'astar', 'pso']

    for test in test_cases:
        print("\n" + "=" * 70)
        print(f"Test: {test['description']}")
        print(f"Start: {test['start']}")
        print(f"End: {test['end']}")
        print("=" * 70)

        # Get coordinates
        start_coords = amap_service.get_coordinates(test['start'])
        end_coords = amap_service.get_coordinates(test['end'])

        if start_coords and end_coords:
            print(f"Start Coordinates: ({start_coords[0]:.6f}, {start_coords[1]:.6f})")
            print(f"End Coordinates: ({end_coords[0]:.6f}, {end_coords[1]:.6f})")
        else:
            print("Failed to get coordinates!")
            continue

        # Test POI search for waypoints
        print("\n--- Searching for POI waypoints ---")
        waypoints = amap_service.search_poi_near_route(
            (start_coords[0], start_coords[1]),
            (end_coords[0], end_coords[1]),
            num_waypoints=2
        )
        print(f"Found {len(waypoints)} waypoints:")
        for lng, lat, name in waypoints:
            print(f"  - {name}: ({lng:.6f}, {lat:.6f})")

        # Test multiple routes with waypoints
        print("\n--- Getting routes with waypoints ---")
        routes = amap_service.get_multiple_routes_with_waypoints(
            (start_coords[0], start_coords[1]),
            (end_coords[0], end_coords[1])
        )
        print(f"Total routes found: {len(routes)}")
        for route in routes:
            route_type = route.get('route_type', 'unknown')
            route_name = route.get('route_name', 'Unnamed')
            distance = float(route.get('distance', 0)) / 1000  # Convert to km
            coords_count = len(route.get('coords', []))
            print(f"  - {route_name} ({route_type}): {distance:.2f}km, {coords_count} points")

        # Run algorithms
        print("\n--- Running Algorithms ---")
        results = {}
        for algo in algorithms:
            print(f"\n{algo.upper()} Algorithm:")
            start_time = time.time()

            result = planner.plan_route(
                start_addr=test['start'],
                end_addr=test['end'],
                algorithm=algo
            )

            elapsed = (time.time() - start_time) * 1000

            if result.get('success'):
                path = result.get('path', [])
                total_cost = result.get('total_cost', 0)
                detail_costs = result.get('detail_costs', {})
                route_coords_count = result.get('route_coords_count', 0)

                print(f"  Success: True")
                print(f"  Path Length: {len(path)} nodes")
                print(f"  Route Coords: {route_coords_count} points")
                print(f"  Total Cost: {total_cost:.2f}")
                if detail_costs:
                    print(f"  Detail Costs:")
                    print(f"    - Distance: {detail_costs.get('distance', 0):.2f}m")
                    print(f"    - Congestion: {detail_costs.get('congestion', 0):.2f}")
                    print(f"    - Construction: {detail_costs.get('construction', 0):.2f}")
                print(f"  Execution Time: {result.get('metrics', {}).get('execution_time_ms', 0):.2f}ms")
                print(f"  API Response Time: {elapsed:.0f}ms")

                results[algo] = {
                    'path': path,
                    'cost': total_cost,
                    'path_length': len(path),
                    'route_coords_count': route_coords_count
                }
            else:
                print(f"  Error: {result.get('error')}")
                results[algo] = None

        # Compare results
        print("\n--- Algorithm Comparison ---")
        if all(results.get(algo) for algo in algorithms):
            # Check if paths are different
            paths = [results[algo]['path'] for algo in algorithms]
            all_same = all(p == paths[0] for p in paths)

            print(f"Paths are identical: {all_same}")

            if not all_same:
                print("\nPath differences found:")
                for algo in algorithms:
                    path = results[algo]['path']
                    # Show first few nodes as sample
                    sample = str(path[:5]) if len(path) > 5 else str(path)
                    print(f"  {algo.upper()}: {sample}... ({len(path)} nodes)")
            else:
                print("\nAll algorithms found the same path.")
                print("This may happen when:")
                print("  - The route is very direct with limited alternatives")
                print("  - POI waypoints didn't create different routes")

            # Cost comparison
            print("\nCost comparison:")
            for algo in algorithms:
                cost = results[algo]['cost']
                print(f"  {algo.upper()}: {cost:.2f}")

        print("\n" + "-" * 70)


def test_cache_effectiveness():
    """Test cache effectiveness with precise locations"""
    print("\n\n" + "=" * 70)
    print("Cache Effectiveness Test")
    print("=" * 70)

    planner = get_route_planner()

    start_addr = '湘潭市岳塘区书院路38号'
    end_addr = '湘潭市雨湖区车站路'

    print(f"\nRoute: {start_addr} -> {end_addr}")

    # First call (cache miss)
    print("\n--- First Call (Cache Miss) ---")
    start_time = time.time()
    result1 = planner.plan_route(start_addr, end_addr, 'dijkstra')
    elapsed1 = (time.time() - start_time) * 1000
    print(f"From Cache: {result1.get('from_cache', False)}")
    print(f"Response Time: {elapsed1:.0f}ms")

    # Second call (cache hit)
    print("\n--- Second Call (Cache Hit) ---")
    start_time = time.time()
    result2 = planner.plan_route(start_addr, end_addr, 'dijkstra')
    elapsed2 = (time.time() - start_time) * 1000
    print(f"From Cache: {result2.get('from_cache', False)}")
    print(f"Response Time: {elapsed2:.0f}ms")
    print(f"Speedup: {elapsed1/elapsed2:.1f}x")

    # Show cache stats
    print("\n--- Cache Statistics ---")
    stats = planner.cache_service.get_cache_stats()
    print(f"Total Entries: {stats.get('total_entries', 0)}")
    print(f"Total Hits: {stats.get('total_hits', 0)}")
    print(f"Hit Rate: {stats.get('hit_rate', 0):.1f}%")


if __name__ == '__main__':
    try:
        test_precise_location_routing()
        test_cache_effectiveness()
        print("\n" + "=" * 70)
        print("[OK] All tests completed successfully!")
        print("=" * 70)
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
