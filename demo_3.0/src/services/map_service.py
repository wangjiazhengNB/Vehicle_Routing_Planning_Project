"""地图生成服务

复用 demo_2.0 的代码，封装Folium地图生成功能
"""

import folium
import os
from typing import List, Tuple, Optional, Dict, Any

from ..config.settings import get_config
from ..algorithms.distance_utils import calculate_distance

config = get_config()


class MapService:
    """地图生成服务类"""

    def __init__(self):
        """初始化地图服务"""
        self.tile_url = config.get("map.tile_url")
        self.attribution = config.get("map.attribution")
        self.default_zoom = config.get("map.default_zoom", 14)

    def generate_route_map(self, start_info: Tuple[float, float, str],
                          end_info: Tuple[float, float, str],
                          route_coords: Optional[List[Tuple[float, float]]] = None,
                          output_file: str = None) -> str:
        """
        生成路径规划地图并保存为HTML文件

        Args:
            start_info: 起点信息 (lng, lat, name)
            end_info: 终点信息 (lng, lat, name)
            route_coords: 路径坐标列表 [(lat, lng), ...]
            output_file: 输出文件路径，默认自动生成

        Returns:
            地图HTML文件路径
        """
        start_lng, start_lat, start_name = start_info
        end_lng, end_lat, end_name = end_info

        # 计算距离并设置自适应缩放级别
        distance_m = calculate_distance(start_lng, start_lat, end_lng, end_lat)
        zoom_level = self._calculate_zoom_level(distance_m)

        # 初始化地图
        center_lat = (start_lat + end_lat) / 2
        center_lng = (start_lng + end_lng) / 2

        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=zoom_level,
            tiles=self.tile_url,
            attr=self.attribution
        )

        # 添加起点标记
        folium.Marker(
            location=[start_lat, start_lng],
            popup=f"起点：{start_name}",
            icon=folium.Icon(color="green", icon="flag")
        ).add_to(m)

        # 添加终点标记
        folium.Marker(
            location=[end_lat, end_lng],
            popup=f"终点：{end_name}",
            icon=folium.Icon(color="red", icon="flag")
        ).add_to(m)

        # 绘制路径
        if route_coords:
            folium.PolyLine(
                route_coords,
                color="blue",
                weight=6,
                opacity=0.9,
                popup=f"{start_name} → {end_name}",
                smooth_factor=0.1
            ).add_to(m)

        # 生成输出文件名
        if output_file is None:
            output_dir = "output/maps"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"route_map_{int(distance_m)}.html")

        # 保存地图
        m.save(output_file)

        # 处理中文编码
        self._fix_chinese_encoding(output_file)

        return output_file

    def _calculate_zoom_level(self, distance_m: float) -> int:
        """
        根据距离计算合适的缩放级别

        Args:
            distance_m: 距离（米）

        Returns:
            缩放级别
        """
        if distance_m < 1000:
            return 17
        elif distance_m < 5000:
            return 15
        elif distance_m < 10000:
            return 14
        elif distance_m < 20000:
            return 13
        else:
            return 12

    def _fix_chinese_encoding(self, file_path: str):
        """
        修复地图文件的中文编码问题

        Args:
            file_path: 地图HTML文件路径
        """
        try:
            with open(file_path, "r+", encoding="utf-8") as f:
                content = f.read()
                f.seek(0)
                f.write(content)
                f.truncate()
        except Exception as e:
            print(f"修复中文编码失败: {e}")

    def generate_comparison_map(self, routes: Dict[str, Dict[str, Any]],
                                start_info: Tuple[float, float, str],
                                end_info: Tuple[float, float, str]) -> str:
        """
        生成多算法对比地图

        Args:
            routes: 算法路径字典 {算法名: {coords: [...], cost: ...}}
            start_info: 起点信息
            end_info: 终点信息

        Returns:
            地图HTML文件路径
        """
        start_lng, start_lat, start_name = start_info
        end_lng, end_lat, end_name = end_info

        # 计算中心点和缩放
        center_lat = (start_lat + end_lat) / 2
        center_lng = (start_lng + end_lng) / 2

        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=self.default_zoom,
            tiles=self.tile_url,
            attr=self.attribution
        )

        # 颜色映射
        colors = {
            "Dijkstra": "blue",
            "PSO": "green",
            "A*": "red",
            "Default": "orange"
        }

        # 添加起点和终点
        folium.Marker(
            location=[start_lat, start_lng],
            popup=f"起点：{start_name}",
            icon=folium.Icon(color="green", icon="play")
        ).add_to(m)

        folium.Marker(
            location=[end_lat, end_lng],
            popup=f"终点：{end_name}",
            icon=folium.Icon(color="red", icon="stop")
        ).add_to(m)

        # 绘制多条路径
        for algo_name, route_data in routes.items():
            coords = route_data.get('coords', [])
            cost = route_data.get('cost', 0)
            color = colors.get(algo_name, "gray")

            folium.PolyLine(
                coords,
                color=color,
                weight=4,
                opacity=0.7,
                popup=f"{algo_name}: 成本={cost:.2f}",
                tooltip=algo_name
            ).add_to(m)

        # 保存地图
        output_dir = "output/maps"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "route_comparison.html")
        m.save(output_file)

        return output_file


# 全局服务实例
_map_service = None


def get_map_service() -> MapService:
    """获取全局地图服务实例"""
    global _map_service
    if _map_service is None:
        _map_service = MapService()
    return _map_service
