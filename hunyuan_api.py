from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.hunyuan.v20230901 import hunyuan_client, models
import json
import os

class HunyuanAPI:
    def __init__(self, secret_id, secret_key):
        self.cred = credential.Credential(secret_id, secret_key)
        self.client = hunyuan_client.HunyuanClient(self.cred, "ap-guangzhou")

    def chat_completion(self, messages, stream=False, model=""):
        try:
            req = models.ChatCompletionsRequest()
            params = {
                "Model": model,
                "Messages": messages,
                "Temperature": 0.5,
                "TopP": 0.8,
                "Stream": stream,
                "StreamModeration": True,
                "EnableEnhancement": True,
                "SearchInfo": True,
                "Citation": True,
                "ForceSearchEnhancement": True,
                "EnableDeepSearch": False,
                "EnableDeepRead": False,
                "EnableThinking": True,
                "EnableRecommendedQuestions": True
            }
            req.from_json_string(json.dumps(params))
            if stream:
                response = self.client.ChatCompletions(req)
                for event in response:
                    try:
                        # 提取data字段内容
                        data_content = json.loads(event.get('data', '{}'))
                        # 提取所需字段
                        result_data = {
                            'answer': data_content.get('Choices', [{}]),
                            'SearchInfo': data_content.get('SearchInfo', {}),
                            'RecommendedQuestions': data_content.get('RecommendedQuestions', [])
                        }
                        # 返回处理后的数据
                        yield json.dumps(result_data)
                    except Exception as e:
                        # 保留原始事件格式
                        yield event
            else:
                resp = self.client.ChatCompletions(req)
                print(f"api响应: {resp.to_json_string()}")
                result = json.loads(resp.to_json_string())
                return result

        except TencentCloudSDKException as err:
            error_msg = f"调用混元API失败: {str(err)}"
            print(f"API调用错误: {err}")
            if stream:
                yield json.dumps({"error": error_msg})
            return error_msg
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            print(f"未知错误: {e}")
            if stream:
                yield json.dumps({"error": error_msg})
            return error_msg

if __name__ == "__main__":
    # 测试API调用
    api = HunyuanAPI(
        secret_id=os.environ.get("HUNYUAN_SECRET_ID"),
        secret_key=os.environ.get("HUNYUAN_SECRET_KEY")
    )
    response = api.chat_completion("你好，介绍一下腾讯混元大模型")
    print("模型回复:", response)