# GitHub部署问题排查清单

## 问题描述
GitHub部署显示成功，但无法通过URL+端口正常访问，而本地上传部署正常。

## 根本原因分析
GitHub部署与本地上传的主要差异：
1. **构建上下文不同**：GitHub使用git clone，本地上传使用文件上传
2. **文件权限和所有权**
3. **网络配置和服务发现**
4. **环境变量注入时机**

## 检查清单

### 1. 文件结构和权限 ✅
- [x] Dockerfile存在且可读
- [x] zeabur.yaml配置正确
- [x] 所有Python文件UTF-8编码
- [x] 必要的配置文件存在

### 2. Docker构建配置 ✅
- [x] Dockerfile EXPOSE 5001
- [x] 多阶段构建正确
- [x] 非root用户配置
- [x] 健康检查配置

### 3. Zeabur配置更新 ✅
```yaml
ports:
  - port: 5001
    protocol: TCP
    targetPort: 5001  # 明确指定内部端口映射
```

### 4. GitHub特定问题排查

#### 4.1 构建上下文问题
- [ ] 检查`.dockerignore`是否过滤了必要文件
- [ ] 验证GitHub的git上下文包含所有文件
- [ ] 确保没有git子模块问题

#### 4.2 网络和服务发现
- [ ] 在Zeabur控制台检查服务状态
- [ ] 查看服务发现日志
- [ ] 检查网络策略和入口规则

#### 4.3 环境变量
- [ ] 确保GitHub部署时环境变量正确注入
- [ ] 检查敏感API密钥配置

## 立即执行步骤

1. **重新部署**: 在Zeabur控制台手动触发重新部署
2. **检查日志**: 查看构建和运行时日志
3. **验证服务发现**: 检查服务域名解析
4. **网络测试**: 使用Zeabur提供的测试工具

## 诊断命令

```bash
# 本地模拟GitHub构建
docker build -t github-test .

# 运行测试
docker run -d -p 5002:5001 --name test-container github-test

# 检查日志
docker logs test-container

# 测试访问
curl http://localhost:5002/health
```

## 紧急修复方案

### 方案A: 强制重建
1. 在Zeabur控制台删除服务
2. 重新通过GitHub部署
3. 检查所有环境变量

### 方案B: 混合部署
1. 使用本地上传部署核心服务
2. 通过GitHub部署进行CI/CD

### 方案C: 使用Docker Hub
1. 构建镜像推送到Docker Hub
2. 在Zeabur中使用Docker Hub镜像

## 联系支持

如果以上步骤都无法解决问题：
- 联系Zeabur技术支持
- 提供部署ID和日志
- 描述GitHub vs 本地上传的差异

## 预防措施

1. **定期验证**: 每月验证GitHub部署流程
2. **监控告警**: 设置部署失败告警
3. **备份策略**: 保持本地上传作为备份方案
4. **文档更新**: 及时更新部署文档