from src import chat


class SmartAgent:
    def __init__(self, user_config, activity_list, prompt_dict):
        self.user_config = user_config
        self.activity_list = activity_list
        self.current_schedule = None
        self.past_schedule = None
        self.past_activities = []
        self.user_profile = user_config['简介']
        self.user_lifestyle = ''
        self.prompt_dict = prompt_dict
        self.weekday = ""
        for i, lifestyle_i in enumerate(user_config['特性']):
            self.user_lifestyle += f'{i + 1}.{lifestyle_i};'

    def generate_daily_schedule(self):
        """
        日计划初始化
        1.读取内容，合成prompt
        2.输入prompt，得到输出结果，并返回
        """
        prompt_format = self.prompt_dict["generate_new_day_plan"]
        variables = {
            "user_profile": self.user_profile,
            "lifestyle": self.user_lifestyle,
            "weekday": self.weekday,
            "schedule_sample": self.prompt_dict["daily_plan_reference.json"][self.user_config["用户名称"]],
            "activity_list": self.activity_list
        }
        prompt = prompt_format.format(**variables)

        # 实际应用中这里会调用LLM生成安排
        self.current_schedule = chat.get_response(content=prompt)
        return self.current_schedule

    def generate_follow_up_schedule(self):
        # 更新日计划
        # 1.读取内容，合成prompt
        prompt_format = self.prompt_dict["update_day_plan"]
        variables = {
            "user_profile": self.user_profile,
            "lifestyle": self.user_lifestyle,
            "schedule": self.current_schedule,
            "past_schedule": self.past_schedule,
            "weekday": self.weekday,
            "activity_list": self.activity_list
        }
        prompt = prompt_format.format(**variables)
        # 2.输入prompt，得到输出结果，并返回
        # 实际应用中这里会调用LLM生成安排
        self.current_schedule = chat.get_response(content=prompt)
        return self.current_schedule

    def judge_waiting_event(self, current_activity, current_waiting_event):
        """判断waiting事件处理方式"""
        # 1.读取内容，合成prompt
        prompt_format = self.prompt_dict["decide_do_what_waiting"]
        variables = {
            "user_profile": self.user_profile,
            "lifestyle": self.user_lifestyle,
            "schedule": self.current_schedule,
            "past_schedule": self.past_schedule,
            "activity": current_activity,
            "event_name": current_waiting_event["event_name"],
            "event_time": current_waiting_event["event_time"],
            "weekday": self.weekday,
            "activity_list": self.activity_list
        }
        prompt = prompt_format.format(**variables)
        # 2.输入prompt，得到输出结果，并返回
        # 实际应用中这里会调用LLM生成安排
        choose_activity = chat.get_response(content=prompt)
        return f"在等待过程中进行活动: {choose_activity}"

    def judge_phone_event(self):
        """判断phone事件处理方式"""
        # 1.读取内容，合成prompt
        prompt_format = self.prompt_dict["decide_do_what_waiting"]
        variables = {
            "user_profile": self.user_profile,
            "lifestyle": self.user_lifestyle,
            "schedule": self.current_schedule,
            "past_schedule": self.past_schedule,
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
            print(f"原计划: {self.past_schedule}")
            print(f"修改后计划为: {phone_decision}")
            return phone_decision
