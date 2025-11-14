# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", "sk-306fd70669ab4d1faa526a050ca99564"),
    base_url="https://api.deepseek.com")


def get_response(content):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": content},
        ],
        stream=False
    )
    return response.choices[0].message.content
