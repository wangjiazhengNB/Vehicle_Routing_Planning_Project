"""
路径缓存服务

管理路径规划结果的缓存，减少高德API调用。
"""
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
from sqlalchemy import text
from ..config.database import get_session


class RouteCacheService:
    """路径缓存服务

    提供路径缓存的存储、查询和管理功能。
    """

    # 缓存策略配置
    CACHE_TTL_DAYS = 7  # 缓存有效期（天）
    MAX_CACHE_SIZE = 10000  # 最大缓存条目数
    MIN_ACCESS_COUNT = 2  # 最小访问次数才保留长期缓存

    def __init__(self):
        """初始化缓存服务"""

    def get_cached_route(
        self,
        start_addr: str,
        end_addr: str,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float]
    ) -> Optional[Dict]:
        """获取缓存的路由

        Args:
            start_addr: 起点地址
            end_addr: 终点地址
            start_coords: 起点坐标 (lng, lat)
            end_coords: 终点坐标 (lng, lat)

        Returns:
            缓存的路由数据，如果不存在返回None
        """
        session = get_session()
        try:
            # 查询缓存 - 包含坐标字段
            query = text("""
                SELECT id, start_lat, start_lng, end_lat, end_lng,
                       graph_data, node_mapping,
                       dijkstra_result, astar_result, pso_result,
                       total_distance, estimated_duration, access_count
                FROM route_cache
                WHERE start_address = :start_addr
                  AND end_address = :end_addr
                  AND created_at > :expire_date
                LIMIT 1
            """)

            expire_date = datetime.now() - timedelta(days=self.CACHE_TTL_DAYS)

            result = session.execute(query, {
                "start_addr": start_addr,
                "end_addr": end_addr,
                "expire_date": expire_date
            }).fetchone()

            if result:
                # 更新访问统计
                update_query = text("""
                    UPDATE route_cache
                    SET access_count = access_count + 1,
                        cache_hit_count = cache_hit_count + 1,
                        last_accessed_at = NOW()
                    WHERE id = :id
                """)
                session.execute(update_query, {"id": result[0]})
                session.commit()

                # 返回缓存数据 - 包含坐标
                return {
                    'start_lat': float(result[1]) if result[1] else None,
                    'start_lng': float(result[2]) if result[2] else None,
                    'end_lat': float(result[3]) if result[3] else None,
                    'end_lng': float(result[4]) if result[4] else None,
                    'graph_data': json.loads(result[5]) if result[5] else None,
                    'node_mapping': json.loads(result[6]) if result[6] else None,
                    'dijkstra_result': json.loads(result[7]) if result[7] else None,
                    'astar_result': json.loads(result[8]) if result[8] else None,
                    'pso_result': json.loads(result[9]) if result[9] else None,
                    'total_distance': float(result[10]) if result[10] else None,
                    'estimated_duration': result[11],
                    'from_cache': True
                }

            return None

        except Exception as e:
            print(f"获取缓存失败: {e}")
            return None
        finally:
            session.close()

    def save_route_cache(
        self,
        start_addr: str,
        end_addr: str,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        amap_response: Dict,
        graph_data: Dict,
        node_coords: Dict,
        algorithm_results: Dict[str, Dict]
    ) -> bool:
        """保存路由到缓存

        Args:
            start_addr: 起点地址
            end_addr: 终点地址
            start_coords: 起点坐标 (lng, lat)
            end_coords: 终点坐标 (lng, lat)
            amap_response: 高德API响应（简化格式或完整格式）
            graph_data: 图结构数据
            node_coords: 节点坐标 {node_id: (lat, lng)}
            algorithm_results: 算法结果 {'dijkstra': {...}, 'astar': {...}, 'pso': {...}}

        Returns:
            是否成功保存
        """
        session = get_session()
        try:
            # Handle both simplified and full API response formats
            total_distance = 0
            estimated_duration = 0
            raw_polyline = ""

            if 'coords' in amap_response:
                # Simplified format from amap_service.get_driving_route()
                total_distance = amap_response.get('distance', 0)
                estimated_duration = amap_response.get('duration', 0)
                coords = amap_response.get('coords', [])

                # Build polyline from coords
                polyline_parts = []
                for lat, lng in coords:
                    polyline_parts.append(f"{lng},{lat}")
                raw_polyline = ';'.join(polyline_parts)

            else:
                # Full API response format
                route = amap_response.get('route', {})
                if not route:
                    return False

                paths = route.get('paths', [])
                if not paths:
                    return False

                path = paths[0]

                # Extract polylines from steps
                polylines = []
                for step in path.get('steps', []):
                    if step.get('polyline'):
                        polylines.append(step['polyline'])
                raw_polyline = ';'.join(polylines)

                total_distance = path.get('distance', 0)
                estimated_duration = path.get('duration', 0)

            # Prepare graph data with node_coords - 确保节点ID为字符串
            graph_with_coords = {
                'graph': graph_data,
                'node_coords': {str(k): v for k, v in node_coords.items()}  # 转换为字符串键
            }
            graph_json = json.dumps(graph_with_coords, ensure_ascii=False)
            node_mapping_json = json.dumps({str(k): v for k, v in node_coords.items()}, ensure_ascii=False)

            # Serialize algorithm results
            dijkstra_result_json = json.dumps(
                algorithm_results.get('dijkstra', {}),
                ensure_ascii=False
            )
            astar_result_json = json.dumps(
                algorithm_results.get('astar', {}),
                ensure_ascii=False
            )
            pso_result_json = json.dumps(
                algorithm_results.get('pso', {}),
                ensure_ascii=False
            )

            # Insert or update cache - fixed typo (pso_result not peso_result)
            query = text("""
                INSERT INTO route_cache
                (start_address, end_address, start_lat, start_lng, end_lat, end_lng,
                 raw_polyline, total_distance, estimated_duration,
                 graph_data, node_mapping, dijkstra_result, astar_result, pso_result,
                 access_count, cache_hit_count)
                VALUES
                (:start_addr, :end_addr, :start_lat, :start_lng, :end_lat, :end_lng,
                 :raw_polyline, :total_distance, :estimated_duration,
                 :graph_data, :node_mapping, :dijkstra_result, :astar_result, :pso_result,
                 1, 0)
                ON DUPLICATE KEY UPDATE
                    raw_polyline = VALUES(raw_polyline),
                    total_distance = VALUES(total_distance),
                    estimated_duration = VALUES(estimated_duration),
                    graph_data = VALUES(graph_data),
                    node_mapping = VALUES(node_mapping),
                    dijkstra_result = VALUES(dijkstra_result),
                    astar_result = VALUES(astar_result),
                    pso_result = VALUES(pso_result),
                    access_count = access_count + 1,
                    last_accessed_at = NOW()
            """)

            session.execute(query, {
                "start_addr": start_addr,
                "end_addr": end_addr,
                "start_lat": start_coords[1],
                "start_lng": start_coords[0],
                "end_lat": end_coords[1],
                "end_lng": end_coords[0],
                "raw_polyline": raw_polyline,
                "total_distance": total_distance,
                "estimated_duration": estimated_duration,
                "graph_data": graph_json,
                "node_mapping": node_mapping_json,
                "dijkstra_result": dijkstra_result_json,
                "astar_result": astar_result_json,
                "pso_result": pso_result_json
            })

            session.commit()
            return True

        except Exception as e:
            session.rollback()
            print(f"保存缓存失败: {e}")
            return False
        finally:
            session.close()

    def cleanup_expired_cache(self) -> int:
        """清理过期的缓存

        Returns:
            清理的条目数
        """
        session = get_session()
        try:
            # 删除过期且访问次数少的缓存
            expire_date = datetime.now() - timedelta(days=self.CACHE_TTL_DAYS)

            query = text("""
                DELETE FROM route_cache
                WHERE created_at < :expire_date
                  AND access_count < :min_access
            """)

            result = session.execute(query, {
                "expire_date": expire_date,
                "min_access": self.MIN_ACCESS_COUNT
            })

            session.commit()
            return result.rowcount

        except Exception as e:
            print(f"清理缓存失败: {e}")
            session.rollback()
            return 0
        finally:
            session.close()

    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息

        Returns:
            统计信息字典
        """
        session = get_session()
        try:
            stats_query = text("""
                SELECT
                    COUNT(*) as total_entries,
                    SUM(access_count) as total_accesses,
                    SUM(cache_hit_count) as total_hits,
                    AVG(access_count) as avg_accesses,
                    MAX(created_at) as latest_entry,
                    COUNT(CASE WHEN created_at > NOW() - INTERVAL 7 DAY THEN 1 END) as recent_entries
                FROM route_cache
            """)

            result = session.execute(stats_query).fetchone()

            total_hits = result[2] or 0
            total_accesses = result[1] or 0
            hit_rate = (total_hits / total_accesses * 100) if total_accesses > 0 else 0

            return {
                'total_entries': result[0] or 0,
                'total_accesses': total_accesses,
                'total_hits': total_hits,
                'hit_rate': round(hit_rate, 2),
                'avg_accesses': round(result[3], 2) if result[3] else 0,
                'latest_entry': result[4].isoformat() if result[4] else None,
                'recent_entries': result[5] or 0
            }

        except Exception as e:
            print(f"获取缓存统计失败: {e}")
            return {}
        finally:
            session.close()


# 全局服务实例
_route_cache_service = None


def get_route_cache_service() -> RouteCacheService:
    """获取全局路径缓存服务实例"""
    global _route_cache_service
    if _route_cache_service is None:
        _route_cache_service = RouteCacheService()
    return _route_cache_service
