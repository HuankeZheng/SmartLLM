import json
import random
from collections import deque
from src import utils


class Event:
    def __init__(self, agent, activity_config, env_config, map_matrix):
        """
        agent: user
        activity_config: details of activities
        param: the happen prob of toilet activity and phone activity
        record: the structure data of smart home
        done_schedule: the plan has done
        todo_schedule: the plan todo
        event_sequence: the sequence todo
        current_activity: the activity being done
        current_event: the event being done
        """
        self.agent = agent
        self.activity_config = activity_config
        self.env_config = env_config
        self.map_matrix = map_matrix
        self.params = {'toilet_prob': agent.toilet_prob, 'phone_prob': agent.phone_prob}
        self.record = []
        self.current_activity = ''
        self.current_event = ''
        self.destination_now = ''
        self.activity_now = ''

    # 工作流模块
    def run_workflow(self, total_days):
        """执行整体工作流"""
        current_day = 1
        while current_day <= total_days:
            print(f"----- 第 {current_day} 天 -----")
            # 1.生成今日安排
            self.agent.weekday = utils.get_weekday(current_day)
            self.todo_schedule = self.agent.generate_daily_schedule()
            # 2.逐个执行活动，将每个活动转化为可执行事件序列，再执行
            self.execute_schedule()
            current_day += 1
        print("所有日期执行结束")

    # 执行模块
    def execute_schedule(self):
        """
        1.执行可执行活动直到可执行活动序列为空
        2.将可执行活动转化为可执行事件序列，执行可执行事件直到可执行事件序列为空
        """
        print(f"今日安排: {self.todo_schedule}")
        while self.todo_schedule:
            # 1.后续安排不为空，则获得最新活动
            activity_todo = self.todo_schedule.popleft()
            activity_name = activity_todo.get("activity_name")
            start_time = activity_todo.get("start_time")
            end_time = activity_todo.get("end_time")
            duration = end_time - start_time

            # 2.判断最新活动是否有效
            activity_list = self.activity_config.get("活动配置", [])
            current_activity = ''
            for activity in activity_list:
                current_name = activity.get("活动名称")
                if current_name == activity_name:
                    current_activity = activity
                    break
            if current_activity == '':
                raise Exception(f"未找到活动 {activity_name}")

            # 3.将最新活动转化为可执行事件序列，并执行
            event_list = self.activity2event_list(activity_name, duration)
            self.event_sequence = self.event_sequence + event_list
            self.handle_event_list(event_list)

            # 4.事件序列结束后触发可能的随机活动
            self.trigger_random_activity()

            # 5.当前活动结束后，判断是否更新日程安排
            self.agent.generate_follow_up_schedule()

    def activity2event_list(self, activity, duration=30):
        """将活动转化为对应的可执行事件序列，并返回"""
        event_list = []
        # 定义事件属性与持续时间的映射关系，便于后续维护
        duration_mapping = {
            "移动": 1,
            "控制": 0,
            "执行": duration
        }

        event_input_list = activity["事件序列"]["正常"]
        for event_input in event_input_list:
            event_attribute = event_input.get("属性")
            # 仅处理已知属性的事件，未知属性不修改duration
            if event_attribute in duration_mapping:
                event_input["duration"] = duration_mapping[event_attribute]
            event_list.append(event_input)
        return event_list

    def handle_event_list(self, event_list):
        """执行可执行事件序列"""
        event_list = deque(event_list)
        while event_list:
            event_todo = event_list.popleft()
            event_state = event_todo.get("属性")
            print(f"执行: {event_todo}")

            # 处理不同类型的事件
            if event_state.startswith("移动"):
                self.execute_movement(event_todo)
            elif event_state.startswith("控制"):
                self.execute_control(event_todo)
            elif event_state.startswith("执行"):
                self.handle_execution_event(event_todo)

    def execute_movement(self, event_todo):
        """
        执行移动事件
        """
        destination_from = self.destination_now
        destination_to = event_todo["目标"]
        path = utils.calculate_path(destination_from, destination_to, map_matrix=self.map_matrix)
        for destination in path:
            for sensor_name, sensor in self.env_config["环境配置"]["传感器"].items():
                destination_x = destination["x"]
                destination_y = destination["y"]
                sensor_x = sensor["x"]
                sensor_y = sensor["y"]
                if abs(destination_x - sensor_x) <= 1 and abs(destination_y - sensor_y) <= 1:
                    print(f"触发{sensor_name}")
                    record_i = {
                        "星期": self.agent.weekday,
                        "时间": utils.int_time2str_time(self.agent.time),
                        "sensor_type": sensor_name,
                        "sensor_state": 'ON',
                        "device_type": '',
                        'device_state': '',
                        'activity': self.activity_now
                    }
                    self.record.append(record_i)
        self.destination_now = destination_to
        self.agent.time += event_todo["duration"]
        print(f"移动事件: {event_todo}")

    def execute_control(self, event_todo):
        """
        执行控制事件
        """
        device_type = event_todo["目标"]
        device_state = event_todo["状态"]
        record_i = {
            "星期": self.agent.weekday,
            "时间": utils.int_time2str_time(self.agent.time),
            "sensor_type": '',
            "sensor_state": '',
            "device_type": device_type,
            'device_state': device_state,
            'activity': self.activity_now
        }
        self.record.append(record_i)
        self.agent.time += event_todo["duration"]
        print(f"控制事件: {event_todo}")

    def handle_execution_event(self, event_todo):
        """
        处理执行事件
        1.随机事件处理逻辑
        2.若没有触发随机事件且为等待型执行事件，则进入等待事件处理逻辑
        """
        flag = self.trigger_random_activity()
        event_state = event_todo["状态"]
        if not flag and event_state == "waiting":
            self.agent.judge_waiting_event(event_todo)
        return

    def trigger_random_activity(self):
        """
        触发随机活动
        1.生成随机概率，执行随机活动
        2.若执行，返回True，否则，返回False
        """
        # 获取基础概率参数（统一参数路径，减少重复访问）
        prob_params = self.params["参数"]["电话"]["概率"]
        # 确定电话概率（根据工作日/休息日区分）
        is_weekday = self.agent.weekday in ["星期一", "星期二", "星期三", "星期四", "星期五"]
        phone_prob = prob_params["工作日"] if is_weekday else prob_params["休息日"]
        # 确定厕所概率（根据当前活动是否为睡觉区分）
        toilet_prob = prob_params["睡眠"] if self.activity_now == "睡觉" else prob_params["白天"]
        # 随机判断并执行活动
        rand = random.random()
        total_toilet = toilet_prob
        total_phone = total_toilet + phone_prob
        if rand < total_toilet:
            activity = "toilet_activity"
        elif rand < total_phone:
            activity = "phone_activity"
        else:
            activity = None
        if activity:
            self.handle_random_activity(activity)
            return True
        return False

    def handle_random_activity(self, activity_type):
        """处理随机活动"""
        if activity_type == "toilet_activity":
            self.handle_toilet_activity()
        elif activity_type == "phone_activity":
            self.handle_phone_activity()
        else:
            raise Exception(f"执行随机活动错误: {activity_type}")

    # 厕所活动
    def handle_toilet_activity(self):
        """处理厕所活动"""
        print("执行厕所活动")
        event_list = self.activity2event_list("厕所活动")
        self.handle_event_list(event_list)
        return

    # 电话活动
    def handle_phone_activity(self):
        """处理电话活动"""
        print("执行phone活动")
        # 1.增加phone活动的记录
        event_list = self.activity2event_list("phone活动")
        self.handle_event_list(event_list)
        # 2.根据决策是否更新日程安排
        result = self.agent.judge_phone_event()
        if result:
            print("更新安排")
            self.todo_schedule = result
        return
