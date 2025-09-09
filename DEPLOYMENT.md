# AIChat 模型API服务部署指南

## 服务概述
- 服务端口：5001
- 主要功能：提供多种AI模型接口（混元、Qwen、万相等）
- 技术栈：Python Flask + 各模型SDK

## 文件结构
```
model_api_service/
├── api.py                 # 主应用文件
├── requirements.txt       # Python依赖
├── *.py                  # 各模型API实现
├── install_service.bat   # Windows服务安装脚本
├── uninstall_service.bat # Windows服务卸载脚本
├── aichat-model-api.service # Linux systemd配置
├── Dockerfile            # 容器化部署配置
└── DEPLOYMENT.md         # 本文件
```

## 部署方式

### 1. Windows系统服务部署
```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装系统服务（管理员权限运行）
install_service.bat

# 卸载服务
uninstall_service.bat
```

### 2. Linux系统服务部署
```bash
# 安装依赖
sudo apt update
sudo apt install python3 python3-pip
pip3 install -r requirements.txt

# 复制服务文件
sudo cp aichat-model-api.service /etc/systemd/system/

# 重新加载systemd
sudo systemctl daemon-reload

# 启用并启动服务
sudo systemctl enable aichat-model-api
sudo systemctl start aichat-model-api

# 查看服务状态
sudo systemctl status aichat-model-api
```

### 3. Docker容器部署
```bash
# 构建镜像
docker build -t aichat-model-api .

# 运行容器
docker run -d -p 5001:5001 --name aichat-api aichat-model-api

# 使用docker-compose
docker-compose up -d
```

### 4. 直接运行（开发模式）
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python api.py
```

### 5. Zeabur云平台部署
详见 [ZEABUR_DEPLOYMENT.md](./ZEABUR_DEPLOYMENT.md)

**重要：在Zeabur部署时需要设置环境变量**
- 必需变量：`FLASK_ENV=production`, `PYTHONUNBUFFERED=1`
- AI服务API密钥（根据需要使用）：
  - `HUNYUAN_SECRET_ID`, `HUNYUAN_SECRET_KEY`
  - `QWEN_API_KEY`, `WAN_API_KEY`, `WAN_VIDEO_API_KEY`
  - `MODELSCOPE_API_KEY`

在Zeabur控制台 -> 服务 -> Environment Variables 中设置

## 服务管理

### Windows
```bash
# 启动服务
nssm start AIChatModelAPI

# 停止服务
nssm stop AIChatModelAPI

# 重启服务
nssm restart AIChatModelAPI

# 查看服务状态
nssm status AIChatModelAPI
```

### Linux
```bash
# 启动服务
sudo systemctl start aichat-model-api

# 停止服务
sudo systemctl stop aichat-model-api

# 重启服务
sudo systemctl restart aichat-model-api

# 查看日志
sudo journalctl -u aichat-model-api -f
```

## 健康检查
服务启动后，可以通过以下方式验证：
```bash
# 检查服务状态
curl http://localhost:5001/api/health

# 测试模型接口
curl -X POST http://localhost:5001/api/model \
  -H "Content-Type: application/json" \
  -d '{"name": "Qwen-Max", "messages": [{"Role": "user", "Content": "你好"}]}'
```

## 故障排除

1. **端口冲突**：修改api.py中的端口号
2. **依赖安装失败**：检查Python版本（需要3.8+）
3. **服务启动失败**：查看service_error.log日志文件
4. **API密钥错误**：检查各模型API的密钥配置

## 安全建议

1. 在生产环境中使用环境变量存储API密钥
2. 配置防火墙限制访问IP
3. 启用HTTPS加密传输
4. 定期更新依赖包版本