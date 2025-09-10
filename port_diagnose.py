#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端口监听诊断工具 - 专门用于诊断Zeabur部署的端口问题
"""

import os
import socket
import subprocess
import sys

def check_port_listening(port=5001):
    """检查指定端口是否被监听"""
    print(f"🔍 检查端口 {port} 监听状态...")
    
    try:
        # 创建socket测试端口
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        
        # 尝试绑定端口（如果端口被占用会失败）
        result = sock.connect_ex(('0.0.0.0', port))
        
        if result == 0:
            print(f"  ✅ 端口 {port} 正在被监听")
            return True
        else:
            print(f"  ❌ 端口 {port} 未被监听 (错误代码: {result})")
            return False
            
    except Exception as e:
        print(f"  💥 端口检查错误: {e}")
        return False
    finally:
        sock.close()

def check_environment_variables():
    """检查环境变量配置"""
    print("🔍 检查环境变量配置...")
    
    important_vars = [
        'PORT',
        'HOST', 
        'FLASK_ENV',
        'PYTHONUNBUFFERED'
    ]
    
    for var in important_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: 未设置")

def check_process_listening():
    """检查当前进程监听状态"""
    print("🔍 检查进程监听状态...")
    
    try:
        # 在Linux环境下检查监听端口
        if sys.platform != 'win32':
            result = subprocess.run(['netstat', '-tlnp'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if ':5001' in line:
                        print(f"  ✅ 找到端口监听: {line.strip()}")
                        return
                print("  ❌ 未找到端口5001的监听")
            else:
                print("  ⚠️  netstat命令执行失败")
        else:
            print("  ⚠️  Windows环境，跳过netstat检查")
            
    except Exception as e:
        print(f"  💥 进程检查错误: {e}")

def simulate_zeabur_environment():
    """模拟Zeabur环境变量"""
    print("🔍 模拟Zeabur环境配置...")
    
    # Zeabur可能设置的环境变量
    zeabur_env = {
        'PORT': '5001',
        'HOST': '0.0.0.0',
        'FLASK_ENV': 'production',
        'PYTHONUNBUFFERED': '1'
    }
    
    for key, value in zeabur_env.items():
        current_value = os.environ.get(key)
        if current_value != value:
            print(f"  ⚠️  {key}: 当前='{current_value}', 期望='{value}'")
        else:
            print(f"  ✅ {key}: {current_value}")

def main():
    print("=" * 60)
    print("🔧 Zeabur端口监听诊断工具")
    print("=" * 60)
    
    # 检查端口监听
    port_ok = check_port_listening(5001)
    
    # 检查环境变量
    check_environment_variables()
    
    # 检查进程状态
    check_process_listening()
    
    # 模拟Zeabur环境
    simulate_zeabur_environment()
    
    print("\n" + "=" * 60)
    
    if port_ok:
        print("🎉 端口监听正常！")
        print("\n📋 如果Zeabur部署仍有问题，可能原因:")
        print("1. Zeabur网络策略限制")
        print("2. 服务发现配置问题")
        print("3. 健康检查端点未正确响应")
    else:
        print("❌ 端口监听有问题！")
        print("\n📋 解决方案:")
        print("1. 检查Gunicorn配置中的bind地址")
        print("2. 验证Dockerfile的EXPOSE指令")
        print("3. 确认Zeabur端口映射配置")
        print("4. 检查防火墙/安全组设置")
    
    print("\n💡 建议在Zeabur控制台查看服务日志获取详细错误信息")

if __name__ == "__main__":
    main()