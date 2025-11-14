import os
import json
import utils

from src.module import agent, event

# map initialization
env_config_dir = "config/env_config.json"
with open(env_config_dir, 'r', encoding='utf-8') as file:
    env_config = json.load(file)
map_matrix = utils.map_initialization(env_config)
# utils.create_color_table(map_matrix)

# load user profile
user_profile_dir = r"config/user_profile.json"
with open(user_profile_dir, 'r', encoding='utf-8') as file:
    user_profile = json.load(file)

# load activity config
activity_config_dir = r"config/activity_config.json"
with open(activity_config_dir, 'r', encoding='utf-8') as file:
    activity_config = json.load(file)

user_choose = "RemoteWorker"
user_profile_choose = user_profile['user_config'][user_choose]
user_profile_choose['user_name'] = user_choose

prompt_path = r"prompt"
prompt_dict = utils.load_prompt_dict(prompt_path)

activity_str = utils.get_activity_str(activity_config)

iteration_day_num = 1

# user initialization
user = agent.SmartAgent(user_profile_choose, activity_str, prompt_dict)

# create event
event_system = event.Event(agent=user, activity_config=activity_config, env_config=env_config, map_matrix=map_matrix)

# run workflow
total_days = 14
event_system.run_workflow(total_days=total_days)
