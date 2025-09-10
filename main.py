# -*- coding: utf-8 -*-
import dashscope
import requests
import time
from io import BytesIO
import json
import os

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from dashscope import ImageSynthesis
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from hunyuan_api import HunyuanAPI
from tencentcloud.common.exception import TencentCloudSDKException
from modelscopeimage_api import ModelScopeImageAPI
from wanvideo_api import Wan2VideoAPI
from modelscope_api import ModelScopeAPI

from qwen_api import QwenAPI
from wan_api import Wan2API
from openai import OpenAI

from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath


app = Flask(__name__)
# 配置CORS以允许所有来源和必要请求头
CORS(app, resources={r"/*": {
    "origins": "*",
    "allow_headers": ["Content-Type", "Authorization"],
    "methods": ["GET", "POST", "OPTIONS"]
}})



# 构建符合API规范的消息序列
def _build_api_messages(messages, name):
    """构建符合API规范的消息序列"""

    # 验证消息数组格式
    #if not isinstance(messages, list):
    #    raise ValueError("messages必须是列表格式")
    
    # 过滤掉无效消息并确保角色交替出现
    filtered_messages = []
    last_role = None
    count = 0
    for msg in messages:
        # 跳过系统消息
        if count == 0:
            count += 1
            continue
        count += 1

        if isinstance(msg, dict) and "Role" in msg and "Content" in msg:
            role = msg["Role"]
            content = msg["Content"]
            # 确保Content是字符串类型
            if not isinstance(content, str):
                content = str(content) if content is not None else ""
            # 检查角色是否交替出现
            if role in ["user", "assistant"] and role != last_role:
                # 判断name是否包含hunyuan字符串，使用大写的Role和 Content
                if "Hunyuan" in name:
                    filtered_messages.append({"Role": role, "Content": content})
                else:
                    filtered_messages.append({"role": role, "content": content})
                last_role = role
    
    # 确保消息序列以user角色结束，腾讯元宝使用大小字母，其他模型使用小写
    if "Hunyuan" in name:
        api_messages = [{"Role": "system", "Content": "请对问题进行深度研究和详细分析，提供全面的回答"}]
        if filtered_messages and filtered_messages[-1]["Role"] != "user":
            raise ValueError("消息序列必须以user角色结束")
    else:
        api_messages = [{"role": "system", "content": "请对问题进行深度研究和详细分析，提供全面的回答"}]
        if filtered_messages and filtered_messages[-1]["role"] != "user":
            raise ValueError("消息序列必须以user角色结束")
    
    api_messages.extend(filtered_messages)
    return api_messages

# 解析混元API响应函数
def parse_hunyuan_response(response):
    """解析混元API响应函数"""
    # 定义生成器函数
    def generate():
        for chunk in response:
            # 打印原始chunk
            try:
                # 处理chunk可能是字符串或字典的情况
                if isinstance(chunk, str):
                    data = json.loads(chunk)
                else:
                    data = chunk
                # 提取SearchInfo和RecommendedQuestions字段
                search_info = data.get('SearchInfo', {})
                recommended_questions = data.get('RecommendedQuestions', [])

                # 安全提取delta_content
                delta_content = ''
                reasoning_content = ''
                
                choices = data.get('answer', [])
                if choices and isinstance(choices, list) and isinstance(choices[0], dict):
                    delta = choices[0].get('Delta', {})
                    if isinstance(delta, dict):
                        content = delta.get('Content', '')
                        # 确保content是字符串类型
                        if isinstance(content, str):
                            delta_content = content
                        elif isinstance(content, (int, float)):
                            delta_content = str(content)
                        else:
                            delta_content = ''

                        # 提取reasoning_content
                        reasoning = delta.get('ReasoningContent', '')
                        # 确保reasoning_content是字符串类型
                        if isinstance(reasoning, str):
                            reasoning_content = reasoning
                        elif isinstance(reasoning, (int, float)):
                            reasoning_content = str(reasoning)
                        else:
                            reasoning_content = ''
                # 构建SSE数据
                sse_data = json.dumps({
                    "content": delta_content,
                    "reasoning_content": reasoning_content,
                    "role": "assistant",
                    "search_info": search_info,
                    "recommended_questions": recommended_questions
                })
                
                # 发送流式数据
                yield f"data: {sse_data}\n\n"
            except Exception as e:
                error_data = json.dumps({"error": f"响应处理失败: {str(e)}", "raw_chunk": str(chunk)})
                yield f"data: {error_data}\n\n"
                continue 
            
    return Response(generate(), mimetype='text/event-stream')

# 解析Qwen API响应函数
def parse_qwen_response(response):
    if response is None:
        return jsonify({"error": "模型调用失败", "status": "failed"}), 500

    if isinstance(response, str):
        return jsonify({"error": response, "status": "failed"}), 500

    # 定义生成器函数
    def generate():
        try:
            for chunk in response:
                try:
                    # 使用model_dump()方法将chunk转换为字典
                    data = chunk.model_dump()
                    # 检查API错误
                    if 'error' in data:
                        print(f"API error received: {data['error']}")
                        yield f"data: {json.dumps(data)}\n\n"
                        continue
                    
                    # 安全提取delta_content和reasoning_content
                    delta_content = ''
                    reasoning_content = ''
                    function_call = ''
                    if isinstance(data, dict):
                        choices = data.get('choices', [])
                        if choices and isinstance(choices, list) and isinstance(choices[0], dict):
                            delta = choices[0].get('delta', {})
                            if isinstance(delta, dict):
                                content = delta.get('content', '')
                                # 确保content是字符串类型
                                if isinstance(content, str):
                                    delta_content = content
                                elif isinstance(content, (int, float)):
                                    delta_content = str(content)
                                else:
                                    delta_content = ''
                                
                                # 提取reasoning_content
                                reasoning = delta.get('reasoning_content', '')
                                if isinstance(reasoning, str):
                                    reasoning_content = reasoning
                                elif isinstance(reasoning, (int, float)):
                                    reasoning_content = str(reasoning)
                                else:
                                    reasoning_content = ''

                                # 提取function_call
                                function_call = delta.get('function_call', {})
                                if isinstance(function_call, dict):
                                    function_call = json.dumps(function_call)

                    sse_data = json.dumps({
                        "content": delta_content,
                        "reasoning_content": reasoning_content,
                        "role": "assistant",
                        "function_call": function_call
                    })
                    # 发送流式数据
                    yield f"data: {sse_data}\n\n"
                except Exception as e:
                    print(f"响应处理错误: {str(e)}")
                    error_data = json.dumps({"error": f"响应处理失败: {str(e)}", "raw_chunk": str(chunk)})
                    yield f"data: {error_data}\n\n"
                    continue
            # 发送完整响应作为结束标记
            yield f"data: {json.dumps({'type': 'complete', 'content': ''}, ensure_ascii=False)}\n\n"
        except Exception as e:
            error_data = json.dumps({"error": str(e)})
            print(f"SSE error: {error_data}")
            yield f'data: {error_data}\n\n'
            
    return Response(generate(), content_type='text/event-stream')

# 解析万相API响应函数
def parse_wan2_response(response):
    """
    解析万相API响应
    """
    if response is None:
        return jsonify({"error": "模型调用失败", "status": "failed"}), 500
    
    # 检查HTTP状态码
    if response.status_code != HTTPStatus.OK:
        return jsonify({"error": f"模型调用失败，状态码: {response.status_code}", "status": "failed"}), 500
    
    # 检查响应内容
    if not response.output or not hasattr(response.output, 'task_id'):
        return jsonify({"error": "模型响应格式错误", "status": "failed"}), 500
    
    # 获取任务ID
    task_id = response.output.task_id
    
    # 轮询任务状态
    while True:
        # 使用DashScope SDK查询任务结果
        try:
            result = dashscope.ImageSynthesis.fetch(task_id)
            if result.status_code == HTTPStatus.OK:
                data = result.output
                if data.task_status == "SUCCEEDED":  # 注意这里是SUCCEEDED而不是SUCCEED
                    # 返回图像URL列表、实际提示词列表、原始提示词
                    image_urls = [item.url for item in data.results]
                    actual_prompts = [item.actual_prompt for item in data.results]
                    
                    print("成功响应:", data)
                    return jsonify({"image_urls": image_urls, "actual_prompts":actual_prompts, "status": "success"})
                elif data.task_status == "FAILED":
                    print("失败响应:", data)
                    return jsonify({"error": data.message, "status": "failed"}), 500
                else:
                    print("其他状态响应:", data)
                    time.sleep(3)
            else:
                print(f"查询任务失败: {result.code}, {result.message}")
                return jsonify({"error": result.message, "status": "failed"}), 500
        except Exception as e:
            print(f"查询任务异常: {str(e)}")
            return jsonify({"error": f"查询任务异常: {str(e)}", "status": "failed"}), 500

# 解析ModelScope Image API响应函数
def parse_modelscope_image_response(response, common_headers, base_url):
    """
    解析ModelScope Image API响应
    """
    if response is None:
        return jsonify({"error": "模型调用失败", "status": "failed"}), 500
    response.raise_for_status()
    task_id = response.json()["task_id"]
    
    # 轮询任务状态
    while True:
        result = requests.get(
            f"{base_url}v1/tasks/{task_id}",
            headers={**common_headers, "X-ModelScope-Task-Type": "image_generation"},
        )
        result.raise_for_status()
        data = result.json()
        print("原始响应:",data)
        if data["task_status"] == "SUCCEED":
            # 返回图像URL列表
            image_urls = data["output_images"]
            print("成功响应:",data)
            return jsonify({"image_urls": image_urls, "status": "success"})
        elif data["task_status"] == "FAILED":
            print("失败响应:",data)
            return jsonify({"error": data["error_message"], "status": "failed"}), 500
        else:
            print("其他状态响应:",data)
            time.sleep(3)

# 解析万相视频 API响应函数
def parse_wan2_video_response(response):
    """
    解析万相视频 API响应
    """
    if response is None:
        return jsonify({"error": "模型调用失败", "status": "failed"}), 500
    
    # 检查HTTP状态码
    if response.status_code != HTTPStatus.OK:
        return jsonify({"error": f"模型调用失败，状态码: {response.status_code}", "status": "failed"}), 500
    
    # 检查响应内容
    if not response.output or not hasattr(response.output, 'task_id'):
        return jsonify({"error": "模型响应格式错误", "status": "failed"}), 500
    
    # 获取任务ID
    task_id = response.output.task_id
    
    # 轮询任务状态
    while True:
        # 使用DashScope SDK查询任务结果
        result = dashscope.VideoSynthesis.fetch(task_id)
        if result.status_code == HTTPStatus.OK:
            data = result.output
            usage = result.usage
            if data.task_status == "SUCCEEDED":  # 注意这里是SUCCEEDED而不是SUCCEED
                # 返回视频URL列表
                print("成功响应:", data)
                video_url = data.video_url
                actual_prompt = data.actual_prompt
                return jsonify({"video_url": video_url, "actual_prompt": actual_prompt, "usage": usage, "status": "success"})
            elif data.task_status == "FAILED":
                print("失败响应:", data)
                return jsonify({"error": data.message, "status": "failed"}), 500
            else:
                print("其他状态响应:", data)
                time.sleep(3)
        else:
            print(f"查询任务失败: {result.code}, {result.message}")
            return jsonify({"error": result.message, "status": "failed"}), 500

# 模型调用路由
@app.route('/api/model', methods=['POST'])
def model():
    data = request.json
    name = data.get('name', 'qwen-max') # 模型名称
    model = data.get('model', 'Qwen/Qwen-Image') #模型
    messages = data.get('messages', '') #消息
    stream = data.get('stream', True) #是否流式
    image_size = data.get('image_size', '1:1') #图片大小
    video_size = data.get('video_size', '1:1') #视频分辨率

    try:
        api_messages = _build_api_messages(messages, name)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

     # 图片尺寸映射
    size_options = {
        "1:1": [1024, 1024],
        "16:9": [1440, 810],
        "9:16": [810, 1440],
        "4:3": [1440, 1080],
        "3:4": [1080, 1440],
        "2:3": [960, 1440],
        "3:2": [1440, 960]
    }
    
    # 获取实际尺寸
    width, height = size_options.get(image_size, [1024, 1024])

    print(f"模型名称: {name}")
    print(f"模型: {model}")
    print(f"消息: {messages}")
    print(f"图片大小: {image_size}")
    print(f"是否流式: {stream}")  
    print(f"API消息序列: {api_messages}")
    
    # ModelScope API配置
    base_url = 'https://api-inference.modelscope.cn/'
    api_key = os.environ.get("MODELSCOPE_API_KEY")

    common_headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # 混元模型
    if name == 'Hunyuan-T1' or name == 'Hunyuan-Turbos' \
        or name == 'Hunyuan-Code':
        # 初始化混元API
        hunyuan = HunyuanAPI(
            secret_id=os.environ.get("HUNYUAN_SECRET_ID"),
            secret_key=os.environ.get("HUNYUAN_SECRET_KEY")
        )

        response = hunyuan.chat_completion(
            model=model,
            messages=api_messages,
            stream=stream
        )
        # 解析混元API响应函数
        parsed_response = parse_hunyuan_response(response)
        return parsed_response
    elif name == 'Qwen-Max' or name == 'Qwen-Plus' or \
        name == 'Qwen-Flash' or name == 'Qwen-Turbo': 
        # 初始化Qwen API
        api_key = os.environ.get("QWEN_API_KEY")  # 获取API密钥
        qwen = QwenAPI(api_key)
        response = qwen.chat_completion(
            messages=api_messages,
            stream=stream,
            model=model,
            extra_body={
                "enable_search": True,
                "enable_thinking": True
            }
        )
        # 解析Qwen API响应函数
        parsed_response = parse_qwen_response(response)
        return parsed_response
    elif name == 'Qwen3-Coder-Plus':        
        # 初始化Qwen API
        api_key = os.environ.get("QWEN_API_KEY")  # 获取API密钥
        qwen = QwenAPI(api_key)
        response = qwen.chat_completion(
            messages=api_messages,
            stream=stream,
            model=model,
            extra_body={
                "enable_thinking": True
            }
        )
        # 解析Qwen API响应函数
        parsed_response = parse_qwen_response(response)
        return parsed_response
    elif name == 'Qwen-MT-Plus':
        # 初始化Qwen API
        api_key = os.environ.get("QWEN_API_KEY")  # 获取API密钥
        qwen = QwenAPI(api_key)
        response = qwen.chat_completion(
            messages=api_messages,
            stream=stream,
            model=model,
            extra_body={
                "translation_options": {
                    "source_language": "Chinese", # 后续前端输入
                    "target_language": "English",   # 后续前端输入
                    "translation_type": "mt",
                    "model": "qwen-mt-plus"
                }
            }
        )
        # 解析Qwen API响应函数
        parsed_response = parse_qwen_response(response)
        return parsed_response
    elif name == 'Wan2.2-Plus' or name == 'Wan2.2-Flash':
        # 初始化万相API
        api_key = os.environ.get("WAN_API_KEY")  # 获取API密钥
        wan2 = Wan2API(api_key)
        response = wan2.chat_completion(
            messages=messages,
            stream=stream,
            model=model,
            extra_body={
                "size": f"{width}*{height}",
                "n": 2
            }
        )
        # 解析万相 API响应函数
        parsed_response = parse_wan2_response(response)
        return parsed_response
    elif name == 'Qwen-Image':
        # 初始化Qwen-Image API  ModleScope API接口
        qwen_image = ModelScopeImageAPI(base_url, common_headers)
        response = qwen_image.chat_completion(
            messages=messages,
            stream=stream,
            model=model,
            extra_body={
                "size": f"{width}x{height}",
                "n": 2 # 当前不支持该参数
            }
        )
        # 解析Qwen-Image API响应函数
        parsed_response = parse_modelscope_image_response(response, common_headers, base_url)
        return parsed_response
    elif name == 'DeepSeek-R1-0528' or name == 'DeepSeek-V3' or \
        name == 'Kimi-K2-Instruct' or name == 'GLM-4.5':
        # 初始化ModleScope API接口
        qwen = ModelScopeAPI(os.environ.get("MODELSCOPE_API_KEY"))
        response = qwen.chat_completion(
            messages=api_messages,
            stream=stream,
            model=model,
            extra_body={
                "enable_search": True,
                "enable_thinking": True
            }
        )
        # 解析Qwen API响应函数
        parsed_response = parse_qwen_response(response)
        return parsed_response
    elif name == "Qwen3-Thinking" or name == 'Qwen3-32B':
        # 初始化ModleScope API接口
        qwen = ModelScopeAPI(os.environ.get("MODELSCOPE_API_KEY"))
        response = qwen.chat_completion(
            messages=api_messages,
            stream=stream,
            model=model,
            extra_body={
                "enable_thinking": True
            }
        )
        # 解析Qwen API响应函数
        parsed_response = parse_qwen_response(response)
        return parsed_response
    elif name == 'Qwen3-Code':
        # 初始化ModleScope API接口
        qwen = ModelScopeAPI(os.environ.get("MODELSCOPE_API_KEY"))
        response = qwen.chat_completion(
            messages=api_messages,
            stream=stream,
            model=model,
            extra_body={
                "enable_thinking": True,
                "enable_code": True
            }
        )
        # 解析Qwen API响应函数
        parsed_response = parse_qwen_response(response)
        return parsed_response
    elif name == 'Wan2.2-T2V-Plus' or name == 'Wanx2.1-T2V-Turbo' or \
         name == 'Wanx2.1-T2V-Plus':
        # 初始化万相视频API  Wan2 API接口
        api_key = os.environ.get("WAN_VIDEO_API_KEY")  # 获取API密钥
        wan2_video = Wan2VideoAPI(api_key)
        response = wan2_video.chat_completion(
            messages=messages,
            model=model,
            extra_body={
                "size": "1920*1080", # 后续需要传入参数
                "duration": 10  # 默认 5s，暂不支持该参数
            }
        )
        # 解析万相视频 API响应函数
        parsed_response = parse_wan2_video_response(response)
        return parsed_response
    else:
        return jsonify({"error": "不支持的模型"}), 400



if __name__ == '__main__':
    # 在5001端口启动服务，允许外部访问  
    # 所有模型调用的 python 总入口
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
