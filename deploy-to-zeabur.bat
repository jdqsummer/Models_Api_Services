@echo off
chcp 65001 >nul

:: Zeabur 部署脚本 (Windows版本)
:: 使用方法: deploy-to-zeabur.bat

echo === Model API Service Zeabur 部署工具 ===
echo.

:: 检查Docker是否安装
echo [INFO] 检查Docker安装...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker 未安装，请先安装 Docker
    pause
    exit /b 1
)
echo [INFO] Docker 已安装

:: 构建Docker镜像
echo [INFO] 正在构建 Docker 镜像...
docker build -t model-api-service .
if errorlevel 1 (
    echo [ERROR] Docker 镜像构建失败
    pause
    exit /b 1
)
echo [INFO] Docker 镜像构建完成

:: 询问是否运行本地测试
echo.
set /p run_test="是否运行本地测试? (y/n): "
if /i "%run_test%"=="y" (
    echo [INFO] 启动本地测试容器...
    
    :: 停止并删除可能存在的旧容器
    docker stop model-api-test 2>nul
    docker rm model-api-test 2>nul
    
    :: 启动新容器
    docker run -d -p 5001:5001 --name model-api-test model-api-service
    
    :: 等待服务启动
    timeout /t 5 /nobreak >nul
    
    :: 测试健康检查
    curl -s http://localhost:5001/health | find "healthy" >nul
    if errorlevel 1 (
        echo [ERROR] 本地测试失败
        echo [INFO] 容器日志:
        docker logs model-api-test
        
        :: 清理容器
        docker stop model-api-test 2>nul
        docker rm model-api-test 2>nul
        
        pause
        exit /b 1
    ) else (
        echo [INFO] 本地测试通过
    )
    
    :: 停止测试容器
    docker stop model-api-test 2>nul
    docker rm model-api-test 2>nul
)

echo.
echo === Zeabur 部署说明 ===
echo.
echo 1. 将代码推送到Git仓库:
echo    git add .
echo    git commit -m "准备Zeabur部署"
echo    git push origin main
echo.
echo 2. 登录 Zeabur (https://zeabur.com)
echo.
echo 3. 创建新项目并连接Git仓库
echo.
echo 4. Zeabur会自动检测并部署
echo.
echo 5. 或者使用Docker镜像部署:
echo    - 推送镜像到Docker Hub:
echo      docker tag model-api-service yourusername/model-api-service:latest
echo      docker push yourusername/model-api-service:latest
echo    - 在Zeabur中选择 "Deploy from Docker Hub"
echo.
echo 6. 重要：在Zeabur控制台中设置环境变量:
echo    - 进入服务 -> Environment Variables
echo    - 添加AI服务API密钥（如需要）:
echo        HUNYUAN_SECRET_ID, HUNYUAN_SECRET_KEY
echo        QWEN_API_KEY, WAN_API_KEY, WAN_VIDEO_API_KEY
echo        MODELSCOPE_API_KEY
echo.

echo [INFO] 部署准备完成！
echo.
pause