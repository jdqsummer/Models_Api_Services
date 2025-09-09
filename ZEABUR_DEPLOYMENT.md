# Zeabur 部署指南

## 项目概述
这是一个基于Flask的AI模型API服务，提供多种AI模型的统一接口。

## 部署到 Zeabur

### 方法一：通过Git仓库部署
1. 将代码推送到GitHub/GitLab仓库
2. 登录 [Zeabur](https://zeabur.com)
3. 创建新项目
4. 连接你的Git仓库
5. 选择部署分支
6. Zeabur会自动检测并构建Docker镜像
7. 部署完成后，Zeabur会提供访问URL

### 方法二：通过Docker镜像部署
1. 构建Docker镜像：
   ```bash
   docker build -t model-api-service .
   ```

2. 推送镜像到Docker Hub：
   ```bash
   docker tag model-api-service yourusername/model-api-service:latest
   docker push yourusername/model-api-service:latest
   ```

3. 在Zeabur中选择"Deploy from Docker Hub"
4. 输入镜像名称：`yourusername/model-api-service:latest`
5. 配置环境变量和资源

## 环境变量配置

在Zeabur控制台中设置以下环境变量：

### 必需配置
| 变量名 | 描述 | 默认值 | 必需 |
|--------|------|--------|------|
| `FLASK_ENV` | Flask环境 | `production` | 是 |
| `PYTHONUNBUFFERED` | Python输出缓冲 | `1` | 是 |

### AI服务API密钥配置（根据需要使用）
| 变量名 | 描述 | 必需 |
|--------|------|------|
| `HUNYUAN_SECRET_ID` | 腾讯云混元API Secret ID | 否 |
| `HUNYUAN_SECRET_KEY` | 腾讯云混元API Secret Key | 否 |
| `QWEN_API_KEY` | 通义千问API密钥 | 否 |
| `WAN_API_KEY` | 万相API密钥 | 否 |
| `WAN_VIDEO_API_KEY` | 万相视频API密钥 | 否 |
| `MODELSCOPE_API_KEY` | ModelScope API密钥 | 否 |

### 可选配置
| 变量名 | 描述 | 默认值 | 必需 |
|--------|------|--------|------|
| `PORT` | 服务端口 | `5001` | 否 |
| `HOST` | 服务监听地址 | `0.0.0.0` | 否 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 |
| `WORKER_COUNT` | Gunicorn工作进程数 | `4` | 否 |
| `THREAD_COUNT` | 每个工作进程线程数 | `2` | 否 |
| `REQUEST_TIMEOUT` | 请求超时时间(秒) | `30` | 否 |

### 设置方法
1. 在Zeabur控制台中选择你的服务
2. 进入"Environment Variables"标签页
3. 点击"Add Variable"添加新的环境变量
4. 输入变量名和值
5. 保存后服务会自动重新部署

## 服务配置
- **端口**: 5001
- **健康检查**: `/health`
- **构建方式**: Docker
- **运行时**: Python 3.8

## 本地测试

1. 构建镜像：
   ```bash
   docker build -t model-api-service .
   ```

2. 运行容器：
   ```bash
   docker run -p 5001:5001 --name model-api model-api-service
   ```

3. 测试健康检查：
   ```bash
   curl http://localhost:5001/health
   ```

## 故障排除

### 构建失败
- 检查Dockerfile语法
- 确认requirements.txt中的包版本兼容性

### 服务无法启动
- 检查端口5001是否被占用
- 查看容器日志：`docker logs model-api`

### 健康检查失败
- 确认应用正确监听5001端口
- 检查`/health`端点是否可访问

## 监控和日志

- Zeabur提供内置的日志查看功能
- 可以通过Zeabur控制台查看实时日志
- 设置告警规则监控服务状态

## 自动伸缩

Zeabur支持基于CPU使用率的自动伸缩：
- 最小副本数：1
- 最大副本数：3
- CPU使用率阈值：80%

## 域名和SSL

- Zeabur提供自动的HTTPS证书
- 可以绑定自定义域名
- 支持HTTP/2协议