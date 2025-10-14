import json
import utils
from module import agent, event

# map initialization
env_config_dir = r"config\env_config.json"
with open(env_config_dir, 'r', encoding='utf-8') as file:
    env_config = json.load(file)
map_matrix=utils.map_initialization(env_config)
utils.create_color_table(map_matrix)

# load user profile
user_profile_dir = r"config\user_profile.json"
with open(user_profile_dir, 'r', encoding='utf-8') as file:
    user_profile = json.load(file)

# load activity config
activity_config_dir = r"config\activity_config.json"
with open(activity_config_dir, 'r', encoding='utf-8') as file:
    activity_config = json.load(file)

user_choose="独居老人"
user_profile_choose=user_profile['用户配置'][user_choose]

iteration_day_num=30

# user initialization
user = agent.SmartAgent(user_profile_choose, activity_config)

# create event
event_system = event.Event(user, total_days=3)

# 运行整个工作流程
event_system.run_workflow()