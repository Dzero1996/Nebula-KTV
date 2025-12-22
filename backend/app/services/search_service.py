"""
搜索服务
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.song import Song


class SearchService:
    """搜索服务类"""
    
    @staticmethod
    async def search_songs(
        db: AsyncSession, 
        query: str,
        limit: int = 50
    ) -> List[Song]:
        """
        搜索歌曲
        
        支持：
        1. 标题模糊搜索
        2. 歌手名模糊搜索
        3. 拼音首字母搜索
        
        Args:
            db: 数据库会话
            query: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            匹配的歌曲列表
        """
        if not query:
            return []
        
        # 构建搜索条件
        search_filter = or_(
            Song.title.ilike(f"%{query}%"),
            Song.artist.ilike(f"%{query}%"),
            Song.title_abbr.ilike(f"%{query}%"),
            Song.artist_abbr.ilike(f"%{query}%")
        )
        
        stmt = select(Song).where(search_filter).limit(limit).order_by(Song.created_at.desc())
        
        result = await db.execute(stmt)
        return result.scalars().all()