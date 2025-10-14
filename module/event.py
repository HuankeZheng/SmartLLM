import json
import random
from collections import deque


class Event:
    def __init__(self, agent, record, activity_config):
        self.agent = agent
        self.record = record
        self.activity_config = activity_config
        self.params = {'toilet_prob': agent.tolie_prob, 'phone_prob': agent.phone_prob}
        self.done_schedule = deque([])
        self.todo_schedule = deque([])
        self.event_sequence = deque([])

    # 随机事件模块
    def trigger_random_event(self):
        """触发随机事件：厕所事件或电话事件"""
        rand = random.random()
        if rand < self.params['toilet_prob']:
            return "toilet_event"
        elif rand < self.params['toilet_prob'] + self.params['phone_prob']:
            return "phone_event"
        return None

    # waiting事件判断模块
    def handle_waiting_event(self, waiting_event):
        """处理waiting状态事件"""
        # 先检查随机事件
        random_event = self.trigger_random_event()
        if random_event:
            self.handle_random_event(random_event)
        # 调用agent的waiting事件判断
        return self.agent.judge_waiting_event(waiting_event)

    def update_schedule(self, schedule):
        self.daily_schedule = json.loads(schedule)

    # 工作流模块
    def run_workflow(self, total_days):
        """执行整体工作流"""
        current_day = 1
        while current_day <= total_days:
            print(f"----- 第 {current_day} 天 -----")
            # 生成今日安排
            schedule = self.agent.generate_daily_schedule()
            # 处理今日安排
            self.update_schedule(schedule=schedule)
            # 执行今日安排
            self.execute_schedule()
            # 更新安排
            self.agent.generate_follow_up_schedule()
            current_day += 1
        print("所有日期执行结束")

    # 执行模块
    def execute_schedule(self):
        """执行活动安排"""
        print(f"执行安排: {self.daily_schedule}")
        while self.daily_schedule:
            activity_todo = self.daily_schedule.popleft().get("activity_name")
            activity_list = self.activity_config.get("活动配置", [])
            current_activity = ''
            for activity in activity_list:
                current_name = activity.get("活动名称")
                if current_name == activity_todo:
                    current_activity = activity
                    break
            if current_activity == '':
                raise Exception(f"未找到活动 {activity_todo}")

            self.add_activity(activity_todo)

            while self.event_sequence:
                event_todo = self.event_sequence.popleft()
                event_state = event_todo.get("属性")
                print(f"执行: {event_todo}")

                # 处理不同类型的事件
                if event_state.startswith("移动"):
                    self.execute_movement(event_todo)
                elif event_state.startswith("控制"):
                    self.execute_control(event_todo)
                elif event_state.startswith("等待"):
                    self.handle_waiting_event(event_todo)

            # 事件序列结束后触发可能的随机事件
            self.trigger_after_activity()
            # 更新后续安排
            self.agent.generate_follow_up_schedule()

    def add_activity(self, activity, duration=30):
        event_sequence = activity["事件序列"]["正常"]
        self.event_sequence = self.event_sequence + event_sequence

    def execute_movement(self, activity):
        """执行移动事件"""
        print(f"进行移动: {activity}")

    def execute_control(self, activity):
        """执行控制事件"""
        print(f"产生控制: {activity}")

    def trigger_after_activity(self):
        """活动结束后触发随机事件检查"""
        event = self.trigger_random_event()
        if event:
            self.handle_random_event(event)

    def handle_random_event(self, event_type):
        """处理随机事件"""
        if event_type == "toilet_event":
            self.handle_toilet_activity()
        elif event_type == "phone_event":
            self.handle_phone_activity()

    # 厕所活动
    def handle_toilet_activity(self):
        """处理厕所活动"""
        print("执行厕所活动")
        self.agent.activity_list.append("厕所活动")

    # 电话活动
    def handle_phone_activity(self):
        """处理电话活动"""
        print("处理电话活动")
        result = self.agent.judge_phone_event()
        print(result)
