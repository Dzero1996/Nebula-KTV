"""
Celery 应用配置
连接 Redis broker，配置任务序列化和结果后端
"""
import os
from celery import Celery

# 从环境变量获取 Redis 配置
CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    "redis://localhost:6379/0"
)
CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    "redis://localhost:6379/0"
)

# 创建 Celery 应用实例
celery_app = Celery(
    "nebula_ktv",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["worker.tasks.process_song"]
)

# Celery 配置
celery_app.conf.update(
    # 任务序列化配置
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 时区配置
    timezone="Asia/Shanghai",
    enable_utc=True,
    
    # 任务执行配置
    task_track_started=True,
    task_time_limit=3600,  # 任务最大执行时间 1 小时
    task_soft_time_limit=3000,  # 软超时 50 分钟
    
    # 结果配置
    result_expires=86400,  # 结果保留 24 小时
    
    # Worker 配置
    worker_prefetch_multiplier=1,  # 每次只预取一个任务（AI 任务较重）
    worker_concurrency=2,  # 并发数（根据 NAS 性能调整）
    
    # 任务路由配置
    task_routes={
        "worker.tasks.process_song.*": {"queue": "ai_processing"},
    },
    
    # 任务默认配置
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
)

# 自动发现任务
celery_app.autodiscover_tasks(["worker.tasks"])
