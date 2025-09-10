#!/bin/bash

# GitHub部署诊断脚本
# 用于诊断GitHub部署成功但无法访问的问题

echo "🔍 GitHub部署诊断工具"
echo "========================"

# 检查当前目录的文件结构
echo "📁 文件结构检查:"
find . -name "*.py" -o -name "*.yaml" -o -name "*.yml" -o -name "Dockerfile" -o -name "requirements.txt" | head -20
echo ""

# 检查文件权限
echo "🔒 文件权限检查:"
ls -la Dockerfile zeabur.yaml gunicorn.conf.py main.py requirements.txt
echo ""

# 检查Python文件编码
echo "🐍 Python文件编码检查:"
for file in *.py; do
    if [ -f "$file" ]; then
        encoding=$(file -i "$file" | awk -F'=' '{print $2}')
        echo "$file: $encoding"
    fi
done
echo ""

# 模拟GitHub构建环境
echo "🐳 模拟GitHub Docker构建:"
docker build -t github-test . > docker-build.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Docker构建成功"
    
    # 运行测试容器
    echo "🚀 启动测试容器:"
    docker run -d --name github-test-container -p 5002:5001 github-test
    
    # 等待服务启动
    sleep 10
    
    # 检查容器日志
    echo "📋 容器日志:"
    docker logs github-test-container | tail -20
    
    # 检查容器内部状态
    echo "🔍 容器内部检查:"
    docker exec github-test-container ps aux
    echo ""
    
    # 测试端口访问
    echo "🌐 测试本地访问:"
    if curl -s http://localhost:5002/health; then
        echo "✅ 本地访问成功"
    else
        echo "❌ 本地访问失败"
        echo "尝试容器内部访问:"
        docker exec github-test-container curl -s http://localhost:5001/health || echo "容器内部访问也失败"
    fi
    
    # 清理
    docker stop github-test-container
    docker rm github-test-container
    
else
    echo "❌ Docker构建失败"
    echo "构建日志:"
    cat docker-build.log | tail -20
fi

echo ""
echo "📋 GitHub部署问题排查清单:"
echo "1. ✅ 检查zeabur.yaml端口配置 (targetPort: 5001)"
echo "2. ✅ 检查Dockerfile EXPOSE 5001"
echo "3. 🔍 查看Zeabur控制台的服务发现配置"
echo "4. 🔍 检查GitHub仓库的Webhook设置"
echo "5. 🔍 查看Zeabur的网络策略和入口规则"
echo ""
echo "💡 建议解决方案:"
echo "- 在Zeabur控制台手动重新部署"
echo "- 检查服务域名解析"
echo "- 验证GitHub Webhook推送"
echo "- 联系Zeabur支持查看服务发现日志"