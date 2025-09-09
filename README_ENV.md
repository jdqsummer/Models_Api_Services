# 环境变量配置指南

本文档说明如何在 Model API Services 中使用环境变量配置 API 密钥。

## 环境变量配置

### 1. 复制环境变量模板

```bash
cp .env.example .env
```

### 2. 配置环境变量

编辑 `.env` 文件，填写您的实际 API 密钥：

```env
# 腾讯云混元API配置
HUNYUAN_SECRET_ID=your_actual_hunyuan_secret_id
HUNYUAN_SECRET_KEY=your_actual_hunyuan_secret_key

# 通义千问API配置
QWEN_API_KEY=your_actual_qwen_api_key

# 万相API配置
WAN_API_KEY=your_actual_wan_api_key
WAN_VIDEO_API_KEY=your_actual_wan_video_api_key

# ModelScope API配置
MODELSCOPE_API_KEY=your_actual_modelscope_api_key
```

### 3. 加载环境变量

#### 方法一：使用 python-dotenv（推荐）

安装依赖：
```bash
pip install python-dotenv
```

在代码中加载：
```python
from dotenv import load_dotenv
load_dotenv()
```

#### 方法二：手动设置环境变量

Linux/macOS:
```bash
export HUNYUAN_SECRET_ID=your_actual_secret_id
export HUNYUAN_SECRET_KEY=your_actual_secret_key
# 其他变量同理
```

Windows:
```cmd
set HUNYUAN_SECRET_ID=your_actual_secret_id
set HUNYUAN_SECRET_KEY=your_actual_secret_key
# 其他变量同理
```

## 支持的API服务

### 腾讯云混元 (Hunyuan)
- 环境变量：`HUNYUAN_SECRET_ID`, `HUNYUAN_SECRET_KEY`
- 默认值：硬编码的测试密钥（仅用于测试）

### 通义千问 (Qwen)
- 环境变量：`QWEN_API_KEY`
- 默认值：硬编码的测试密钥（仅用于测试）

### 万相 (Wan)
- 环境变量：`WAN_API_KEY`（图像生成）
- 环境变量：`WAN_VIDEO_API_KEY`（视频生成）
- 默认值：硬编码的测试密钥（仅用于测试）

### ModelScope
- 环境变量：`MODELSCOPE_API_KEY`
- 默认值：硬编码的测试密钥（仅用于测试）

## 安全建议

1. **不要将 `.env` 文件提交到版本控制**
   - 确保 `.env` 在 `.gitignore` 中
   - 只提交 `.env.example` 文件

2. **使用不同的环境**
   - 开发环境：`.env.development`
   - 生产环境：`.env.production`
   - 测试环境：`.env.test`

3. **定期轮换密钥**
   - 定期更新 API 密钥
   - 使用密钥管理服务（如 AWS Secrets Manager）

## Zeabur 部署环境变量设置

在 Zeabur 平台部署时，需要通过控制台设置环境变量：

1. 登录 Zeabur 控制台 (https://zeabur.com)
2. 选择您的服务
3. 进入 "Environment Variables" 标签页
4. 点击 "Add Variable" 添加环境变量
5. 输入变量名和实际值
6. 保存后服务会自动重新部署

### 必需设置的环境变量
- `FLASK_ENV=production`
- `PYTHONUNBUFFERED=1`

### AI服务API密钥（根据需要使用）
- `HUNYUAN_SECRET_ID` - 腾讯云混元Secret ID
- `HUNYUAN_SECRET_KEY` - 腾讯云混元Secret Key
- `QWEN_API_KEY` - 通义千问API密钥
- `WAN_API_KEY` - 万相API密钥
- `WAN_VIDEO_API_KEY` - 万相视频API密钥
- `MODELSCOPE_API_KEY` - ModelScope API密钥

## 故障排除

### 环境变量未生效
1. 检查 `.env` 文件路径是否正确
2. 确认 `python-dotenv` 已安装
3. 重启应用使环境变量生效

### Zeabur 环境变量设置问题
1. 确认在 Zeabur 控制台中正确设置了环境变量
2. 检查变量名拼写是否正确
3. 保存后等待服务重新部署完成

### 环境变量必需设置
现在系统不再提供硬编码的默认测试密钥，必须通过环境变量设置正确的API密钥才能正常运行服务。