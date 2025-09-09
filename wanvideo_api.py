import json
import os
import dashscope
from dashscope import VideoSynthesis
from http import HTTPStatus

class Wan2VideoAPI:
    def __init__(self, api_key):
        dashscope.api_key = api_key

    def chat_completion(self, messages, stream=True, model="wan2.2-t2v-plus", extra_body=None):
        if extra_body is None:
            extra_body = {}
        try:
            # 调用API
            response = VideoSynthesis.call(api_key=dashscope.api_key,
                          model=model,
                          prompt=messages,
                          size=extra_body.get("size", "1920*1080"),
                          duration=extra_body.get("duration", 10))

            # 处理响应
            if response.status_code == HTTPStatus.OK:
                return response
            else:
                print(f"API调用失败: {response.code}, {response.message}")
                return None
        except Exception as e:
            print(f"API调用失败: {e}")
            return None

if __name__ == "__main__":
    api = Wan2VideoAPI(api_key=os.environ.get("WAN_VIDEO_API_KEY"))
    messages = [{"role": "user", "content": "画一只猫"}]
    response = api.chat_completion(messages)
    if response is not None:
        print("模型回复:", response.output)
    else:
        print("模型调用失败")