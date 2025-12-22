"""
媒体资产数据模型 (Schema v4.0)
支持极高清画质和无损音质
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Text, BigInteger, Integer, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.sql import func
from pydantic import BaseModel, Field

from app.db.database import Base


class AssetType(str, Enum):
    """媒体资产类型枚举"""
    VIDEO_MASTER = "video_master"           # 主视频文件
    AUDIO_ORIGINAL = "audio_original"       # 原版立体声 (无损/高码率)
    AUDIO_INST = "audio_inst"               # AI 分离的伴奏
    AUDIO_VOCAL = "audio_vocal"             # AI 分离的人声 (用于评分/练习)
    LYRICS_VTT = "lyrics_vtt"               # 时间轴歌词
    LYRICS_WORD_LEVEL = "lyrics_word_level" # 逐字对齐歌词 (JSON)
    WAVEFORM_JSON = "waveform_json"         # 音频波形数据


class MediaAsset(Base):
    """媒体资产 SQLAlchemy 模型"""
    __tablename__ = "media_assets"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    song_id = Column(PG_UUID(as_uuid=True), nullable=False)
    type = Column(String(30), nullable=False)
    path = Column(Text, nullable=False)
    
    # 技术元数据
    file_size = Column(BigInteger, nullable=True)       # 字节
    duration = Column(Numeric(10, 2), nullable=True)    # 精确时长
    codec = Column(String(20), nullable=True)           # 'h264', 'hevc', 'aac', 'flac'
    bitrate = Column(Integer, nullable=True)            # 320000 (320kbps)
    resolution = Column(String(20), nullable=True)      # '1920x1080' (仅视频)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ============================================
# Pydantic Schemas
# ============================================

class MediaAssetBase(BaseModel):
    """媒体资产基础 Schema"""
    song_id: UUID
    type: AssetType
    path: str = Field(..., min_length=1)
    
    # 技术元数据
    file_size: Optional[int] = Field(None, ge=0)
    duration: Optional[float] = Field(None, ge=0)
    codec: Optional[str] = Field(None, max_length=20)
    bitrate: Optional[int] = Field(None, ge=0)
    resolution: Optional[str] = Field(None, max_length=20)


class MediaAssetCreate(MediaAssetBase):
    """创建媒体资产 Schema"""
    pass


class MediaAssetUpdate(BaseModel):
    """更新媒体资产 Schema"""
    path: Optional[str] = Field(None, min_length=1)
    file_size: Optional[int] = Field(None, ge=0)
    duration: Optional[float] = Field(None, ge=0)
    codec: Optional[str] = Field(None, max_length=20)
    bitrate: Optional[int] = Field(None, ge=0)
    resolution: Optional[str] = Field(None, max_length=20)


class MediaAssetResponse(MediaAssetBase):
    """媒体资产响应 Schema"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
