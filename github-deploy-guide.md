# GitHub部署问题排查指南

## 🔍 问题描述
GitHub部署无法正常访问，但本地上传部署成功

## 🎯 可能的原因和解决方案

### 1. Git子模块或.git目录问题
GitHub部署时可能缺少.git目录或子模块

**解决方案**:
```yaml
# 在zeabur.yaml中添加
build:
  dockerfile: Dockerfile
  context: .
  args:
    - BUILDKIT_CONTEXT_KEEP_GIT_DIR=1
```

### 2. 文件路径大小写问题
GitHub对文件名大小写敏感，Windows不敏感

**检查**:
```bash
# 检查所有文件路径
find . -name "*.py" | grep -E "[A-Z]"
```

### 3. 环境变量配置
GitHub部署时环境变量可能未正确设置

**解决方案**:
- 在Zeabur控制台确认所有环境变量已设置
- 特别是 `MODELSCOPE_API_KEY` 和其他AI服务密钥

### 4. 构建缓存问题
GitHub构建可能使用了错误的缓存

**解决方案**:
- 在Zeabur中清除构建缓存
- 或者强制重新构建

### 5. 端口映射问题

**确认zeabur.yaml配置**:
```yaml
ports:
  - port: 5001
    protocol: TCP
```

### 6. 文件权限问题
GitHub部署时文件权限可能不同

**在Dockerfile中添加**:
```dockerfile
# 确保文件权限正确
RUN chmod +x /app/*.sh
```

## 🚀 部署检查清单

### 部署前检查
1. ✅ 所有Python文件使用小写命名
2. ✅ 环境变量在Zeabur控制台正确设置
3. ✅ Dockerfile中无硬编码的绝对路径
4. ✅ requirements.txt包含所有依赖
5. ✅ .gitignore不会过滤部署必需文件

### GitHub特定检查
1. ✅ 仓库设置为公开或Zeabur有访问权限
2. ✅ 分支名称正确（main/master）
3. ✅ 无.gitmodules或子模块问题
4. ✅ 文件大小写一致

### Zeabur控制台检查
1. ✅ 构建日志无错误
2. ✅ 容器正常启动
3. ✅ 健康检查通过
4. ✅ 端口映射正确

## 📋 故障排除步骤

### 步骤1: 检查构建日志
在Zeabur控制台查看详细的构建日志

### 步骤2: 本地模拟GitHub环境
```bash
# 克隆到新目录测试（模拟GitHub环境）
git clone your-repo-url test-deploy
cd test-deploy

# 构建测试
docker build -t test-image .

# 运行测试
docker run -p 5001:5001 test-image
```

### 步骤3: 验证环境变量
```bash
# 在Zeabur容器中检查环境变量
docker exec -it container-name env
```

### 步骤4: 检查文件是否存在
```bash
# 进入容器检查文件
docker exec -it container-name ls -la /app
```

## 🔧 紧急修复

如果GitHub部署持续失败，可以：

1. **使用Docker Hub部署**:
   ```bash
   docker tag model-api-service yourusername/model-api-service:latest
   docker push yourusername/model-api-service:latest
   ```
   
   然后在Zeabur中选择"Deploy from Docker Hub"

2. **手动上传ZIP**:
   - 将代码打包为ZIP文件
   - 在Zeabur中选择"Upload ZIP"

## 📞 支持

如果问题仍然存在：

1. 查看Zeabur官方文档：https://docs.zeabur.com
2. 联系Zeabur支持
3. 提供详细的构建日志和错误信息

## ✅ 验证部署成功

部署成功后，测试以下端点：

- `GET /health` - 健康检查
- `GET /` - 根目录
- `POST /api/model` - 模型API

使用curl测试：
```bash
curl https://your-zeabur-url.zeabur.app/health
```