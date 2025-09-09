@echo off
echo 正在安装AIChat模型API服务...

REM 检查nssm工具是否存在
if not exist "nssm.exe" (
    echo 正在下载nssm工具...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/ci/nssm-2.24-101-g897c7ad.zip' -OutFile 'nssm.zip'"
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath ."
    move "nssm-2.24-101-g897c7ad\win64\nssm.exe" .
    rmdir /s /q "nssm-2.24-101-g897c7ad"
    del "nssm.zip"
)

REM 安装服务
nssm install AIChatModelAPI "%CD%\venv\Scripts\python.exe" "%CD%\api.py"
nssm set AIChatModelAPI Description "AIChat模型API服务 - 提供多种AI模型接口"
nssm set AIChatModelAPI AppDirectory "%CD%"
nssm set AIChatModelAPI AppStdout "%CD%\service.log"
nssm set AIChatModelAPI AppStderr "%CD%\service_error.log"
nssm set AIChatModelAPI Start SERVICE_AUTO_START

REM 启动服务
nssm start AIChatModelAPI

echo.
echo 服务安装完成！
echo 服务名称: AIChatModelAPI
echo 运行端口: 5001
echo 日志文件: service.log 和 service_error.log
echo.
echo 管理命令:
echo   启动服务: nssm start AIChatModelAPI
echo   停止服务: nssm stop AIChatModelAPI
echo   重启服务: nssm restart AIChatModelAPI
echo   卸载服务: nssm remove AIChatModelAPI confirm