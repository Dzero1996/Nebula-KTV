"""
歌曲数据模型 (Schema v4.0)
基于元数据构建指南的终极架构
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Numeric, BigInteger
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY, JSONB
from sqlalchemy.sql import func
from pydantic import BaseModel, Field

from app.db.database import Base


class SongStatus(str, Enum):
    """歌曲处理状态枚举"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class LanguageFamily(str, Enum):
    """语系枚举"""
    CHINESE = "Chinese"
    ENGLISH = "English"
    JAPANESE = "Japanese"
    KOREAN = "Korean"
    OTHER = "Other"


class LanguageDialect(str, Enum):
    """方言枚举"""
    MANDARIN = "Mandarin"
    CANTONESE = "Cantonese"
    HOKKIEN = "Hokkien"
    OTHER = "Other"


class SingingType(str, Enum):
    """演唱形式枚举"""
    SOLO = "Solo"
    DUET = "Duet"
    GROUP = "Group"
    CHOIR = "Choir"


class GenderType(str, Enum):
    """性别类型枚举"""
    MALE = "Male"
    FEMALE = "Female"
    MIX = "Mix"
    BAND = "Band"


class Genre(str, Enum):
    """音乐流派枚举"""
    POP = "Pop"
    ROCK = "Rock"
    RNB = "R&B"
    BALLAD = "Ballad"
    EDM = "EDM"
    JAZZ = "Jazz"
    CLASSICAL = "Classical"
    HIPHOP = "HipHop"
    FOLK = "Folk"
    OTHER = "Other"


class QualityBadge(str, Enum):
    """画质标签枚举"""
    QUALITY_4K = "4K"
    HD = "HD"
    SD = "SD"


class Song(Base):
    """歌曲 SQLAlchemy 模型"""
    __tablename__ = "songs"

    # 1. 基础身份信息
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(Text, nullable=False)
    subtitle = Column(Text, nullable=True)
    artist = Column(Text, nullable=False)
    album = Column(Text, nullable=True)
    year = Column(Integer, nullable=True)
    cover_path = Column(Text, nullable=True)
    
    # 2. 创作与版权信息
    lyricist = Column(Text, nullable=True)
    composer = Column(Text, nullable=True)
    arranger = Column(Text, nullable=True)
    publisher = Column(Text, nullable=True)
    
    # 3. KTV 业务分类
    language_family = Column(String(20), nullable=True)
    language_dialect = Column(String(20), nullable=True)
    singing_type = Column(String(20), nullable=True)
    gender_type = Column(String(20), nullable=True)
    genre = Column(String(30), nullable=True)
    scenario = Column(JSONB, nullable=True)
    
    # 4. 搜索优化
    title_pinyin = Column(Text, nullable=True)
    title_abbr = Column(String(50), nullable=True)
    artist_pinyin = Column(Text, nullable=True)
    artist_abbr = Column(String(50), nullable=True)
    aliases = Column(JSONB, nullable=True)
    
    # 5. AI 音频指纹
    duration = Column(Integer, nullable=True)
    bpm = Column(Integer, nullable=True)
    original_key = Column(String(10), nullable=True)
    camelot_key = Column(String(5), nullable=True)
    energy = Column(Numeric(3, 2), nullable=True)
    danceability = Column(Numeric(3, 2), nullable=True)
    valence = Column(Numeric(3, 2), nullable=True)
    vocal_range_low = Column(String(5), nullable=True)
    vocal_range_high = Column(String(5), nullable=True)
    difficulty_level = Column(Integer, nullable=True)
    feature_vector = Column(ARRAY(Numeric), nullable=True)
    
    # 6. 状态与运营
    status = Column(String(20), default=SongStatus.PENDING.value)
    play_count = Column(Integer, default=0)
    last_played_at = Column(DateTime(timezone=True), nullable=True)
    is_favorite = Column(Boolean, default=False)
    quality_badge = Column(String(10), nullable=True)
    meta_json = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# ============================================
# Pydantic Schemas
# ============================================

class SongBase(BaseModel):
    """歌曲基础 Schema"""
    # 基础信息
    title: str = Field(..., min_length=1, max_length=500)
    artist: str = Field(..., min_length=1, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=500)
    album: Optional[str] = Field(None, max_length=200)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    cover_path: Optional[str] = None
    
    # 创作信息
    lyricist: Optional[str] = Field(None, max_length=200)
    composer: Optional[str] = Field(None, max_length=200)
    arranger: Optional[str] = Field(None, max_length=200)
    publisher: Optional[str] = Field(None, max_length=200)
    
    # 分类信息
    language_family: Optional[str] = Field(None, max_length=20)
    language_dialect: Optional[str] = Field(None, max_length=20)
    singing_type: Optional[str] = Field(None, max_length=20)
    gender_type: Optional[str] = Field(None, max_length=20)
    genre: Optional[str] = Field(None, max_length=30)
    scenario: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    
    # 兜底字段
    meta_json: Dict[str, Any] = Field(default_factory=dict)


class SongCreate(SongBase):
    """创建歌曲 Schema"""
    pass


class SongUpdate(BaseModel):
    """更新歌曲 Schema"""
    # 基础信息
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    artist: Optional[str] = Field(None, min_length=1, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=500)
    album: Optional[str] = Field(None, max_length=200)
    year: Optional[int] = Field(None, ge=1900, le=2100)
    cover_path: Optional[str] = None
    
    # 创作信息
    lyricist: Optional[str] = Field(None, max_length=200)
    composer: Optional[str] = Field(None, max_length=200)
    arranger: Optional[str] = Field(None, max_length=200)
    publisher: Optional[str] = Field(None, max_length=200)
    
    # 分类信息
    language_family: Optional[str] = Field(None, max_length=20)
    language_dialect: Optional[str] = Field(None, max_length=20)
    singing_type: Optional[str] = Field(None, max_length=20)
    gender_type: Optional[str] = Field(None, max_length=20)
    genre: Optional[str] = Field(None, max_length=30)
    scenario: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    
    # AI 音频指纹
    duration: Optional[int] = Field(None, ge=0)
    bpm: Optional[int] = Field(None, ge=20, le=300)
    original_key: Optional[str] = Field(None, max_length=10)
    camelot_key: Optional[str] = Field(None, max_length=5)
    energy: Optional[float] = Field(None, ge=0.0, le=1.0)
    danceability: Optional[float] = Field(None, ge=0.0, le=1.0)
    valence: Optional[float] = Field(None, ge=0.0, le=1.0)
    vocal_range_low: Optional[str] = Field(None, max_length=5)
    vocal_range_high: Optional[str] = Field(None, max_length=5)
    difficulty_level: Optional[int] = Field(None, ge=1, le=5)
    feature_vector: Optional[List[float]] = None
    
    # 状态与运营
    status: Optional[SongStatus] = None
    is_favorite: Optional[bool] = None
    quality_badge: Optional[str] = Field(None, max_length=10)
    meta_json: Optional[Dict[str, Any]] = None


class JSONBFilter(BaseModel):
    """JSONB 筛选条件 Schema"""
    bpm_min: Optional[int] = Field(None, ge=20, le=300, description="最小 BPM")
    bpm_max: Optional[int] = Field(None, ge=20, le=300, description="最大 BPM")
    original_key: Optional[str] = Field(None, max_length=10, description="原调")
    genre: Optional[str] = Field(None, max_length=30, description="音乐流派")
    tags: Optional[List[str]] = Field(None, description="场景标签列表")
    difficulty_min: Optional[int] = Field(None, ge=1, le=5, description="最小难度")
    difficulty_max: Optional[int] = Field(None, ge=1, le=5, description="最大难度")
    language_family: Optional[str] = Field(None, max_length=20, description="语系")
    meta_key: Optional[str] = Field(None, description="meta_json 中的键名")
    meta_value: Optional[str] = Field(None, description="meta_json 中的值")


class SongResponse(BaseModel):
    """歌曲响应 Schema"""
    # 基础信息
    id: UUID
    title: str
    artist: str
    subtitle: Optional[str] = None
    album: Optional[str] = None
    year: Optional[int] = None
    cover_path: Optional[str] = None
    
    # 创作信息
    lyricist: Optional[str] = None
    composer: Optional[str] = None
    arranger: Optional[str] = None
    publisher: Optional[str] = None
    
    # 分类信息
    language_family: Optional[str] = None
    language_dialect: Optional[str] = None
    singing_type: Optional[str] = None
    gender_type: Optional[str] = None
    genre: Optional[str] = None
    scenario: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    
    # 搜索优化
    title_pinyin: Optional[str] = None
    title_abbr: Optional[str] = None
    artist_pinyin: Optional[str] = None
    artist_abbr: Optional[str] = None
    
    # AI 音频指纹
    duration: Optional[int] = None
    bpm: Optional[int] = None
    original_key: Optional[str] = None
    camelot_key: Optional[str] = None
    energy: Optional[float] = None
    danceability: Optional[float] = None
    valence: Optional[float] = None
    vocal_range_low: Optional[str] = None
    vocal_range_high: Optional[str] = None
    difficulty_level: Optional[int] = None
    feature_vector: Optional[List[float]] = None
    
    # 状态与运营
    status: SongStatus
    play_count: int = 0
    last_played_at: Optional[datetime] = None
    is_favorite: bool = False
    quality_badge: Optional[str] = None
    meta_json: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
