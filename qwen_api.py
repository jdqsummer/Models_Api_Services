import json
import os
from openai import OpenAI

class QwenAPI:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )

    def chat_completion(self, messages, stream=True, model="qwen-turbo",extra_body = {}):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,
                extra_body=extra_body,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_current_weather",
                            "description": "获取当前天气",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {
                                        "type": "string",
                                        "description": "城市名称"
                                    },
                                    "unit": {
                                        "type": "string",
                                        "enum": ["摄氏度", "华氏度"]
                                    }
                                },
                                "required": ["location"]
                            }
                        }
                    }
                ],
                tool_choice="auto",
                parallel_tool_calls=True
            )
            
            return response
        except Exception as e:
            error_msg = f"通义千问API调用失败: {e}"
            print(error_msg)
            return error_msg

if __name__ == "__main__":
    # 测试API调用
    api = QwenAPI(api_key=os.environ.get("QWEN_API_KEY"))
    messages = [{'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': '你好，介绍一下通义千问大模型'}]
    response = api.chat_completion(messages, model="qwen-turbo")
    if response is not None:
        print("模型回复:", response.choices[0].message.content)
    else:
        print("模型调用失败")
