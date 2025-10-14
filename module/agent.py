import chat


class SmartAgent:
    def __init__(self, user_config, activity_list):
        self.user_config = user_config
        self.activity_list = activity_list
        self.current_schedule = None
        self.past_activities = []
        self.LLM = chat.DeepSeekLLM()
        self.user_profile = user_config['简介']
        self.user_lifestyle = ''
        for i, lifestyle_i in enumerate(user_config['特性']):
            self.user_lifestyle += f'{i + 1}.{lifestyle_i};'

    def generate_daily_schedule(self):
        """生成今日的安排"""
        prompt = f"基于用户配置: {self.user_config} 和活动列表: {self.activity_list}，参考样例: {self.daily_example}，生成今日的活动安排"
        # 实际应用中这里会调用LLM生成安排
        self.current_schedule = self.LLM.generate(prompt=prompt)
        return self.current_schedule

    def generate_follow_up_schedule(self):
        """生成今日的后续安排"""
        prompt = f"基于用户配置: {self.user_config}, 活动列表: {self.activity_list}, 已完成活动: {self.past_activities}, 当前安排: {self.current_schedule}，判断是否需要重新安排"
        # 实际应用中这里会调用LLM生成后续安排
        updated_schedule = f"更新后的安排 (基于提示: {prompt})"
        self.current_schedule = updated_schedule
        return self.current_schedule

    def judge_waiting_event(self, current_waiting_event):
        """判断waiting事件处理方式"""
        # 简单逻辑示例，实际应根据具体情况判断
        return f"判断结果: 继续当前waiting事件 '{current_waiting_event}'"

    def judge_phone_event(self):
        """判断phone事件处理方式"""
        # 简单逻辑示例，实际应根据具体情况判断
        return "判断结果: 调整今日安排，增加外出活动"
