# -*- coding: utf-8 -*-

import json
from openai import OpenAI
import os

class ModelScopeAPI:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api-inference.modelscope.cn/v1"
        )

    def chat_completion(self, messages, stream=True, model="qwen-plus", extra_body = {}):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,
                extra_body=extra_body
            )
            
            return response
        except Exception as e:
            print(f"通义千问API调用失败: {e}")
            return None

if __name__ == "__main__":
    # 测试API调用
    api = ModelScopeAPI(api_key=os.environ.get("MODELSCOPE_API_KEY"))
    messages = [{'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': '你好，介绍一下通义千问大模型'}]
    response = api.chat_completion(messages, model="qwen3-Thinking")
    if response is not None:
        print("模型回复:", response.choices[0].message.content)
    else:
        print("模型调用失败")
    