"""
歌曲业务逻辑服务
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from app.models.song import Song, SongCreate, SongUpdate, SongResponse, JSONBFilter
from app.utils.pinyin_utils import to_pinyin_abbr
from app.services.search_service import SearchService


class SongService:
    """歌曲服务类"""
    
    @staticmethod
    async def create_song(db: AsyncSession, data: SongCreate) -> Song:
        """创建歌曲"""
        # 生成拼音首字母
        title_abbr = to_pinyin_abbr(data.title)
        artist_abbr = to_pinyin_abbr(data.artist)
        
        song = Song(
            title=data.title,
            artist=data.artist,
            meta_json=data.meta_json,
            title_abbr=title_abbr,
            artist_abbr=artist_abbr,
            # 可选字段
            subtitle=data.subtitle,
            album=data.album,
            year=data.year,
            cover_path=data.cover_path,
            lyricist=data.lyricist,
            composer=data.composer,
            arranger=data.arranger,
            publisher=data.publisher,
            language_family=data.language_family,
            language_dialect=data.language_dialect,
            singing_type=data.singing_type,
            gender_type=data.gender_type,
            genre=data.genre,
            scenario=data.scenario,
            aliases=data.aliases,
        )
        
        db.add(song)
        await db.commit()
        await db.refresh(song)
        return song
    
    @staticmethod
    async def get_song(db: AsyncSession, song_id: UUID) -> Optional[Song]:
        """获取单首歌曲"""
        result = await db.execute(
            select(Song).where(Song.id == song_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    def build_jsonb_filters(jsonb_filter: JSONBFilter) -> List:
        """
        构建 JSONB 筛选条件
        
        支持的筛选：
        - BPM 范围筛选
        - 原调筛选
        - 流派筛选
        - 场景标签筛选 (JSONB @> 操作符)
        - 难度范围筛选
        - 语系筛选
        - meta_json 自定义键值筛选
        """
        filters = []
        
        # BPM 范围筛选
        if jsonb_filter.bpm_min is not None:
            filters.append(Song.bpm >= jsonb_filter.bpm_min)
        if jsonb_filter.bpm_max is not None:
            filters.append(Song.bpm <= jsonb_filter.bpm_max)
        
        # 原调筛选
        if jsonb_filter.original_key is not None:
            filters.append(Song.original_key == jsonb_filter.original_key)
        
        # 流派筛选
        if jsonb_filter.genre is not None:
            filters.append(Song.genre == jsonb_filter.genre)
        
        # 场景标签筛选 (使用 JSONB @> 操作符检查数组包含)
        if jsonb_filter.tags:
            for tag in jsonb_filter.tags:
                # 使用 PostgreSQL JSONB @> 操作符检查 scenario 数组是否包含该标签
                filters.append(Song.scenario.contains([tag]))
        
        # 难度范围筛选
        if jsonb_filter.difficulty_min is not None:
            filters.append(Song.difficulty_level >= jsonb_filter.difficulty_min)
        if jsonb_filter.difficulty_max is not None:
            filters.append(Song.difficulty_level <= jsonb_filter.difficulty_max)
        
        # 语系筛选
        if jsonb_filter.language_family is not None:
            filters.append(Song.language_family == jsonb_filter.language_family)
        
        # meta_json 自定义键值筛选
        if jsonb_filter.meta_key is not None:
            if jsonb_filter.meta_value is not None:
                # 使用 JSONB ->> 操作符获取文本值并比较
                filters.append(Song.meta_json[jsonb_filter.meta_key].astext == jsonb_filter.meta_value)
            else:
                # 仅检查键是否存在
                filters.append(Song.meta_json.has_key(jsonb_filter.meta_key))
        
        return filters
    
    @staticmethod
    async def list_songs(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 20, 
        query: Optional[str] = None,
        jsonb_filter: Optional[JSONBFilter] = None
    ) -> List[Song]:
        """获取歌曲列表（支持 JSONB 筛选）"""
        stmt = select(Song)
        
        # 添加搜索条件
        if query:
            search_filter = or_(
                Song.title.ilike(f"%{query}%"),
                Song.artist.ilike(f"%{query}%"),
                Song.title_abbr.ilike(f"%{query}%"),
                Song.artist_abbr.ilike(f"%{query}%")
            )
            stmt = stmt.where(search_filter)
        
        # 添加 JSONB 筛选条件
        if jsonb_filter:
            filters = SongService.build_jsonb_filters(jsonb_filter)
            if filters:
                stmt = stmt.where(and_(*filters))
        
        # 添加分页
        stmt = stmt.offset(skip).limit(limit).order_by(Song.created_at.desc())
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def update_song(db: AsyncSession, song_id: UUID, data: SongUpdate) -> Optional[Song]:
        """更新歌曲"""
        song = await SongService.get_song(db, song_id)
        if not song:
            return None
        
        # 更新字段
        update_data = data.model_dump(exclude_unset=True)
        
        # 如果更新了标题或歌手，重新生成拼音首字母
        if "title" in update_data:
            update_data["title_abbr"] = to_pinyin_abbr(update_data["title"])
        if "artist" in update_data:
            update_data["artist_abbr"] = to_pinyin_abbr(update_data["artist"])
        
        for field, value in update_data.items():
            setattr(song, field, value)
        
        await db.commit()
        await db.refresh(song)
        return song
    
    @staticmethod
    async def delete_song(db: AsyncSession, song_id: UUID) -> bool:
        """删除歌曲"""
        song = await SongService.get_song(db, song_id)
        if not song:
            return False
        
        await db.delete(song)
        await db.commit()
        return True
    
    @staticmethod
    async def get_recent_songs(db: AsyncSession, limit: int = 10) -> List[Song]:
        """获取最近添加的歌曲"""
        stmt = select(Song).order_by(Song.created_at.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def search_songs(db: AsyncSession, query: str) -> List[Song]:
        """搜索歌曲"""
        return await SearchService.search_songs(db, query)