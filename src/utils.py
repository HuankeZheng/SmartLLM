import json
import numpy as np
import matplotlib
from collections import deque

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.table import Table
import os

plt.rcParams["font.family"] = ["SimHei"]  # window


# plt.rcParams["font.family"] = ["Heiti TC", "STHeiti"]  # mac


def map_initialization(data):
    xmin = data['environment_config']['Layout']['xmin']
    xhigh = data['environment_config']['Layout']['xhigh']
    ymin = data['environment_config']['Layout']['ymin']
    yhigh = data['environment_config']['Layout']['yhigh']

    map_matrix = [[-1] * (yhigh - ymin + 1) for _ in range(xhigh - xmin + 1)]

    # set area
    sector = data['environment_config']['valid_area']
    for key, value in sector.items():
        for _, sector0 in value['Scope'].items():
            xmin = sector0['xmin']
            xhigh = sector0['xhigh']
            ymin = sector0['ymin']
            yhigh = sector0['yhigh']
            for i in range(xmin, xhigh + 1):
                for j in range(ymin, yhigh + 1):
                    map_matrix[i][j] = 1

    # set sensor
    sensor = data['environment_config']['sensor']
    for key, value in sensor.items():
        x = value['x']
        y = value['y']
        if 'Door' in key:
            map_matrix[x][y] = 2
        elif 'Motion' in key:
            map_matrix[x][y] = 3
        else:
            raise Exception("no such sensor type")

    # set device
    device = data['environment_config']['control_device']
    for key, value in device.items():
        x = value['x']
        y = value['y']
        map_matrix[x][y] = 4

    # set facility
    device = data['environment_config']['Facility']
    for key, value in device.items():
        x = value['x']
        y = value['y']
        map_matrix[x][y] = 5
    return map_matrix


def create_color_table(matrix):
    # map visualization
    # color map
    color_map = {
        1: "#FFFFFF",  # White
        2: "#FFFF00",  # Yellow
        3: "#00FA9A",  # Green
        4: "#00BFFF",  # Blue
        5: "#DC143C",  # Red
        -1: "#808080"  # Gray
    }

    n_rows, n_cols = len(matrix), len(matrix[0])

    fig, ax = plt.subplots(figsize=(n_cols, n_rows))
    ax.set_axis_off()

    table = Table(ax, bbox=[0, 0, 1, 1])

    cell_width = 1.0 / n_cols
    cell_height = 1.0 / n_rows

    for i in range(n_rows):
        for j in range(n_cols):
            value = matrix[i][j]
            if value not in color_map:
                raise ValueError(f"The matrix value must be an integer between 1 and 5: {value}")

            table.add_cell(i, j, cell_width, cell_height, text=value,
                           loc='center', facecolor=color_map[value])

    ax.add_table(table)

    plt.title("Matrix Color Chart")
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
        return "Monday"
    elif current_day == 1:
        return "Tuesday"
    elif current_day == 2:
        return "Wednesday"
    elif current_day == 3:
        return "Thursday"
    elif current_day == 4:
        return "Friday"
    elif current_day == 5:
        return "Saturday"
    else:
        return "Sunday"


def get_activity_str(data):
    activity_str = ''
    for activity in data['activity_config']:
        activity_name = activity['activity_name']
        if activity_name not in ["Toilet", "Phone", "Going Out"]:
            if activity_str == '':
                activity_str = activity_name
            else:
                activity_str = activity_str + ', ' + activity_name
    print(activity_str)
    return activity_str


def move_to_area(position_from, area_to, map_matrix):
    """
    Move to any reachable position within the target area

    Args:
        position_from: Starting position [x, y]
        area_to: Target area dictionary, containing multiple sub-areas
        map_matrix: Map matrix, where 0 indicates reachable and 1 indicates obstacle

    Returns:
        Shortest path list, returns empty list if unreachable
    """
    # If the starting point is unreachable, return an empty path directly.
    if not is_valid_position(position_from, map_matrix):
        return []

    # If the starting point is already within the target area
    if is_position_in_area(position_from, area_to):
        return [position_from]

    rows = len(map_matrix)
    cols = len(map_matrix[0]) if rows > 0 else 0

    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    # Record visited states, paths, and distances
    visited = [[False] * cols for _ in range(rows)]
    parent = [[None] * cols for _ in range(rows)]
    distance = [[-1] * cols for _ in range(rows)]

    # BFS queue
    queue = deque()
    start_x, start_y = position_from
    queue.append((start_x, start_y))
    visited[start_x][start_y] = True
    distance[start_x][start_y] = 0

    found_positions = []  # Store the position found within the target area.

    while queue:
        x, y = queue.popleft()

        # If the current position is within the target area, record it.
        if is_position_in_area([x, y], area_to):
            found_positions.append((x, y, distance[x][y]))

        # Traverse all four directions
        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Check if the new position is valid and has not been accessed
            if (0 <= nx < rows and 0 <= ny < cols and
                    not visited[nx][ny] and is_valid_position([nx, ny], map_matrix)):
                visited[nx][ny] = True
                parent[nx][ny] = (x, y)
                distance[nx][ny] = distance[x][y] + 1
                queue.append((nx, ny))

    # If no reachable target position is found
    if not found_positions:
        return []

    # Find the closest target position
    found_positions.sort(key=lambda pos: pos[2])
    closest_x, closest_y, _ = found_positions[0]

    # Trace the Build Path
    path = []
    current = (closest_x, closest_y)

    while current != (start_x, start_y):
        path.append([current[0], current[1]])
        current = parent[current[0]][current[1]]

    path.append([start_x, start_y])
    path.reverse()  # Reverse Path, From Start to End

    return path


def move_to_position(position_from, position_to, map_matrix):
    # If the start or end point is unreachable, return an empty path directly.
    if (not is_valid_position(position_from, map_matrix) or
            not is_valid_position(position_to, map_matrix)):
        return []

    # If the starting point and ending point are the same
    if position_from == position_to:
        return [position_from]

    # BFS for Finding the Shortest Path
    rows = len(map_matrix)
    cols = len(map_matrix[0]) if rows > 0 else 0

    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    visited = [[False] * cols for _ in range(rows)]
    parent = [[None] * cols for _ in range(rows)]

    queue = deque()
    start_x, start_y = position_from
    queue.append((start_x, start_y))
    visited[start_x][start_y] = True

    found = False
    end_x, end_y = position_to

    while queue:
        x, y = queue.popleft()

        if x == end_x and y == end_y:
            found = True
            break

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            if (0 <= nx < rows and 0 <= ny < cols and
                    not visited[nx][ny] and is_valid_position([nx, ny], map_matrix)):
                visited[nx][ny] = True
                parent[nx][ny] = (x, y)
                queue.append((nx, ny))

    if found:
        path = []
        current = (end_x, end_y)

        while current != (start_x, start_y):
            path.append([current[0], current[1]])
            current = parent[current[0]][current[1]]

        path.append([start_x, start_y])
        path.reverse()

        return path

    return []


def is_position_in_area(position, area_to):
    """
    Check whether the position is within any subarea of the target area.
    """
    x, y = position

    # Iterate through all sub-areas
    for area_name, area_bounds in area_to.items():
        xmin = area_bounds["xmin"]
        xhigh = area_bounds["xhigh"]
        ymin = area_bounds["ymin"]
        yhigh = area_bounds["yhigh"]

        if (xmin <= x <= xhigh and ymin <= y <= yhigh):
            return True

    return False


def is_valid_position(position, map_matrix):
    """Check if the position is valid and reachable"""
    x, y = position
    rows = len(map_matrix)
    cols = len(map_matrix[0]) if rows > 0 else 0

    if x < 0 or x >= rows or y < 0 or y >= cols:
        return False

    value = map_matrix[x][y]
    return value != -1


def str_time2int_time(str_time):
    """Convert a string in the format H:MM to a minute value"""
    hour_str, minute_str = str_time.split(":")
    return int(hour_str) * 60 + int(minute_str)


def int_time2str_time(int_time):
    """
    Convert minutes to a string in the h:m format (automatically handles values exceeding 24 hours)
    """
    total_minutes = int_time % (24 * 60)
    hour = total_minutes // 60
    minute = total_minutes % 60
    # 9:5 → 09:05）
    return f"{hour:02d}:{minute:02d}"


def adjust_toilet_prob(toilet_prob, diff_time):
    # Adjust the probability based on the time of the last toilet.
    if diff_time < 1:
        time_factor = 0.5
    elif diff_time < 3:
        time_factor = 1
    elif diff_time < 6:
        time_factor = 2
    elif diff_time > 8:
        time_factor = 5
    else:
        time_factor = 3
    return time_factor * toilet_prob


def adjust_phone_prob(phone_prob, phone_happened, time):
    # Adjust the probability based on the time now.
    if phone_happened == 1:
        phone_factor = 0
    elif 6 < time <= 12:
        phone_factor = 1
    elif 12 < time <= 14:
        phone_factor = 0.8
    elif 14 < time <= 16:
        phone_factor = 0.6
    elif 16 < time <= 18:
        phone_factor = 0.2
    else:
        phone_factor = 0
    return phone_factor * phone_prob


def adjust_step_out_prob(time):
    if 6 < time <= 12:
        step_out_prob = 1
    elif 12 < time <= 18:
        step_out_prob = 1 - (time - 12) / (18 - 12)
    else:
        step_out_prob = 0
    return step_out_prob
