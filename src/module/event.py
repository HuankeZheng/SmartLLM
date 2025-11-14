import json
import os.path
import random
from collections import deque
from src import utils
import pandas as pd


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
        self.record = []
        self.event_record = []
        self.position_now = None
        self.activity_now = None
        self.todo_schedule = deque([])
        self.done_schedule = deque([])
        self.current_day = 5
        self.phone_happened = 0
        self.random_num = random.randint(1, 100)

    def reset_state(self):
        self.todo_schedule = deque([])
        self.done_schedule = deque([])
        self.record = []
        self.event_record = []
        self.agent.weekday = utils.get_weekday(self.current_day)
        self.phone_happened = 0
        if self.position_now is None:
            bed = self.env_config["environment_config"]["Facility"]["BedroomBed"]
            self.position_now = bed['x'], bed['y']

    # 工作流模块
    def run_workflow(self, total_days):
        """workflow"""
        while self.current_day <= total_days:
            print(f"----- Day {self.current_day} -----")
            # 1.Reset State
            self.reset_state()
            # 2.Generate daily_schedule
            self.todo_schedule = deque(self.agent.generate_daily_schedule())
            # 3.execute activity step by step
            self.execute_schedule()
            # 4.save daily_record
            self.save_record(self.current_day - 1)
        print("所有日期execution结束")

    # execution module
    def execute_schedule(self):
        """
        Convert executable activities into executable event_sequence,
        execute events until the executable event_sequence is empty
        """
        print(f"今日安排: {self.todo_schedule}")
        while self.todo_schedule:
            # 1. If subsequent schedule is not empty, get the next activity
            activity_todo = self.todo_schedule.popleft()
            self.activity_now = activity_todo
            activity_name = activity_todo.get("activity_name")
            start_time = activity_todo.get("start_time")
            end_time = activity_todo.get("end_time")
            duration = (utils.str_time2int_time(end_time) - utils.str_time2int_time(start_time) + 24 * 60) % (24 * 60)

            if self.agent.time == "":
                self.agent.time = utils.str_time2int_time(start_time)
                self.agent.last_toilet_time = self.agent.time
            else:
                self.activity_now["start_time"] = utils.int_time2str_time(self.agent.time)

            # 2. Check if the next activity is valid
            current_activity = self.find_activity(activity_name)

            # 3. Convert the next activity into executable event_sequence and execute
            event_list = self.activity2event_list(current_activity, activity_name, duration)
            self.handle_event_list(event_list, activity_name)

            # 4. Trigger possible random activities after event_sequence ends
            self.trigger_random_activity()

            self.activity_now["end_time"] = utils.int_time2str_time(self.agent.time)
            self.done_schedule.append(self.activity_now)

            # 5. After current activity ends, determine whether to update schedule based on planned time and current time
            time_diff = utils.str_time2int_time(end_time) - self.agent.time
            if abs(time_diff) > 60 and len(self.todo_schedule) > 1:
                self.todo_schedule = deque(
                    self.agent.generate_follow_up_schedule(self.todo_schedule, self.done_schedule))

    def activity2event_list(self, activity, activity_name, duration=1):
        """Convert the activity into corresponding executable event_sequence and return it"""
        event_list = []
        duration_mapping = {
            "Movement": 1,
            "control": 1,
            "execution": duration
        }

        activity = activity["event_sequence"]
        if activity_name != 'Cooking':
            event_input_list = activity["normal"]
        else:
            rand = random.random()
            prob_params = self.agent.user_config["Parameter"]
            cook_prob = prob_params["Cooking"]["Probability"]
            prob1 = cook_prob["Heating"]
            prob2 = cook_prob["Stewing"]
            if rand < prob1:
                event_input_list = activity["Heating"]
            elif rand < (prob1 + prob2):
                event_input_list = activity["Stewing"]
            else:
                event_input_list = activity["Stir-frying"]

        for event_input in event_input_list:
            event_attribute = event_input.get("attribute")
            duration_attribute = event_input.get("Generate")
            if event_attribute in duration_mapping:
                if duration_attribute == "random":
                    event_input["duration"] = random.randint(3, 10)
                else:
                    event_input["duration"] = duration_mapping[event_attribute]
            event_input["activity_name"] = activity_name
            event_list.append(event_input)
        return event_list

    def handle_event_list(self, event_list, activity_name):
        """handle executable event_sequence"""
        event_list = deque(event_list)
        while event_list:
            event_todo = event_list.popleft().copy()
            event_state = event_todo.get("attribute")
            event_todo["activity_name"] = activity_name
            event_todo["start_time"] = utils.int_time2str_time(self.agent.time)
            self.event_record.append(event_todo)

            # execute different event
            if event_state.startswith("Movement"):
                self.execute_movement(event_todo)
            elif event_state.startswith("control"):
                self.execute_control(event_todo)
            elif event_state.startswith("execution"):
                self.handle_execution_event(event_todo)

    def execute_movement(self, event_todo):
        """
        Movement
        """
        position_from = self.position_now
        destination_to = event_todo["target"]
        if event_todo["state"] == "area":
            area_to = self.env_config["environment_config"]["valid_area"][destination_to]["Scope"]
            path = utils.move_to_area(position_from=position_from, area_to=area_to, map_matrix=self.map_matrix)
            activity_name = ''
            self.area_now = destination_to
        elif event_todo["state"] == "position":
            env_config = self.env_config["environment_config"]
            position_to = (env_config["Facility"].get(destination_to) or
                           env_config["control_device"].get(destination_to))
            position_to = position_to['x'], position_to['y']
            path = utils.move_to_position(position_from=position_from, position_to=position_to,
                                          map_matrix=self.map_matrix)
            activity_name = event_todo["activity_name"]
            self.pos_now = destination_to
        else:
            path = []
            activity_name = ''
        if path:
            for destination in path:
                for sensor_name, sensor in self.env_config["environment_config"]["sensor"].items():
                    destination_x = destination[0]
                    destination_y = destination[1]
                    sensor_x = sensor["x"]
                    sensor_y = sensor["y"]
                    if abs(destination_x - sensor_x) <= 1 and abs(destination_y - sensor_y) <= 1:
                        # print(f"触发{sensor_name}")
                        record_i = {
                            "Day": self.agent.weekday,
                            "Hour": utils.int_time2str_time(self.agent.time),
                            "sensor_type": sensor_name,
                            "sensor_state": 'ON',
                            "device_type": '',
                            'device_state': '',
                            'activity': activity_name
                        }
                        self.record.append(record_i)
            self.position_now = path[-1]
            self.update_time(event_todo["duration"])

    def execute_control(self, event_todo):
        """
        execute_control_event
        """
        device_type = event_todo["target"]
        device_state = event_todo["state"]
        record_i = {
            "Day": self.agent.weekday,
            "Hour": utils.int_time2str_time(self.agent.time),
            "sensor_type": '',
            "sensor_state": '',
            "device_type": device_type,
            'device_state': device_state,
            'activity': event_todo["activity_name"]
        }
        self.record.append(record_i)
        self.update_time(event_todo["duration"])

    def handle_execution_event(self, event_todo):
        """
        Handle event execution
        1. Random event handling logic
        2. If no random event is triggered and it's a wait-type execution event, enter the wait event handling logic
        """

        event_state = event_todo["state"]
        duration = event_todo["duration"]
        area_now = self.area_now
        pos_now = self.pos_now
        if event_state == "waiting" or event_state == 'doing':
            flag, random_activity = self.trigger_random_activity()
            if flag:
                split_duration = random.randint(0, duration)
                duration = duration - split_duration
                self.update_time(split_duration)
                self.handle_random_activity(random_activity)
            if not flag and event_state == "waiting":
                waiting_activity = self.agent.judge_waiting_event(self.todo_schedule, self.done_schedule,
                                                                  self.activity_now, event_todo)
                self.handle_waiting_activity(waiting_activity, event_todo["duration"])
                duration = duration - event_todo["duration"]
        self.execute_movement(
            {"state": "area", "target": area_now, "activity_name": event_todo["activity_name"], "duration": 1})
        self.execute_movement(
            {"state": "position", "target": pos_now, "activity_name": event_todo["activity_name"], "duration": 1})
        self.update_time(duration)
        self.execute_movement(
            {"state": "position", "target": pos_now, "activity_name": event_todo["activity_name"], "duration": 1})
        return

    def trigger_random_activity(self):
        """
        Trigger Random Activity
        1. Generate a random probability value to execute a random activity
        2. If execution occurs, return True; otherwise, return False
        """
        prob_params = self.agent.user_config["Parameter"]
        # Determine Phone Probability (based on Weekday/Weekend days)
        is_weekday = self.agent.weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        phone_prob = prob_params["Phone"]["Probability"]
        phone_prob = phone_prob["Weekday"] if is_weekday else phone_prob["Weekend"]
        phone_prob = utils.adjust_phone_prob(phone_prob, self.phone_happened, self.agent.time / 60)
        # Determine ToiletProbability (based on whether the current activity is Sleeping)
        toilet_prob = prob_params["Toilet"]["Probability"]
        toilet_prob = toilet_prob["Sleeping"] if self.activity_now["activity_name"] == "Sleeping" else toilet_prob["Daytime"]
        toilet_prob = utils.adjust_toilet_prob(toilet_prob, abs(self.agent.time - self.agent.last_toilet_time) / 60)
        # Randomly determine and execute activities
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
            return True, activity
        return False, ''

    def handle_random_activity(self, activity_type):
        """handle_random_activity"""
        if activity_type == "toilet_activity":
            self.handle_toilet_activity()
        elif activity_type == "phone_activity":
            self.handle_phone_activity()
        else:
            raise Exception(f"execution random activity error: {activity_type}")

    # Toilet活动
    def handle_toilet_activity(self):
        """handle_toilet_activity"""
        activity_name = "Toilet"
        current_activity = self.find_activity(activity_name)
        event_list = self.activity2event_list(current_activity, activity_name)
        self.handle_event_list(event_list, activity_name)
        self.agent.last_toilet_time = self.agent.time
        return

    # 电话活动
    def handle_phone_activity(self):
        """handle_phone_activity"""
        # 1.Record phone activities
        activity_name = "Phone"
        current_activity = self.find_activity(activity_name)
        event_list = self.activity2event_list(current_activity, activity_name)
        self.handle_event_list(event_list, activity_name)
        # 2.Whether to update the schedule based on the decision
        step_out_prob = utils.adjust_step_out_prob(self.agent.time / 60)
        rand = random.random()
        if rand <= step_out_prob:
            self.phone_happened = 1
            result = self.agent.judge_phone_event(self.todo_schedule, self.done_schedule)
            print("Update Schedule")
            self.todo_schedule = deque(result)
        return

    def handle_waiting_activity(self, waiting_activity_name, duration):
        """handle_waiting_activity"""
        activity_now = self.activity_now.copy()
        activity_now["end_time"] = utils.int_time2str_time(self.agent.time)
        self.done_schedule.append(activity_now)
        print(f"Waiting activity:{waiting_activity_name}")
        waiting_activity = {
            "activity_name": waiting_activity_name,
            "start_time": utils.int_time2str_time(self.agent.time)
        }
        current_activity = self.find_activity(waiting_activity_name)
        event_list = self.activity2event_list(current_activity, waiting_activity_name, duration)
        self.handle_event_list(event_list, waiting_activity_name)
        waiting_activity["end_time"] = utils.int_time2str_time(self.agent.time)
        self.done_schedule.append(waiting_activity)
        self.activity_now["start_time"] = utils.int_time2str_time(self.agent.time)
        return

    def find_activity(self, activity_name):
        current_activity = ''
        activity_list = self.activity_config.get("activity_config", [])
        for activity in activity_list:
            current_name = activity.get("activity_name")
            if current_name == activity_name:
                current_activity = activity
                break
        if current_activity == '':
            raise Exception(f"cant find activity {activity_name}")
        return current_activity

    def update_time(self, duration):
        old_time = self.agent.time
        self.agent.time = (self.agent.time + duration) % (24 * 60)
        if self.agent.time < old_time:
            self.current_day += 1
            self.agent.weekday = utils.get_weekday(self.current_day)

    def save_record(self, current_day):
        save_path = f"record/{self.agent.user_config['user_name']}/{self.random_num}/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        done_schedule = pd.DataFrame(list(self.done_schedule))
        done_schedule.to_csv(save_path + f"done_schedule_day{current_day}.csv", index=False,
                             encoding='utf-8-sig')
        record = pd.DataFrame(list(self.record))
        record.to_csv(save_path + f"record_day{current_day}.csv", index=False,
                      encoding='utf-8-sig')
        event_record = pd.DataFrame(list(self.event_record))
        event_record.to_csv(save_path + f"event_record_day{current_day}.csv", index=False,
                            encoding='utf-8-sig')
