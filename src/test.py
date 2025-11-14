import pandas as pd

activity_config=pd.read_json("config/activity_config.json")
activity_config=activity_config["activity_config"]
activity_name =[item['activity_name'] for item in activity_config]
print(set(activity_name))

DAY_CATEGORY = {
    "Monday": "Weekday", "Tuesday": "Weekday", "Wednesday": "Weekday",
    "Thursday": "Weekday", "Friday": "Weekday",
    "Saturday": "Weekend", "Sunday": "Weekend"
}
output=[]
for key,value in DAY_CATEGORY.items():
    if value =="Weekday":
        output.append(key)
print(output)