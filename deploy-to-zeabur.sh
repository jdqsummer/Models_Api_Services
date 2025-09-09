#!/bin/bash

# Zeabur 部署脚本
# 使用方法: ./deploy-to-zeabur.sh [选项]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Docker是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    print_status "Docker 已安装"
}

# 构建Docker镜像
build_image() {
    print_status "正在构建 Docker 镜像..."
    docker build -t model-api-service .
    print_status "Docker 镜像构建完成"
}

# 运行本地测试
run_local_test() {
    print_status "启动本地测试容器..."
    docker run -d -p 5001:5001 --name model-api-test model-api-service
    
    # 等待服务启动
    sleep 5
    
    # 测试健康检查
    if curl -s http://localhost:5001/health | grep -q "healthy"; then
        print_status "本地测试通过"
    else
        print_error "本地测试失败"
        docker logs model-api-test
        exit 1
    fi
    
    # 停止测试容器
    docker stop model-api-test
    docker rm model-api-test
}

# 显示部署说明
show_deployment_instructions() {
    echo ""
    echo "=== Zeabur 部署说明 ==="
    echo ""
    echo "1. 将代码推送到Git仓库:"
    echo "   git add ."
    echo "   git commit -m '准备Zeabur部署'"
    echo "   git push origin main"
    echo ""
    echo "2. 登录 Zeabur (https://zeabur.com)"
    echo ""
    echo "3. 创建新项目并连接Git仓库"
    echo ""
    echo "4. Zeabur会自动检测并部署"
    echo ""
    echo "5. 或者使用Docker镜像部署:"
    echo "   - 推送镜像到Docker Hub:"
    echo "     docker tag model-api-service yourusername/model-api-service:latest"
    echo "     docker push yourusername/model-api-service:latest"
    echo "   - 在Zeabur中选择 'Deploy from Docker Hub'"
    echo ""
    echo "6. 重要：在Zeabur控制台中设置环境变量:"
    echo "   - 进入服务 -> Environment Variables"
    echo "   - 添加AI服务API密钥（如需要）:"
    echo "       HUNYUAN_SECRET_ID, HUNYUAN_SECRET_KEY"
    echo "       QWEN_API_KEY, WAN_API_KEY, WAN_VIDEO_API_KEY"
    echo "       MODELSCOPE_API_KEY"
    echo ""
}

# 主函数
main() {
    echo "=== Model API Service Zeabur 部署工具 ==="
    echo ""
    
    # 检查Docker
    check_docker
    
    # 构建镜像
    build_image
    
    # 运行本地测试
    read -p "是否运行本地测试? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_local_test
    fi
    
    # 显示部署说明
    show_deployment_instructions
    
    print_status "部署准备完成！"
}

# 执行主函数
main "$@"