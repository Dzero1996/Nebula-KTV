"""
Celery 任务模块
"""
from worker.tasks.process_song import process_song_task

__all__ = ["process_song_task"]
