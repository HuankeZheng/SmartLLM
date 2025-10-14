import requests
import json
import time
from typing import Optional, Dict, Any


class DeepSeekLLM:
    """
    DeepSeek大语言模型调用客户端
    """

    def __init__(self, api_key: str = "", base_url: str = "https://api.deepseek.com/v1/chat/completions"):
        """
        初始化DeepSeek客户端

        :param api_key: DeepSeek API密钥
        :param base_url: API基础地址，默认为官方地址
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def generate(self,
                 prompt: str,
                 model: str = "deepseek-chat",
                 temperature: float = 0.7,
                 max_tokens: int = 1024,
                 top_p: float = 0.95,
                 stream: bool = False,
                 timeout: int = 60) -> Dict[str, Any]:
        """
        调用DeepSeek模型生成结果

        :param prompt: 输入的提示文本
        :param model: 模型名称，默认为"deepseek-chat"
        :param temperature: 温度参数，控制生成的随机性
        :param max_tokens: 最大生成token数
        :param top_p: 核采样参数
        :param stream: 是否流式返回
        :param timeout: 请求超时时间(秒)
        :return: 模型返回的结果字典
        """
        # 构建请求数据
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream
        }

        try:
            # 发送请求
            response = requests.post(
                url=self.base_url,
                headers=self.headers,
                data=json.dumps(data),
                timeout=timeout
            )

            # 检查响应状态
            response.raise_for_status()

            # 返回解析后的结果
            return response.json()

        except requests.exceptions.RequestException as e:
            # 处理请求异常
            print(f"请求发生错误: {str(e)}")
            return {"error": str(e)}
        except json.JSONDecodeError:
            # 处理JSON解析错误
            print("无法解析响应内容为JSON")
            return {"error": "Invalid JSON response", "content": response.text}