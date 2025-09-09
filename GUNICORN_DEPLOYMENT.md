# Gunicorn 部署指南

## 问题背景

在运行大型语言模型（如 Qwen3-Thinking）时，由于模型推理时间较长，经常出现 Gunicorn Worker Timeout 错误：

```
[2025-09-08 06:40:40 +0000] [7] [CRITICAL] WORKER TIMEOUT (pid:8)
```

## 解决方案

### 1. 超时配置

已添加 Gunicorn 配置文件 `gunicorn.conf.py`，主要配置：

- **timeout**: 300 秒（5分钟）- 工作进程超时时间
- **graceful_timeout**: 30 秒 - 优雅关闭超时时间
- **keepalive**: 5 秒 - 保持连接超时时间

### 2. 环境变量配置

在 `.env` 文件中添加以下配置：

```env
# Gunicorn超时配置（单位：秒）
GUNICORN_TIMEOUT=300
GUNICORN_GRACEFUL_TIMEOUT=30
```

### 3. Docker 部署

Dockerfile 已更新为使用 Gunicorn 启动应用：

```dockerfile
CMD ["gunicorn", "-c", "gunicorn.conf.py", "main:app"]
```

### 4. 健康检查

添加了健康检查端点 `/health`，用于容器健康检查。

## 部署步骤

### 本地开发环境

1. 安装 Gunicorn：
```bash
pip install gunicorn
```

2. 启动服务：
```bash
gunicorn -c gunicorn.conf.py main:app
```

### Docker 部署

1. 构建镜像：
```bash
docker build -t model-api-service .
```

2. 运行容器：
```bash
docker run -d -p 5001:5001 \
  -e GUNICORN_TIMEOUT=300 \
  -e GUNICORN_GRACEFUL_TIMEOUT=30 \
  model-api-service
```

### Zeabur 部署

1. 确保 `zeabur.yaml` 中的端口配置正确
2. 部署时自动使用新的 Dockerfile 配置

## 性能优化建议

1. **调整超时时间**：根据模型推理时间调整 `GUNICORN_TIMEOUT`
2. **增加工作进程**：调整 `WORKER_COUNT` 环境变量
3. **监控日志**：关注 Gunicorn 日志中的超时警告
4. **使用异步工作器**：对于 I/O 密集型任务，考虑使用 `gevent` 工作器

## 故障排除

如果仍然出现超时错误：

1. 检查模型推理时间是否超过配置的超时时间
2. 查看 Gunicorn 日志确认实际配置
3. 考虑进一步增加超时时间或优化模型调用

## 版本要求

- Python 3.8+
- Gunicorn 21.2.0+
- Flask 2.3.0+