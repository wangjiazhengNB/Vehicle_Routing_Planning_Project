import pandas as pd
import numpy as np
import folium

def load_road_data():
    try:
        df = pd.read_csv("road_data.csv")
        return df
    except Exception as e:
        print("读数据失败 :", e)
        return None
    
    
def calc_total_cost(df):
    distance = np.array(df["distance"])
    congestion = np.array(df["congestion"])
    construction = np.array(df["construction"])

    weight_distance = 0.5
    weight_congestion = 0.3
    weight_construction = 0.2

    construction_cost = np.where(construction == 1, 5, 0)
    total_cost = np.sum(distance * weight_distance + congestion * weight_congestion + construction_cost * weight_construction)
    return total_cost

def draw_route_map():
   start = (39.9042, 116.4074)  # 起点
   end = (39.9242, 116.4174)    # 终点
   route = [start, (39.9142, 116.4074), end]
   
   # 创建地图
   map_obj = folium.Map(location=start, zoom_start=14)
   # 起点为绿色
   folium.Marker(start, popup="起点", icon=folium.Icon(color="green")).add_to(map_obj)
   # 终点为红色
   folium.Marker(end, popup="终点", icon=folium.Icon(color="red")).add_to(map_obj)
   # 路径为蓝色
   folium.PolyLine(route, color="blue", weight=5).add_to(map_obj)

   # 保存地图为HTML文件
   map_obj.save("route_map.html")
   print("地图已经保存成：route_map.html")

if __name__ == "__main__":
    # 读数据
    road_df = load_road_data()
    if road_df is None:
        print("程序结束")
        exit()
    
    # 算总代价
    total_cost = calc_total_cost(road_df)
    print("所有道路的多目标总代价是：", round(total_cost, 2))

    # 画地图
    draw_route_map()
    print("demo运行完成!")

    