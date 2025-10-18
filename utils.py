import json
import numpy as np
import matplotlib

matplotlib.use('TkAgg')  # 或其他可用后端如'Qt5Agg'
import matplotlib.pyplot as plt
from matplotlib.table import Table
import os

plt.rcParams["font.family"] = ["SimHei"]  # 设置中文字体


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


def calculate_path(destination_from, destination_to, map_matrix):
    path = []
    return path
