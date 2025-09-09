import json
import requests

from openai import OpenAI

class ModelScopeImageAPI:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def chat_completion(self, messages, stream=True, model="wan2.2-plus", extra_body=None):
        if extra_body is None:
            extra_body = {}
        try:
            # 调用API
            common_headers = {**self.headers, "X-ModelScope-Async-Mode": "true"}
            response = requests.post(
                f"{self.url}v1/images/generations",
                headers=common_headers,
                data=json.dumps({
                    "model": model,  # ModelScope Model-Id, required
                    "prompt": messages,
                    "size":  extra_body.get("size", "1024x1024"),
                    "n": extra_body.get("n", 4),
                }, ensure_ascii=False).encode('utf-8')
            )
            
            # 处理响应
            if response.status_code == 200:
                return response
            else:
                print(f"API调用失败: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            print(f"API调用失败: {e}")
            return None

if __name__ == "__main__":
    api = ModelScopeImageAPI(url="https://api-inference.modelscope.cn/v1/images/generations",
                             headers={
                                 "Authorization": "Bearer sk-1234567890abcdef1234567890abcdef",
                                 "Content-Type": "application/json",
                             })
    messages = [{"role": "user", "content": "画一只猫"}]
    response = api.chat_completion(messages)
    if response is not None:
        print("模型回复:", response.json())
    else:
        print("模型调用失败")