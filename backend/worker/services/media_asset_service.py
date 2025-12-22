"""
媒体资产服务层 (同步版本，用于 Celery Worker)
"""
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.media_asset import MediaAsset, AssetType

logger = logging.getLogger(__name__)


class SyncMediaAssetService:
    """同步媒体资产服务类 (用于 Celery Worker)"""
    
    @staticmethod
    def get_asset(db: Session, asset_id: UUID) -> Optional[MediaAsset]:
        """获取单个媒体资产"""
        return db.query(MediaAsset).filter(MediaAsset.id == asset_id).first()
    
    @staticmethod
    def get_assets_by_song(db: Session, song_id: UUID) -> List[MediaAsset]:
        """获取歌曲的所有媒体资产"""
        return db.query(MediaAsset).filter(MediaAsset.song_id == song_id).all()
    
    @staticmethod
    def get_asset_by_song_and_type(
        db: Session, 
        song_id: UUID, 
        asset_type: AssetType
    ) -> Optional[MediaAsset]:
        """获取歌曲的特定类型媒体资产"""
        return db.query(MediaAsset).filter(
            MediaAsset.song_id == song_id,
            MediaAsset.type == asset_type.value
        ).first()
    
    @staticmethod
    def create_asset(
        db: Session,
        song_id: UUID,
        asset_type: AssetType,
        path: str,
        file_size: Optional[int] = None,
        duration: Optional[float] = None,
        codec: Optional[str] = None,
        bitrate: Optional[int] = None,
        resolution: Optional[str] = None,
    ) -> MediaAsset:
        """创建媒体资产"""
        asset = MediaAsset(
            song_id=song_id,
            type=asset_type.value,
            path=path,
            file_size=file_size,
            duration=duration,
            codec=codec,
            bitrate=bitrate,
            resolution=resolution,
        )
        db.add(asset)
        db.flush()  # 获取生成的 ID
        db.refresh(asset)
        logger.info(f"创建媒体资产: song_id={song_id}, type={asset_type.value}, path={path}")
        return asset
    
    @staticmethod
    def create_media_assets_for_song(
        db: Session,
        song_id: UUID,
        video_path: str,
        audio_original_path: str,
        audio_inst_path: str,
        video_metadata: Optional[Dict[str, Any]] = None,
        audio_original_metadata: Optional[Dict[str, Any]] = None,
        audio_inst_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[MediaAsset]:
        """
        为处理完成的歌曲创建所有必需的媒体资产记录
        
        Args:
            db: 数据库会话
            song_id: 歌曲 UUID
            video_path: 主视频文件路径
            audio_original_path: 原唱音轨路径
            audio_inst_path: 伴奏音轨路径
            video_metadata: 视频元数据 (file_size, duration, codec, bitrate, resolution)
            audio_original_metadata: 原唱音轨元数据
            audio_inst_metadata: 伴奏音轨元数据
            
        Returns:
            创建的媒体资产列表
        """
        video_metadata = video_metadata or {}
        audio_original_metadata = audio_original_metadata or {}
        audio_inst_metadata = audio_inst_metadata or {}
        
        assets = []
        
        # 创建视频资产
        video_asset = SyncMediaAssetService.create_asset(
            db=db,
            song_id=song_id,
            asset_type=AssetType.VIDEO_MASTER,
            path=video_path,
            file_size=video_metadata.get("file_size"),
            duration=video_metadata.get("duration"),
            codec=video_metadata.get("codec"),
            bitrate=video_metadata.get("bitrate"),
            resolution=video_metadata.get("resolution"),
        )
        assets.append(video_asset)
        
        # 创建原唱音轨资产
        audio_original_asset = SyncMediaAssetService.create_asset(
            db=db,
            song_id=song_id,
            asset_type=AssetType.AUDIO_ORIGINAL,
            path=audio_original_path,
            file_size=audio_original_metadata.get("file_size"),
            duration=audio_original_metadata.get("duration"),
            codec=audio_original_metadata.get("codec"),
            bitrate=audio_original_metadata.get("bitrate"),
        )
        assets.append(audio_original_asset)
        
        # 创建伴奏音轨资产
        audio_inst_asset = SyncMediaAssetService.create_asset(
            db=db,
            song_id=song_id,
            asset_type=AssetType.AUDIO_INST,
            path=audio_inst_path,
            file_size=audio_inst_metadata.get("file_size"),
            duration=audio_inst_metadata.get("duration"),
            codec=audio_inst_metadata.get("codec"),
            bitrate=audio_inst_metadata.get("bitrate"),
        )
        assets.append(audio_inst_asset)
        
        logger.info(f"为歌曲 {song_id} 创建了 {len(assets)} 个媒体资产记录")
        return assets
    
    @staticmethod
    def delete_assets_by_song(db: Session, song_id: UUID) -> int:
        """删除歌曲的所有媒体资产，返回删除数量"""
        count = db.query(MediaAsset).filter(MediaAsset.song_id == song_id).delete()
        logger.info(f"删除歌曲 {song_id} 的 {count} 个媒体资产")
        return count
    
    @staticmethod
    def has_required_assets(db: Session, song_id: UUID) -> bool:
        """
        检查歌曲是否具有所有必需的媒体资产
        必需资产: video_master, audio_original, audio_inst
        
        Args:
            db: 数据库会话
            song_id: 歌曲 UUID
            
        Returns:
            如果所有必需资产都存在则返回 True
        """
        required_types = [
            AssetType.VIDEO_MASTER.value,
            AssetType.AUDIO_ORIGINAL.value,
            AssetType.AUDIO_INST.value,
        ]
        
        existing_types = db.query(MediaAsset.type).filter(
            MediaAsset.song_id == song_id,
            MediaAsset.type.in_(required_types)
        ).all()
        
        existing_type_set = {t[0] for t in existing_types}
        return all(rt in existing_type_set for rt in required_types)
