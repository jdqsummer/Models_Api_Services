import json
import os
import dashscope
from dashscope import ImageSynthesis
from http import HTTPStatus

class Wan2API:
    def __init__(self, api_key):
        dashscope.api_key = api_key

    def chat_completion(self, messages, stream=True, model="wan2.2-plus", extra_body=None):
        if extra_body is None:
            extra_body = {}
        try:
            # 调用API
            response = ImageSynthesis.call(api_key=dashscope.api_key,
                          model=model,
                          prompt=messages,
                          n=extra_body.get("n", 4),
                          size=extra_body.get("size", "1024*1024"))

            # 处理响应
            if response.status_code == HTTPStatus.OK:
                return response
            else:
                print(f"API调用失败: {response.code}, {response.message}")
                return response
        except Exception as e:
            print(f"API调用失败: {e}")
            error_msg = f"未知错误: {str(e)}"
            return error_msg  

if __name__ == "__main__":
    api = Wan2API(api_key=os.environ.get("WAN_API_KEY"))
    messages = [{"role": "user", "content": "画一只猫"}]
    response = api.chat_completion(messages)
    if response is not None:
        print("模型回复:", response.output)
    else:
        print("模型调用失败")