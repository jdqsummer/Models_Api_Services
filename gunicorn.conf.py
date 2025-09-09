import os

# Gunicorn配置文件
# 超时设置（单位：秒）
import os

# 工作进程超时时间（从环境变量获取，默认300秒=5分钟）
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 300))

# 优雅关闭超时时间
graceful_timeout = int(os.environ.get('GUNICORN_GRACEFUL_TIMEOUT', 30))

# 保持连接超时时间
keepalive = 5

# 工作进程数
workers = int(os.environ.get('WORKER_COUNT', 4))

# 每个工作进程的线程数
threads = int(os.environ.get('THREAD_COUNT', 2))

# 工作进程类
worker_class = 'sync'

# 最大请求数（防止内存泄漏）
max_requests = int(os.environ.get('MAX_REQUESTS', 1000))
max_requests_jitter = 50

# 日志配置
loglevel = 'info'
accesslog = '-'  # 标准输出
errorlog = '-'   # 标准输出

# 绑定地址
bind = '0.0.0.0:5001'

# 进程名称
proc_name = 'model-api-service'

# 预加载应用（减少内存使用，加快启动速度）
preload_app = True