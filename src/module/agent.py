import json

from src import chat


class SmartAgent:
    def __init__(self, user_config, activity_list, prompt_dict):
        self.user_config = user_config
        self.activity_list = activity_list
        self.user_profile = user_config['Introduction']
        self.user_lifestyle = ''
        self.prompt_dict = prompt_dict
        self.weekday = ""
        self.time = ""
        for i, lifestyle_i in enumerate(user_config['Characteristics']):
            self.user_lifestyle += f'{i + 1}.{lifestyle_i};'

    def generate_daily_schedule(self):
        prompt_format = self.prompt_dict["generate_new_day_plan"]
        plan_reference = json.loads(self.prompt_dict["daily_plan_reference.json"])[self.user_config["user_name"]]

        DAY_CATEGORY = {
            "Monday": "Weekday", "Tuesday": "Weekday", "Wednesday": "Weekday",
            "Thursday": "Weekday", "Friday": "Weekday",
            "Saturday": "Weekend", "Sunday": "Weekend"
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

        schedule = chat.get_response(content=prompt)
        try:
            schedule = schedule.replace("'", '"')
            schedule = json.loads(schedule)
        except json.JSONDecodeError as e:
            print(f"JSON Error: {e}")
            print(f"Original Schedule: {schedule}")
        except Exception as e:
            print(f"Other Error: {e}")
            print(f"Original Schedule: {schedule}")
        return schedule

    def generate_follow_up_schedule(self, todo_schedule, done_schedule):
        # update schedule
        # 1.generate prompt
        prompt_format = self.prompt_dict["update_day_plan"]
        variables = {
            "user_profile": self.user_profile,
            "user_lifestyle": self.user_lifestyle,
            "todo_schedule": list(todo_schedule),
            "past_schedule": list(done_schedule),
            "weekday": self.weekday,
            "activity_list": self.activity_list
        }
        prompt = prompt_format.format(**variables)
        # 2.generate schedule
        schedule = chat.get_response(content=prompt)
        try:
            print(f"Original Schedule: {todo_schedule}")
            print(f"New Schedule: {schedule}")
            schedule = schedule.replace("'", '"')
            schedule = json.loads(schedule)
        except json.JSONDecodeError as e:
            print(f"JSON Error: {e}")
            print(f"Original Schedule: {schedule}")
        except Exception as e:
            print(f"Other Error: {e}")
            print(f"Original Schedule: {schedule}")
        return schedule

    def judge_waiting_event(self, todo_schedule, done_schedule, current_activity, current_waiting_event):
        # waiting decision
        # 1.generate prompt
        prompt_format = self.prompt_dict["decide_do_what_waiting"]
        variables = {
            "user_profile": self.user_profile,
            "user_lifestyle": self.user_lifestyle,
            "todo_schedule": list(todo_schedule),
            "past_schedule": list(done_schedule),
            "activity": current_activity["activity_name"],
            "event_name": current_waiting_event["target"],
            "event_time": current_waiting_event["duration"],
            "weekday": self.weekday,
            "activity_list": self.activity_list
        }
        prompt = prompt_format.format(**variables)
        # 2.generate decision
        choose_activity = chat.get_response(content=prompt)
        print(f"Waiting activity: {choose_activity}")
        return choose_activity

    def judge_phone_event(self, todo_schedule, done_schedule):
        # phone decision
        # 1.generate prompt
        prompt_format = self.prompt_dict["decide_whether_step_out"]
        variables = {
            "user_profile": self.user_profile,
            "user_lifestyle": self.user_lifestyle,
            "todo_schedule": list(todo_schedule),
            "past_schedule": list(done_schedule),
            "weekday": self.weekday,
            "activity_list": self.activity_list + ',Going Out'
        }
        prompt = prompt_format.format(**variables)
        # 2.generate decision
        phone_decision = chat.get_response(content=prompt)
        print(f"Original Schedule: {todo_schedule}")
        print(f"New Schedule: {phone_decision}")
        phone_decision = phone_decision.replace("'", '"')
        phone_decision = json.loads(phone_decision)
        return phone_decision
