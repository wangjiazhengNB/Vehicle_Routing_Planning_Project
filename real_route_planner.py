import folium
from get_real_road_data import (
    high_precision_lnglat,
    get_amap_route,
    calculate_distance,
    cache_address_coords
)

# 生成高德可视化地图并保存为HTML文件
def generate_amap(start_info, end_info, route_coords):
    start_lng, start_lat, start_poi = start_info
    end_lng, end_lat, end_poi = end_info
    
    # 计算距离并设置自适应缩放级别
    distance_m = calculate_distance(start_lng, start_lat, end_lng, end_lat)
    if distance_m < 1000:
        zoom_level = 17
    elif distance_m < 5000:
        zoom_level = 15
    elif distance_m < 10000:
        zoom_level = 14
    else:
        zoom_level = 13
    
    # 高德矢量底图配置
    gaode_tiles = (
        'http://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&style=7&x={x}&y={y}&z={z}'
    )
    
    # 初始化地图
    center_lat = (start_lat + end_lat) / 2
    center_lng = (start_lng + end_lng) / 2
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=zoom_level,
        tiles=gaode_tiles,
        attr='高德地图'
    )
    
    # 添加起点/终点标记
    folium.Marker(
        location=[start_lat, start_lng],
        popup=f"起点：{start_poi}",
        icon=folium.Icon(color="green", icon="flag")
    ).add_to(m)
    
    folium.Marker(
        location=[end_lat, end_lng],
        popup=f"终点：{end_poi}",
        icon=folium.Icon(color="red", icon="flag")
    ).add_to(m)
    
    # 绘制路径
    if route_coords:
        folium.PolyLine(
            route_coords,
            color="blue",
            weight=6,
            opacity=0.9,
            popup=f"{start_poi} → {end_poi}",
            smooth_factor=0.1
        ).add_to(m)
    
    # 保存地图并处理中文编码
    map_file = "real_route_map.html"
    m.save(map_file)
    
    with open(map_file, "r+", encoding="utf-8") as f:
        content = f.read()
        f.seek(0)
        f.write(content)
        f.truncate()
    
    return map_file

# 主交互流程
def main():
    print("=== 湘潭市高精度驾车路径规划 ===\n")
    
    # 输入并验证起点
    while True:
        start_addr = input("请输入起点：").strip()
        if not start_addr:
            print("提示：起点不能为空，请重新输入")
            continue
        start_info = cache_address_coords(start_addr)
        if start_info[0] is not None:
            break
        print("提示：地址定位失败，请输入更具体的地址（如：湘潭大学南门）")
    
    # 输入并验证终点
    while True:
        end_addr = input("请输入终点：").strip()
        if not end_addr:
            print("提示：终点不能为空，请重新输入")
            continue
        end_info = cache_address_coords(end_addr)
        if end_info[0] is not None:
            break
        print("提示：地址定位失败，请输入更具体的地址（如：万达广场1号门）")
    
    # 路径规划与地图生成
    print("\n正在规划最优路径...")
    start_lnglat = (start_info[0], start_info[1])
    end_lnglat = (end_info[0], end_info[1])
    route_coords, distance, duration = get_amap_route(start_lnglat, end_lnglat)
    
    if route_coords:
        map_file = generate_amap(start_info, end_info, route_coords)
        print(f"\n规划完成！")
        print(f"总距离：{distance}米，预计耗时：{int(duration)//60}分钟")
        print(f"地图文件已生成：{map_file}（双击即可打开）")
    else:
        print("\n提示：路径规划失败，无法生成路线地图")

# 程序入口
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已被用户终止")
    except Exception:
        print("\n\n程序运行出错，请检查网络或地址是否正确")