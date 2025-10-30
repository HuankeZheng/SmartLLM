import json

from src import chat


class SmartAgent:
    def __init__(self, user_config, activity_list, prompt_dict):
        self.user_config = user_config
        self.activity_list = activity_list
        self.user_profile = user_config['简介']
        self.user_lifestyle = ''
        self.prompt_dict = prompt_dict
        self.weekday = ""
        self.time = ""
        for i, lifestyle_i in enumerate(user_config['特性']):
            self.user_lifestyle += f'{i + 1}.{lifestyle_i};'

    def generate_daily_schedule(self):
        """
        日计划初始化
        1.读取内容，合成prompt
        2.输入prompt，得到输出结果，并返回
        """
        prompt_format = self.prompt_dict["generate_new_day_plan"]
        plan_reference = json.loads(self.prompt_dict["daily_plan_reference.json"])[self.user_config["用户名称"]]

        DAY_CATEGORY = {
            "星期一": "工作日", "星期二": "工作日", "星期三": "工作日",
            "星期四": "工作日", "星期五": "工作日",
            "星期六": "周末", "星期日": "周末"
        }
        category = DAY_CATEGORY.get(self.weekday)
        if category and plan_reference.get(category):
            plan_reference = plan_reference[category]
        else:
            plan_reference = plan_reference["default"]

        variables = {
            "user_profile": self.user_profile,
            "user_lifestyle": self.user_lifestyle,
            "weekday": self.weekday,
            "schedule_sample": plan_reference,
            "activity_list": self.activity_list
        }
        prompt = prompt_format.format(**variables)

        # 实际应用中这里会调用LLM生成安排
        schedule = chat.get_response(content=prompt)
        schedule = json.loads(schedule)
        return schedule

    def generate_follow_up_schedule(self, todo_schedule, done_schedule):
        # 更新日计划
        # 1.读取内容，合成prompt
        prompt_format = self.prompt_dict["update_day_plan"]
        variables = {
            "user_profile": self.user_profile,
            "user_lifestyle": self.user_lifestyle,
            "todo_schedule": todo_schedule,
            "past_schedule": done_schedule,
            "weekday": self.weekday,
            "activity_list": self.activity_list
        }
        prompt = prompt_format.format(**variables)
        # 2.输入prompt，得到输出结果，并返回
        # 实际应用中这里会调用LLM生成安排
        schedule = chat.get_response(content=prompt)
        schedule = json.loads(schedule)
        return schedule

    def judge_waiting_event(self, todo_schedule, done_schedule, current_activity, current_waiting_event):
        """判断waiting事件处理方式"""
        # 1.读取内容，合成prompt
        prompt_format = self.prompt_dict["decide_do_what_waiting"]
        variables = {
            "user_profile": self.user_profile,
            "user_lifestyle": self.user_lifestyle,
            "todo_schedule": todo_schedule,
            "past_schedule": done_schedule,
            "activity": current_activity["activity_name"],
            "event_name": current_waiting_event["目标"],
            "event_time": current_waiting_event["duration"],
            "weekday": self.weekday,
            "activity_list": self.activity_list
        }
        prompt = prompt_format.format(**variables)
        # 2.输入prompt，得到输出结果，并返回
        # 实际应用中这里会调用LLM生成安排
        choose_activity = chat.get_response(content=prompt)
        print(f"在等待过程中进行活动: {choose_activity}")
        return choose_activity

    def judge_phone_event(self, todo_schedule, done_schedule):
        """判断phone事件处理方式"""
        # 1.读取内容，合成prompt
        prompt_format = self.prompt_dict["decide_whether_step_out"]
        variables = {
            "user_profile": self.user_profile,
            "user_lifestyle": self.user_lifestyle,
            "todo_schedule": todo_schedule,
            "past_schedule": done_schedule,
            "weekday": self.weekday,
            "activity_list": self.activity_list
        }
        prompt = prompt_format.format(**variables)
        # 2.输入prompt，得到输出结果，并返回
        # 实际应用中这里会调用LLM生成安排
        phone_decision = chat.get_response(content=prompt)
        if "否" in phone_decision:
            print("不进行计划修改")
            return None
        else:
            print(f"原计划: {todo_schedule}")
            print(f"修改后计划为: {phone_decision}")
            phone_decision = json.loads(phone_decision)
            return phone_decision
