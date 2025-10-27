import json
import numpy as np
import matplotlib
from collections import deque

matplotlib.use('TkAgg')  # 或其他可用后端如'Qt5Agg'
import matplotlib.pyplot as plt
from matplotlib.table import Table
import os

plt.rcParams["font.family"] = ["SimHei"]  # window设置中文字体


# plt.rcParams["font.family"] = ["Heiti TC", "STHeiti"]  # mac设置中文字体


def map_initialization(data):
    xmin = data['环境配置']['整体布局']['xmin']
    xhigh = data['环境配置']['整体布局']['xhigh']
    ymin = data['环境配置']['整体布局']['ymin']
    yhigh = data['环境配置']['整体布局']['yhigh']

    map_matrix = [[-1] * (yhigh - ymin + 1) for _ in range(xhigh - xmin + 1)]

    # 布置区域
    sector = data['环境配置']['有效区域']
    for key, value in sector.items():
        for _, sector0 in value['范围'].items():
            xmin = sector0['xmin']
            xhigh = sector0['xhigh']
            ymin = sector0['ymin']
            yhigh = sector0['yhigh']
            for i in range(xmin, xhigh + 1):
                for j in range(ymin, yhigh + 1):
                    map_matrix[i][j] = 1

    # 布置传感器
    sensor = data['环境配置']['传感器']
    for key, value in sensor.items():
        x = value['x']
        y = value['y']
        if 'Door' in key:
            map_matrix[x][y] = 2
        elif 'Motion' in key:
            map_matrix[x][y] = 3
        else:
            raise Exception("no such sensor type")

    # 布置设备
    device = data['环境配置']['控制设备']
    for key, value in device.items():
        x = value['x']
        y = value['y']
        map_matrix[x][y] = 4

    # 布置设施
    device = data['环境配置']['设施']
    for key, value in device.items():
        x = value['x']
        y = value['y']
        map_matrix[x][y] = 5
    return map_matrix


def create_color_table(matrix):
    # map可视化
    # 定义颜色映射，1-5分别对应不同颜色
    color_map = {
        1: "#FFFFFF",  # 白色
        2: "#FFFF00",  # 黄色
        3: "#00FA9A",  # 绿色
        4: "#00BFFF",  # 蓝色
        5: "#DC143C",  # 红色
        -1: "#808080"  # 灰色
    }

    # 获取矩阵的行列数
    n_rows, n_cols = len(matrix), len(matrix[0])

    # 创建图形和坐标轴
    fig, ax = plt.subplots(figsize=(n_cols, n_rows))
    ax.set_axis_off()  # 隐藏坐标轴

    # 创建表格
    table = Table(ax, bbox=[0, 0, 1, 1])

    # 添加单元格
    cell_width = 1.0 / n_cols
    cell_height = 1.0 / n_rows

    for i in range(n_rows):
        for j in range(n_cols):
            value = matrix[i][j]
            # 确保值在1-5范围内
            if value not in color_map:
                raise ValueError(f"矩阵值必须是1-5之间的整数，发现值: {value}")

            # 添加单元格，设置背景颜色
            table.add_cell(i, j, cell_width, cell_height, text=value,
                           loc='center', facecolor=color_map[value])

    # 将表格添加到坐标轴
    ax.add_table(table)

    plt.title("矩阵颜色表格")
    plt.show()


def load_prompt_dict(folder_path):
    prompt_dict = {}
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                prompt_dict[filename] = content
    return prompt_dict


def get_weekday(current_day):
    current_day = current_day % 7
    if current_day == 0:
        return "星期一"
    elif current_day == 1:
        return "星期二"
    elif current_day == 2:
        return "星期三"
    elif current_day == 3:
        return "星期四"
    elif current_day == 4:
        return "星期五"
    elif current_day == 5:
        return "星期六"
    else:
        return "星期日"


def get_activity_str(data):
    activity_str = ''
    for activity in data['活动配置']:
        activity_name = activity['活动名称']
        activity_str = activity_name + ', ' + activity_str
    print(activity_str)


def move_to_area(position_from, area_to, map_matrix):
    """
    移动到目标区域内的任意可达位置

    Args:
        position_from: 起点位置 [x, y]
        area_to: 目标区域字典，包含多个子区域
        map_matrix: 地图矩阵，0表示可达，1表示障碍

    Returns:
        最短路径列表，如果无法到达则返回空列表
    """
    # 如果起点不可达，直接返回空路径
    if not is_valid_position(position_from, map_matrix):
        return []

    # 如果起点已经在目标区域内
    if is_position_in_area(position_from, area_to):
        return [position_from]

    rows = len(map_matrix)
    cols = len(map_matrix[0]) if rows > 0 else 0

    # 方向：上、右、下、左
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    # 记录访问状态、路径和距离
    visited = [[False] * cols for _ in range(rows)]
    parent = [[None] * cols for _ in range(rows)]
    distance = [[-1] * cols for _ in range(rows)]

    # BFS队列
    queue = deque()
    start_x, start_y = position_from
    queue.append((start_x, start_y))
    visited[start_x][start_y] = True
    distance[start_x][start_y] = 0

    found_positions = []  # 存储找到的目标区域内的位置

    while queue:
        x, y = queue.popleft()

        # 如果当前位置在目标区域内，记录下来
        if is_position_in_area([x, y], area_to):
            found_positions.append((x, y, distance[x][y]))

        # 遍历四个方向
        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # 检查新位置是否有效且未被访问
            if (0 <= nx < rows and 0 <= ny < cols and
                    not visited[nx][ny] and is_valid_position([nx, ny], map_matrix)):
                visited[nx][ny] = True
                parent[nx][ny] = (x, y)
                distance[nx][ny] = distance[x][y] + 1
                queue.append((nx, ny))

    # 如果没有找到任何可达的目标位置
    if not found_positions:
        return []

    # 找到距离最近的目标位置
    found_positions.sort(key=lambda pos: pos[2])  # 按距离排序
    closest_x, closest_y, _ = found_positions[0]

    # 回溯构建路径
    path = []
    current = (closest_x, closest_y)

    # 回溯到起点
    while current != (start_x, start_y):
        path.append([current[0], current[1]])
        current = parent[current[0]][current[1]]

    path.append([start_x, start_y])
    path.reverse()  # 反转路径，从起点到终点

    return path


def move_to_position(position_from, position_to, map_matrix):
    # 如果起点或终点不可达，直接返回空路径
    if (not is_valid_position(position_from, map_matrix) or
            not is_valid_position(position_to, map_matrix)):
        return []

    # 如果起点和终点相同
    if position_from == position_to:
        return [position_from]

    # BFS寻找最短路径
    rows = len(map_matrix)
    cols = len(map_matrix[0]) if rows > 0 else 0

    # 方向：上、右、下、左
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    # 记录访问状态和路径
    visited = [[False] * cols for _ in range(rows)]
    parent = [[None] * cols for _ in range(rows)]

    # BFS队列
    queue = deque()
    start_x, start_y = position_from
    queue.append((start_x, start_y))
    visited[start_x][start_y] = True

    found = False
    end_x, end_y = position_to

    while queue:
        x, y = queue.popleft()

        # 如果到达终点
        if x == end_x and y == end_y:
            found = True
            break

        # 遍历四个方向
        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # 检查新位置是否有效且未被访问
            if (0 <= nx < rows and 0 <= ny < cols and
                    not visited[nx][ny] and is_valid_position([nx, ny], map_matrix)):
                visited[nx][ny] = True
                parent[nx][ny] = (x, y)
                queue.append((nx, ny))

    # 如果找到路径，回溯构建路径
    if found:
        path = []
        current = (end_x, end_y)

        # 回溯到起点
        while current != (start_x, start_y):
            path.append([current[0], current[1]])
            current = parent[current[0]][current[1]]

        path.append([start_x, start_y])
        path.reverse()  # 反转路径，从起点到终点

        return path

    return []  # 没有找到路径


def is_position_in_area(position, area_to):
    """
    检查位置是否在目标区域的任何一个子区域内
    """
    x, y = position

    # 遍历所有子区域
    for area_name, area_bounds in area_to.items():
        xmin = area_bounds["xmin"]
        xhigh = area_bounds["xhigh"]
        ymin = area_bounds["ymin"]
        yhigh = area_bounds["yhigh"]

        if (xmin <= x <= xhigh and ymin <= y <= yhigh):
            return True

    return False


def is_valid_position(position, map_matrix):
    """检查位置是否有效且可达"""
    x, y = position
    rows = len(map_matrix)
    cols = len(map_matrix[0]) if rows > 0 else 0

    # 检查边界
    if x < 0 or x >= rows or y < 0 or y >= cols:
        return False

    # 检查是否可达（值不为-1且不为4）
    value = map_matrix[x][y]
    return value != -1 and value != 4


def str_time2int_time(str_time):
    """将"时:分"格式的字符串转换为分钟数"""
    # 只分割一次字符串，避免重复操作
    hour_str, minute_str = str_time.split(":")
    return int(hour_str) * 60 + int(minute_str)


def int_time2str_time(int_time):
    """将分钟数转换为"时:分"格式的字符串（自动处理超过24小时的情况）"""
    # 取模处理超过24小时的情况，使用整除和取余更简洁
    total_minutes = int_time % (24 * 60)
    hour = total_minutes // 60
    minute = total_minutes % 60
    # 确保分钟数始终为两位数（如 9:5 → 09:05）
    return f"{hour:02d}:{minute:02d}"


def adjust_toilet_prob(toilet_prob, diff_time):
    if diff_time < 1:
        # 1小时内上过厕所，概率大幅降低
        time_factor = 0.1
    elif diff_time < 3:
        # 1-3小时内上过厕所，概率适度降低
        time_factor = 0.3
    elif diff_time < 6:
        # 3-6小时内上过厕所，概率轻微降低
        time_factor = 0.7
    elif diff_time > 8:
        # 超过8小时没上厕所，概率适度增加
        time_factor = 2
    else:
        # 6-8小时，正常概率
        time_factor = 1.0
    return time_factor * toilet_prob


# # 测试示例
# if __name__ == "__main__":
#     # 测试地图
#     test_map = [
#         [0, 0, 0, 0],
#         [0, -1, 4, 0],
#         [0, 0, 0, 0],
#         [0, 4, -1, 0]
#     ]
#
#     # 测试用例
#     start = [0, 0]
#     end = [3, 3]
#
#     path = move_to_position(start, end, test_map)
#     print("路径:", path)
#
#     # 另一个测试用例
#     start2 = [0, 0]
#     end2 = [1, 2]  # 这个位置不可达
#
#     path2 = move_to_position(start2, end2, test_map)
#     print("到不可达位置的路径:", path2)

if __name__ == "__main__":
    # 测试地图1：简单无障碍地图
    test_map1 = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]

    # 测试地图2：有障碍物地图
    test_map2 = [
        [0, 0, 0, 0],
        [0, -1, 4, 0],
        [0, 0, 0, 0],
        [0, 4, -1, 0]
    ]

    # 测试地图3：复杂障碍地图
    test_map3 = [
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ]

    # 定义目标区域
    area1 = {
        "区域一": {
            "xmin": 2,
            "xhigh": 3,
            "ymin": 2,
            "yhigh": 3
        }
    }

    area2 = {
        "区域一": {
            "xmin": 1,
            "xhigh": 2,
            "ymin": 1,
            "yhigh": 2
        },
        "区域二": {
            "xmin": 3,
            "xhigh": 3,
            "ymin": 3,
            "yhigh": 3
        }
    }

    print("=== 测试1: 简单地图到单区域 ===")
    start1 = [0, 0]
    path1 = move_to_area(start1, area1, test_map1)
    print(f"从 {start1} 到区域 {area1} 的路径: {path1}")

    print("\n=== 测试2: 有障碍物地图到单区域 ===")
    start2 = [0, 0]
    path2 = move_to_area(start2, area1, test_map2)
    print(f"从 {start2} 到区域 {area1} 的路径: {path2}")

    print("\n=== 测试3: 复杂地图到多区域 ===")
    start3 = [0, 0]
    path3 = move_to_area(start3, area2, test_map3)
    print(f"从 {start3} 到区域 {area2} 的路径: {path3}")

    print("\n=== 测试4: 起点已在区域内 ===")
    start4 = [2, 2]
    path4 = move_to_area(start4, area1, test_map1)
    print(f"从 {start4} 到区域 {area1} 的路径: {path4}")

    print("\n=== 测试5: 无法到达区域 ===")
    # 创建一个被隔离的区域
    isolated_area = {
        "隔离区域": {
            "xmin": 0,
            "xhigh": 0,
            "ymin": 4,
            "yhigh": 4
        }
    }
    start5 = [0, 0]
    path5 = move_to_area(start5, isolated_area, test_map3)
    print(f"从 {start5} 到区域 {isolated_area} 的路径: {path5}")

    print("\n=== 测试6: 你的示例区域 ===")
    example_area = {
        "区域一": {
            "xmin": 1,
            "xhigh": 8,
            "ymin": 1,
            "yhigh": 10
        },
        "区域二": {
            "xmin": 9,
            "xhigh": 10,
            "ymin": 4,
            "yhigh": 10
        }
    }
    # 创建一个更大的测试地图
    large_map = [[0] * 11 for _ in range(11)]
    start6 = [0, 0]
    path6 = move_to_area(start6, example_area, large_map)
    print(f"从 {start6} 到示例区域的路径长度: {len(path6)}")
    print(f"路径终点: {path6[-1] if path6 else '无路径'}")
