"""高德地图API服务

复用 demo_2.0 的代码，封装高德地图API调用
"""

import requests
import logging
from functools import lru_cache
from typing import Tuple, Optional, Dict, Any, List

from ..config.settings import get_config

# 配置日志
logger = logging.getLogger(__name__)


config = get_config()


class AmapService:
    """高德地图API服务类"""

    def __init__(self):
        """初始化高德API服务"""
        self.api_key = config.amap_api_key
        self.poi_url = config.get("amap.poi_url")
        self.geocode_url = config.get("amap.geocode_url")
        self.route_url = config.get("amap.route_url")
        self.default_city = config.amap_default_city
        self.timeout = config.get("amap.timeout", 10)

    @lru_cache(maxsize=config.cache_size)
    def get_coordinates(self, address: str) -> Optional[Tuple[float, float, str]]:
        """
        获取地址坐标（带缓存）

        Args:
            address: 地址字符串

        Returns:
            (lng, lat, poi_name) 或 None
        """
        result = self.high_precision_lnglat(address)
        if result and result[0] is not None:
            return result
        return None

    def standardize_address(self, address: str) -> str:
        """
        地址标准化：自动补充城市及对应行政区

        Args:
            address: 原始地址

        Returns:
            标准化后的地址
        """
        # 地标映射
        area_mapping = {
            "湘潭大学": "雨湖区",
            "万达广场": "岳塘区",
            "湖南工程学院": "岳塘区",
            "步步高广场": "岳塘区",
            "湘潭火车站": "雨湖区",
            "湘潭北站": "雨湖区",
            "湘江大桥": "岳塘区"
        }

        for landmark, area in area_mapping.items():
            if landmark in address:
                return f"{self.default_city}{area}{address}"

        # 自动补充城市前缀
        if not address.startswith(self.default_city):
            return f"{self.default_city}{address}"

        return address

    def high_precision_lnglat(self, address: str) -> Optional[Tuple[float, float, str]]:
        """
        高精度定位：优先POI搜索，兜底地理编码

        Args:
            address: 地址字符串

        Returns:
            (lng, lat, poi_name) 或 None
        """
        std_addr = self.standardize_address(address)

        # 第一步：POI精准搜索
        poi_result = self._search_poi(address)
        if poi_result:
            return poi_result

        # 第二步：地理编码兜底
        geo_result = self._geocode_address(std_addr)
        if geo_result:
            return geo_result

        return None

    def _search_poi(self, address: str) -> Optional[Tuple[float, float, str]]:
        """
        POI搜索

        Args:
            address: 地址字符串

        Returns:
            (lng, lat, poi_name) 或 None
        """
        try:
            params = {
                "key": self.api_key,
                "keywords": address,
                "city": self.default_city,
                "children": 0,
                "offset": 1,
                "page": 1,
                "output": "json"
            }

            response = requests.get(self.poi_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "1" and int(data["count"]) > 0:
                poi = data["pois"][0]
                lng = float(poi["location"].split(",")[0])
                lat = float(poi["location"].split(",")[1])
                logger.debug(f"POI搜索成功: {address} -> ({lng}, {lat})")
                return (lng, lat, poi["name"])
            else:
                logger.warning(f"POI搜索无结果: {address}, status={data.get('status')}, info={data.get('info')}")
        except requests.Timeout:
            logger.error(f"POI搜索超时: {self.poi_url}, timeout={self.timeout}s, address={address}")
        except requests.ConnectionError as e:
            logger.error(f"POI搜索网络连接失败: {self.poi_url}, address={address}, error={str(e)}")
        except requests.RequestException as e:
            logger.error(f"POI搜索请求失败: {self.poi_url}, address={address}, error={str(e)}")
        except Exception as e:
            logger.error(f"POI搜索未知错误: address={address}, error={str(e)}")

        return None

    def _geocode_address(self, address: str) -> Optional[Tuple[float, float, str]]:
        """
        地理编码

        Args:
            address: 地址字符串

        Returns:
            (lng, lat, address) 或 None
        """
        try:
            params = {
                "key": self.api_key,
                "address": address,
                "city": self.default_city,
                "extensions": "all",
                "output": "json"
            }

            response = requests.get(self.geocode_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "1" and len(data["geocodes"]) > 0:
                geo = data["geocodes"][0]
                lng = float(geo["location"].split(",")[0])
                lat = float(geo["location"].split(",")[1])
                logger.debug(f"地理编码成功: {address} -> ({lng}, {lat})")
                return (lng, lat, address)
            else:
                logger.warning(f"地理编码无结果: {address}, status={data.get('status')}, info={data.get('info')}")
        except requests.Timeout:
            logger.error(f"地理编码超时: {self.geocode_url}, timeout={self.timeout}s, address={address}")
        except requests.ConnectionError as e:
            logger.error(f"地理编码网络连接失败: {self.geocode_url}, address={address}, error={str(e)}")
        except requests.RequestException as e:
            logger.error(f"地理编码请求失败: {self.geocode_url}, address={address}, error={str(e)}")
        except Exception as e:
            logger.error(f"地理编码未知错误: address={address}, error={str(e)}")

        return None

    def get_driving_route(self, start_coords: Tuple[float, float],
                          end_coords: Tuple[float, float]) -> Optional[Dict[str, Any]]:
        """
        获取驾车路径

        Args:
            start_coords: 起点坐标 (lng, lat)
            end_coords: 终点坐标 (lng, lat)

        Returns:
            路径信息字典，包含 coords, distance, duration 等
            或 None（请求失败）
        """
        try:
            params = {
                "key": self.api_key,
                "origin": f"{start_coords[0]},{start_coords[1]}",
                "destination": f"{end_coords[0]},{end_coords[1]}",
                "city": self.default_city,
                "output": "json",
                "strategy": 1,  # 推荐路线
                "extensions": "all"
            }

            response = requests.get(self.route_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "1" and len(data["route"]["paths"]) > 0:
                path = data["route"]["paths"][0]
                route_coords = []

                for step in path["steps"]:
                    for point in step["polyline"].split(";"):
                        lng, lat = map(float, point.split(","))
                        route_coords.append((lat, lng))

                return {
                    "coords": route_coords,
                    "distance": float(path.get("distance", 0)),
                    "duration": int(path.get("duration", 0))
                }
        except requests.Timeout:
            logger.error(f"路径规划超时: {self.route_url}, timeout={self.timeout}s")
        except requests.ConnectionError as e:
            logger.error(f"路径规划网络连接失败: {self.route_url}, error={str(e)}")
        except requests.RequestException as e:
            logger.error(f"路径规划请求失败: {self.route_url}, error={str(e)}")
        except Exception as e:
            logger.error(f"路径规划未知错误: error={str(e)}")

        return None

    def get_multiple_driving_routes(self, start_coords: Tuple[float, float],
                                    end_coords: Tuple[float, float],
                                    strategies: List[int] = None) -> List[Dict[str, Any]]:
        """
        使用多种策略获取多条驾车路径

        Args:
            start_coords: 起点坐标 (lng, lat)
            end_coords: 终点坐标 (lng, lat)
            strategies: 策略列表，默认使用5种策略
                0: 速度优先
                1: 费用优先
                2: 距离优先
                3: 不走高速
                4: 躲避拥堵

        Returns:
            路径列表，每条路径包含 coords, distance, duration, strategy, polyline
        """
        if strategies is None:
            strategies = [0, 1, 2, 3, 4]

        routes = []
        for strategy in strategies:
            try:
                params = {
                    "key": self.api_key,
                    "origin": f"{start_coords[0]},{start_coords[1]}",
                    "destination": f"{end_coords[0]},{end_coords[1]}",
                    "city": self.default_city,
                    "output": "json",
                    "strategy": strategy,
                    "extensions": "all"
                }

                response = requests.get(self.route_url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                if data["status"] == "1" and len(data["route"]["paths"]) > 0:
                    path = data["route"]["paths"][0]
                    route_coords = []

                    # 提取polyline
                    polylines = []
                    for step in path.get("steps", []):
                        polyline = step.get("polyline", "")
                        if polyline:
                            polylines.append(polyline)
                            for point in polyline.split(";"):
                                lng, lat = map(float, point.split(","))
                                route_coords.append((lat, lng))

                    routes.append({
                        "coords": route_coords,
                        "distance": float(path.get("distance", 0)),
                        "duration": int(path.get("duration", 0)),
                        "strategy": strategy,
                        "polyline": ";".join(polylines),
                        "strategy_name": self._get_strategy_name(strategy)
                    })
            except Exception as e:
                logger.warning(f"策略{strategy}获取路径失败: {e}")
                continue

        return routes

    def _get_strategy_name(self, strategy: int) -> str:
        """获取策略名称"""
        return {
            0: "速度优先",
            1: "费用优先",
            2: "距离优先",
            3: "不走高速",
            4: "躲避拥堵"
        }.get(strategy, f"策略{strategy}")

    def get_route_with_waypoints(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        waypoints: List[Tuple[float, float]] = None,
        strategy: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        获取带途经点的驾车路径

        Args:
            start_coords: 起点坐标 (lng, lat)
            end_coords: 终点坐标 (lng, lat)
            waypoints: 途经点列表 [(lng, lat), ...]
            strategy: 策略ID (0-4)

        Returns:
            路径信息字典，包含 coords, distance, duration, waypoints 等
        """
        if not waypoints:
            return self.get_driving_route(start_coords, end_coords)

        try:
            # 高德API途经点格式: lng,lat|lng,lat|...
            waypoint_str = "|".join([f"{wp[0]},{wp[1]}" for wp in waypoints])

            params = {
                "key": self.api_key,
                "origin": f"{start_coords[0]},{start_coords[1]}",
                "destination": f"{end_coords[0]},{end_coords[1]}",
                "waypoints": waypoint_str,
                "city": self.default_city,
                "output": "json",
                "strategy": strategy,
                "extensions": "all"
            }

            response = requests.get(self.route_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "1" and len(data["route"]["paths"]) > 0:
                path = data["route"]["paths"][0]
                route_coords = []

                # 提取polyline
                polylines = []
                for step in path.get("steps", []):
                    polyline = step.get("polyline", "")
                    if polyline:
                        polylines.append(polyline)
                        for point in polyline.split(";"):
                            lng, lat = map(float, point.split(","))
                            route_coords.append((lat, lng))

                return {
                    "coords": route_coords,
                    "distance": float(path.get("distance", 0)),
                    "duration": int(path.get("duration", 0)),
                    "waypoints": waypoints,
                    "polyline": ";".join(polylines),
                    "strategy": strategy
                }
        except requests.Timeout:
            logger.error(f"途经点路径规划超时: {self.route_url}, timeout={self.timeout}s")
        except requests.ConnectionError as e:
            logger.error(f"途经点路径规划网络连接失败: {self.route_url}, error={str(e)}")
        except requests.RequestException as e:
            logger.error(f"途经点路径规划请求失败: {self.route_url}, error={str(e)}")
        except Exception as e:
            logger.error(f"途经点路径规划未知错误: error={str(e)}")

        return None

    def search_poi_near_route(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        keywords: List[str] = None,
        num_waypoints: int = 3
    ) -> List[Tuple[float, float, str]]:
        """
        在起点和终点之间搜索POI作为途经点

        Args:
            start_coords: 起点坐标 (lng, lat)
            end_coords: 终点坐标 (lng, lat)
            keywords: POI关键词列表，如["商场", "公园", "医院"]
            num_waypoints: 需要的途经点数量

        Returns:
            途经点列表 [(lng, lat, name), ...]
        """
        if keywords is None:
            keywords = ["商场", "广场", "公园", "医院", "学校", "银行"]

        # 计算中点区域
        mid_lng = (start_coords[0] + end_coords[0]) / 2
        mid_lat = (start_coords[1] + end_coords[1]) / 2

        # 计算搜索半径（基于起点终点距离）
        from ..algorithms.distance_utils import haversine_distance
        total_distance = haversine_distance(start_coords[0], start_coords[1],
                                            end_coords[0], end_coords[1])
        search_radius = min(max(int(total_distance / 3), 1000), 5000)  # 1-5km

        waypoints = []

        for keyword in keywords:
            if len(waypoints) >= num_waypoints:
                break

            try:
                params = {
                    "key": self.api_key,
                    "keywords": keyword,
                    "location": f"{mid_lng},{mid_lat}",
                    "radius": search_radius,
                    "city": self.default_city,
                    "offset": 5,
                    "page": 1,
                    "output": "json"
                }

                response = requests.get(self.poi_url, params=params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                if data["status"] == "1" and int(data["count"]) > 0:
                    for poi in data["pois"][:num_waypoints]:
                        lng, lat = map(float, poi["location"].split(","))
                        name = poi["name"]

                        # 避免与起点终点太近
                        dist_to_start = haversine_distance(start_coords[0], start_coords[1],
                                                          lng, lat)
                        dist_to_end = haversine_distance(end_coords[0], end_coords[1],
                                                        lng, lat)

                        if dist_to_start > 500 and dist_to_end > 500:  # 至少距离500米
                            waypoints.append((lng, lat, name))
                            if len(waypoints) >= num_waypoints:
                                break
            except Exception as e:
                logger.warning(f"搜索POI途经点失败 ({keyword}): {e}")
                continue

        return waypoints

    def get_multiple_routes_with_waypoints(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float]
    ) -> List[Dict[str, Any]]:
        """
        获取多条路径：直达路线 + 带途经点的绕行路线

        Args:
            start_coords: 起点坐标 (lng, lat)
            end_coords: 终点坐标 (lng, lat)

        Returns:
            路径列表，包含直达路线和绕行路线
        """
        routes = []

        # 1. 获取直达路线（推荐策略）
        direct_route = self.get_driving_route(start_coords, end_coords)
        if direct_route:
            direct_route["route_type"] = "direct"
            direct_route["route_name"] = "直达路线"
            routes.append(direct_route)

        # 2. 搜索POI作为途经点
        waypoints = self.search_poi_near_route(start_coords, end_coords)

        # 3. 为每个途经点创建绕行路线
        for i, (lng, lat, name) in enumerate(waypoints[:3]):  # 最多3个途经点
            waypoint_route = self.get_route_with_waypoints(
                start_coords, end_coords,
                waypoints=[(lng, lat)],
                strategy=1
            )
            if waypoint_route:
                waypoint_route["route_type"] = f"waypoint_{i}"
                waypoint_route["route_name"] = f"经由{name}"
                routes.append(waypoint_route)

        # 4. 如果没有绕行路线，尝试不同策略
        if len(routes) <= 1:
            for strategy in [0, 2, 4]:
                alt_route = self.get_driving_route_with_strategy(
                    start_coords, end_coords, strategy
                )
                if alt_route:
                    alt_route["route_type"] = f"strategy_{strategy}"
                    alt_route["route_name"] = self._get_strategy_name(strategy)
                    routes.append(alt_route)

        return routes

    def get_driving_route_with_strategy(
        self,
        start_coords: Tuple[float, float],
        end_coords: Tuple[float, float],
        strategy: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        使用指定策略获取驾车路径

        Args:
            start_coords: 起点坐标 (lng, lat)
            end_coords: 终点坐标 (lng, lat)
            strategy: 策略ID

        Returns:
            路径信息字典
        """
        try:
            params = {
                "key": self.api_key,
                "origin": f"{start_coords[0]},{start_coords[1]}",
                "destination": f"{end_coords[0]},{end_coords[1]}",
                "city": self.default_city,
                "output": "json",
                "strategy": strategy,
                "extensions": "all"
            }

            response = requests.get(self.route_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if data["status"] == "1" and len(data["route"]["paths"]) > 0:
                path = data["route"]["paths"][0]
                route_coords = []

                polylines = []
                for step in path.get("steps", []):
                    polyline = step.get("polyline", "")
                    if polyline:
                        polylines.append(polyline)
                        for point in polyline.split(";"):
                            lng, lat = map(float, point.split(","))
                            route_coords.append((lat, lng))

                return {
                    "coords": route_coords,
                    "distance": float(path.get("distance", 0)),
                    "duration": int(path.get("duration", 0)),
                    "strategy": strategy,
                    "polyline": ";".join(polylines)
                }
        except Exception as e:
            logger.warning(f"策略{strategy}获取路径失败: {e}")

        return None

    def clear_cache(self):
        """清除地址缓存"""
        self.get_coordinates.cache_clear()


# 全局服务实例
_amap_service = None


def get_amap_service() -> AmapService:
    """获取全局高德API服务实例"""
    global _amap_service
    if _amap_service is None:
        _amap_service = AmapService()
    return _amap_service
