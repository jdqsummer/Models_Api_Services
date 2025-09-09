@echo off
echo 正在卸载AIChat模型API服务...

REM 检查nssm工具是否存在
if not exist "nssm.exe" (
    echo nssm工具不存在，请先运行install_service.bat安装服务
    pause
    exit /b 1
)

REM 停止并删除服务
nssm stop AIChatModelAPI
nssm remove AIChatModelAPI confirm

echo 服务卸载完成！
echo.
echo 如果需要重新安装，请运行install_service.bat
pause