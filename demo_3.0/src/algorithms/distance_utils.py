"""距离计算工具模块

复用 demo_2.0 的 calculate_distance 函数，并扩展其他距离计算方法
"""

from math import radians, sin, cos, sqrt, atan2
from typing import Tuple


def haversine_distance(lng1: float, lat1: float, lng2: float, lat2: float) -> float:
    """
    使用Haversine公式计算两点间的大圆距离（球面距离）

    Args:
        lng1: 第一点的经度
        lat1: 第一点的纬度
        lng2: 第二点的经度
        lat2: 第二点的纬度

    Returns:
        两点间的距离（米）
    """
    lat1, lon1 = radians(lat1), radians(lng1)
    lat2, lon2 = radians(lat2), radians(lng2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    R = 6371000  # 地球半径（米）
    return R * c


def euclidean_distance(lng1: float, lat1: float, lng2: float, lat2: float) -> float:
    """
    计算两点间的欧几里得距离（直线距离）

    Args:
        lng1: 第一点的经度
        lat1: 第一点的纬度
        lng2: 第二点的经度
        lat2: 第二点的纬度

    Returns:
        两点间的距离（米），近似值
    """
    # 将经纬度转换为米（粗略估计）
    # 1度纬度约等于111km
    # 1度经度约等于111km * cos(纬度)
    lat_diff = (lat2 - lat1) * 111000
    lng_diff = (lng2 - lng1) * 111000 * cos(radians(lat1))

    return sqrt(lat_diff ** 2 + lng_diff ** 2)


def manhattan_distance(lng1: float, lat1: float, lng2: float, lat2: float) -> float:
    """
    计算两点间的曼哈顿距离（折线距离）

    Args:
        lng1: 第一点的经度
        lat1: 第一点的纬度
        lng2: 第二点的经度
        lat2: 第二点的纬度

    Returns:
        两点间的曼哈顿距离（米），近似值
    """
    # 将经纬度转换为米（粗略估计）
    lat_diff = abs(lat2 - lat1) * 111000
    lng_diff = abs(lng2 - lng1) * 111000 * cos(radians(lat1))

    return lat_diff + lng_diff


def calculate_distance(lng1: float, lat1: float, lng2: float, lat2: float,
                       method: str = 'haversine') -> float:
    """
    计算两点间距离（统一入口）

    Args:
        lng1: 第一点的经度
        lat1: 第一点的纬度
        lng2: 第二点的经度
        lat2: 第二点的纬度
        method: 计算方法 ('haversine', 'euclidean', 'manhattan')
                默认为 'haversine'，最准确

    Returns:
        两点间的距离（米）
    """
    methods = {
        'haversine': haversine_distance,
        'euclidean': euclidean_distance,
        'manhattan': manhattan_distance
    }

    if method not in methods:
        raise ValueError(f"不支持的 distance method: {method}. "
                        f"支持的选项: {list(methods.keys())}")

    return methods[method](lng1, lat1, lng2, lat2)


def calculate_distance_between_coords(coords1: Tuple[float, float],
                                     coords2: Tuple[float, float],
                                     method: str = 'haversine') -> float:
    """
    计算两个坐标点之间的距离

    Args:
        coords1: 第一个坐标 (lng, lat) 或 (lat, lng)
        coords2: 第二个坐标 (lng, lat) 或 (lat, lng)
        method: 计算方法，默认为 'haversine'

    Returns:
        两点间的距离（米）
    """
    # 自动检测坐标格式
    # 如果第一个值范围在[0, 180]，可能是经度
    # 如果第一个值范围在[-90, 90]，可能是纬度
    lng1, lat1 = _parse_coords(coords1)
    lng2, lat2 = _parse_coords(coords2)

    return calculate_distance(lng1, lat1, lng2, lat2, method)


def _parse_coords(coords: Tuple[float, float]) -> Tuple[float, float]:
    """
    解析坐标，确保格式为 (lng, lat)

    Args:
        coords: 坐标元组，可能是 (lng, lat) 或 (lat, lng)

    Returns:
        (lng, lat) 格式的坐标
    """
    if len(coords) != 2:
        raise ValueError(f"坐标格式错误: {coords}，应为 (lng, lat) 或 (lat, lng)")

    # 简单启发式：如果第一个值在[-90, 90]之间且大于第二个值，可能是纬度
    # 因为纬度范围是[-90, 90]，经度范围是[-180, 180]
    # 这个启发式不总是准确，但对中国大陆坐标通常有效
    if -90 <= coords[0] <= 90 and (coords[0] > coords[1] or coords[1] > 180):
        return coords[1], coords[0]  # 返回 (lng, lat)
    else:
        return coords[0], coords[1]  # 已经是 (lng, lat) 格式


# 为了兼容 demo_2.0，保留原函数名
def calculate_distance_original(lng1, lat1, lng2, lat2):
    """原始计算距离函数（兼容 demo_2.0）"""
    return calculate_distance(lng1, lat1, lng2, lat2)
