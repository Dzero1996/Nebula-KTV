"""
媒体资产服务层
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.media_asset import MediaAsset, MediaAssetCreate, AssetType


class MediaAssetService:
    """媒体资产服务类"""
    
    @staticmethod
    async def get_asset(db: AsyncSession, asset_id: UUID) -> Optional[MediaAsset]:
        """获取单个媒体资产"""
        result = await db.execute(
            select(MediaAsset).where(MediaAsset.id == asset_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_assets_by_song(db: AsyncSession, song_id: UUID) -> List[MediaAsset]:
        """获取歌曲的所有媒体资产"""
        result = await db.execute(
            select(MediaAsset).where(MediaAsset.song_id == song_id)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_asset_by_song_and_type(
        db: AsyncSession, 
        song_id: UUID, 
        asset_type: AssetType
    ) -> Optional[MediaAsset]:
        """获取歌曲的特定类型媒体资产"""
        result = await db.execute(
            select(MediaAsset).where(
                MediaAsset.song_id == song_id,
                MediaAsset.type == asset_type.value
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_asset(db: AsyncSession, asset_data: MediaAssetCreate) -> MediaAsset:
        """创建媒体资产"""
        asset = MediaAsset(
            song_id=asset_data.song_id,
            type=asset_data.type.value,
            path=asset_data.path,
            file_size=asset_data.file_size,
            duration=asset_data.duration,
            codec=asset_data.codec,
            bitrate=asset_data.bitrate,
            resolution=asset_data.resolution,
        )
        db.add(asset)
        await db.commit()
        await db.refresh(asset)
        return asset
    
    @staticmethod
    async def delete_asset(db: AsyncSession, asset_id: UUID) -> bool:
        """删除媒体资产"""
        asset = await MediaAssetService.get_asset(db, asset_id)
        if not asset:
            return False
        await db.delete(asset)
        await db.commit()
        return True
    
    @staticmethod
    async def delete_assets_by_song(db: AsyncSession, song_id: UUID) -> int:
        """删除歌曲的所有媒体资产，返回删除数量"""
        assets = await MediaAssetService.get_assets_by_song(db, song_id)
        count = len(assets)
        for asset in assets:
            await db.delete(asset)
        await db.commit()
        return count
