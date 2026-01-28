import requests
from functools import lru_cache

# 高德API配置
AMAP_KEY = "33dfc2e2f2c13df1e239242db84d5e29"
AMAP_POI_URL = "https://restapi.amap.com/v3/place/text"
AMAP_GEOCODE_URL = "https://restapi.amap.com/v3/geocode/geo"
AMAP_ROUTE_URL = "https://restapi.amap.com/v3/direction/driving"

# 缓存最多50个地址坐标，避免重复请求API
@lru_cache(maxsize=50)
def cache_address_coords(address):
    return high_precision_lnglat(address)

# 地址标准化：自动补充湘潭市及对应行政区
def standardize_address(address):
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
            return f"湘潭市{area}{address}"
    
    if not address.startswith("湘潭市"):
        return f"湘潭市{address}"
    
    return address

# 高精度定位：优先POI搜索，兜底地理编码
def high_precision_lnglat(address):
    std_addr = standardize_address(address)
    
    # 第一步：POI精准搜索
    try:
        poi_params = {
            "key": AMAP_KEY,
            "keywords": address,
            "city": "湘潭市",
            "children": 0,
            "offset": 1,
            "page": 1,
            "output": "json"
        }
        
        res = requests.get(AMAP_POI_URL, params=poi_params, timeout=5)
        res.raise_for_status()
        data = res.json()
        
        if data["status"] == "1" and int(data["count"]) > 0:
            poi = data["pois"][0]
            lng = float(poi["location"].split(",")[0])
            lat = float(poi["location"].split(",")[1])
            return (lng, lat, poi["name"])
    except:
        pass
    
    # 第二步：地理编码兜底
    try:
        geo_params = {
            "key": AMAP_KEY,
            "address": std_addr,
            "city": "湘潭市",
            "extensions": "all",
            "output": "json"
        }
        
        res = requests.get(AMAP_GEOCODE_URL, params=geo_params, timeout=5)
        res.raise_for_status()
        data = res.json()
        
        if data["status"] == "1" and len(data["geocodes"]) > 0:
            geo = data["geocodes"][0]
            lng = float(geo["location"].split(",")[0])
            lat = float(geo["location"].split(",")[1])
            return (lng, lat, address)
    except:
        pass
    
    return (None, None, None)

# 计算两点间直线距离（单位：米）
def calculate_distance(lng1, lat1, lng2, lat2):
    from math import radians, sin, cos, sqrt, atan2
    
    lat1, lon1 = radians(lat1), radians(lng1)
    lat2, lon2 = radians(lat2), radians(lng2)
    R = 6371000
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

# 高德路径规划：返回路径坐标列表、总距离、总耗时
def get_amap_route(start_lnglat, end_lnglat):
    params = {
        "key": AMAP_KEY,
        "origin": f"{start_lnglat[0]},{start_lnglat[1]}",
        "destination": f"{end_lnglat[0]},{end_lnglat[1]}",
        "city": "湘潭市",
        "output": "json",
        "strategy": 1,
        "extensions": "all"
    }
    
    try:
        res = requests.get(AMAP_ROUTE_URL, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        if data["status"] == "1" and len(data["route"]["paths"]) > 0:
            path = data["route"]["paths"][0]
            route_coords = []
            
            for step in path["steps"]:
                for point in step["polyline"].split(";"):
                    lng, lat = map(float, point.split(","))
                    route_coords.append((lat, lng))
            
            return route_coords, path["distance"], path["duration"]
    except:
        pass
    
    return None, 0, 0