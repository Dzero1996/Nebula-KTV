"""
歌曲处理任务
完整的 AI 处理流水线骨架
"""
import logging
import os
from typing import Dict, Any, Optional
from uuid import UUID

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded

from app.models.song import SongStatus
from app.models.media_asset import AssetType

logger = logging.getLogger(__name__)


def _generate_output_paths(song_id: str, file_path: str) -> Dict[str, str]:
    """
    根据原始文件路径生成输出文件路径
    
    Args:
        song_id: 歌曲 UUID 字符串
        file_path: 原始视频文件路径
        
    Returns:
        包含各类输出文件路径的字典
    """
    # 获取文件目录和基础名称
    base_dir = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    
    # 创建输出目录
    output_dir = os.path.join(base_dir, "processed", song_id)
    
    return {
        "video_master": file_path,  # 原始视频作为主视频
        "audio_original": os.path.join(output_dir, f"{base_name}_original.mp3"),
        "audio_inst": os.path.join(output_dir, f"{base_name}_inst.mp3"),
        "audio_vocal": os.path.join(output_dir, f"{base_name}_vocal.mp3"),
        "lyrics_vtt": os.path.join(output_dir, f"{base_name}.vtt"),
    }


def _create_media_assets(
    song_id: str,
    video_path: str,
    audio_original_path: str,
    audio_inst_path: str,
    video_metadata: Optional[Dict[str, Any]] = None,
    audio_original_metadata: Optional[Dict[str, Any]] = None,
    audio_inst_metadata: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    为处理完成的歌曲创建媒体资产记录
    
    Args:
        song_id: 歌曲 UUID 字符串
        video_path: 主视频文件路径
        audio_original_path: 原唱音轨路径
        audio_inst_path: 伴奏音轨路径
        video_metadata: 视频元数据
        audio_original_metadata: 原唱音轨元数据
        audio_inst_metadata: 伴奏音轨元数据
        
    Returns:
        创建成功返回 True，否则返回 False
    """
    from worker.db import get_db_session
    from worker.services.media_asset_service import SyncMediaAssetService
    
    try:
        with get_db_session() as db:
            assets = SyncMediaAssetService.create_media_assets_for_song(
                db=db,
                song_id=UUID(song_id),
                video_path=video_path,
                audio_original_path=audio_original_path,
                audio_inst_path=audio_inst_path,
                video_metadata=video_metadata,
                audio_original_metadata=audio_original_metadata,
                audio_inst_metadata=audio_inst_metadata,
            )
            logger.info(f"成功创建 {len(assets)} 个媒体资产记录: {song_id}")
            return True
    except Exception as e:
        logger.exception(f"创建媒体资产记录失败: {song_id}, 错误: {str(e)}")
        return False


@shared_task(
    bind=True,
    name="worker.tasks.process_song.process_song_task",
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def process_song_task(self, song_id: str, file_path: str) -> Dict[str, Any]:
    """
    完整的歌曲处理流水线:
    1. 更新状态为 PROCESSING
    2. 提取音频 (TODO)
    3. UVR5 分离人声/伴奏 (TODO)
    4. Whisper 生成歌词 (TODO)
    5. 创建媒体资产记录
    6. 更新数据库状态为 READY
    
    Args:
        song_id: 歌曲 UUID 字符串
        file_path: 原始视频文件路径
        
    Returns:
        处理结果字典
    """
    # 延迟导入，避免循环依赖
    from worker.db import get_db_session
    from app.models.song import Song
    
    logger.info(f"开始处理歌曲: {song_id}, 文件: {file_path}")
    
    try:
        # Step 1: 更新状态为 PROCESSING
        with get_db_session() as db:
            song = db.query(Song).filter(Song.id == UUID(song_id)).first()
            if not song:
                logger.error(f"歌曲不存在: {song_id}")
                return {
                    "success": False,
                    "song_id": song_id,
                    "error": "Song not found"
                }
            
            song.status = SongStatus.PROCESSING.value
            db.commit()
            logger.info(f"歌曲状态更新为 PROCESSING: {song_id}")
        
        # 生成输出文件路径
        output_paths = _generate_output_paths(song_id, file_path)
        
        # Step 2: 提取音频 (TODO: 实现 FFmpeg 音频提取)
        logger.info(f"[TODO] 提取音频: {file_path}")
        
        # Step 3: UVR5 分离人声/伴奏 (TODO: 实现 AI 音频分离)
        logger.info(f"[TODO] UVR5 音频分离: {song_id}")
        
        # Step 4: Whisper 生成歌词 (TODO: 实现 AI 歌词生成)
        logger.info(f"[TODO] Whisper 歌词生成: {song_id}")
        
        # Step 5: 创建媒体资产记录
        # 注意：在实际实现中，这里应该使用真实的文件元数据
        # 目前使用模拟的路径和元数据
        assets_created = _create_media_assets(
            song_id=song_id,
            video_path=output_paths["video_master"],
            audio_original_path=output_paths["audio_original"],
            audio_inst_path=output_paths["audio_inst"],
            video_metadata={
                "codec": "h264",
                "resolution": "1920x1080",
            },
            audio_original_metadata={
                "codec": "mp3",
                "bitrate": 320000,
            },
            audio_inst_metadata={
                "codec": "mp3",
                "bitrate": 320000,
            },
        )
        
        if not assets_created:
            logger.warning(f"媒体资产记录创建失败，但继续处理: {song_id}")
        
        # Step 6: 更新状态为 READY
        with get_db_session() as db:
            song = db.query(Song).filter(Song.id == UUID(song_id)).first()
            if song:
                song.status = SongStatus.READY.value
                db.commit()
                logger.info(f"歌曲处理完成，状态更新为 READY: {song_id}")
        
        return {
            "success": True,
            "song_id": song_id,
            "status": SongStatus.READY.value,
            "assets_created": assets_created,
            "output_paths": output_paths,
            "message": "Song processed successfully"
        }
        
    except SoftTimeLimitExceeded:
        logger.error(f"歌曲处理超时: {song_id}")
        _mark_song_failed(song_id, "Processing timeout")
        return {
            "success": False,
            "song_id": song_id,
            "error": "Processing timeout"
        }
        
    except Exception as e:
        logger.exception(f"歌曲处理失败: {song_id}, 错误: {str(e)}")
        _mark_song_failed(song_id, str(e))
        raise  # 重新抛出异常以触发重试


def _mark_song_failed(song_id: str, error_message: str) -> None:
    """
    将歌曲标记为处理失败
    
    Args:
        song_id: 歌曲 UUID 字符串
        error_message: 错误信息
    """
    from worker.db import get_db_session
    from app.models.song import Song
    
    try:
        with get_db_session() as db:
            song = db.query(Song).filter(Song.id == UUID(song_id)).first()
            if song:
                song.status = SongStatus.FAILED.value
                # 在 meta_json 中记录错误信息
                if song.meta_json is None:
                    song.meta_json = {}
                song.meta_json["error"] = error_message
                db.commit()
                logger.info(f"歌曲标记为 FAILED: {song_id}, 错误: {error_message}")
    except Exception as e:
        logger.exception(f"标记歌曲失败状态时出错: {song_id}, 错误: {str(e)}")
