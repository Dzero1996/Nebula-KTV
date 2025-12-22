"""
歌曲 CRUD API 路由
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.song import SongCreate, SongUpdate, SongResponse, JSONBFilter
from app.services.song_service import SongService

router = APIRouter(prefix="/api/songs", tags=["songs"])


@router.get("/", response_model=List[SongResponse])
async def list_songs(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    query: Optional[str] = Query(None, description="搜索关键词"),
    # JSONB 筛选参数
    bpm_min: Optional[int] = Query(None, ge=20, le=300, description="最小 BPM"),
    bpm_max: Optional[int] = Query(None, ge=20, le=300, description="最大 BPM"),
    original_key: Optional[str] = Query(None, description="原调 (e.g., 'C', 'Am')"),
    genre: Optional[str] = Query(None, description="音乐流派"),
    tags: Optional[str] = Query(None, description="场景标签，逗号分隔 (e.g., 'Wedding,Romance')"),
    difficulty_min: Optional[int] = Query(None, ge=1, le=5, description="最小难度"),
    difficulty_max: Optional[int] = Query(None, ge=1, le=5, description="最大难度"),
    language_family: Optional[str] = Query(None, description="语系"),
    meta_key: Optional[str] = Query(None, description="meta_json 中的键名"),
    meta_value: Optional[str] = Query(None, description="meta_json 中的值"),
    db: AsyncSession = Depends(get_db)
):
    """获取歌曲列表（支持分页、搜索和 JSONB 筛选）"""
    # 构建 JSONB 筛选条件
    jsonb_filter = None
    if any([bpm_min, bpm_max, original_key, genre, tags, difficulty_min, difficulty_max, 
            language_family, meta_key]):
        jsonb_filter = JSONBFilter(
            bpm_min=bpm_min,
            bpm_max=bpm_max,
            original_key=original_key,
            genre=genre,
            tags=tags.split(",") if tags else None,
            difficulty_min=difficulty_min,
            difficulty_max=difficulty_max,
            language_family=language_family,
            meta_key=meta_key,
            meta_value=meta_value
        )
    
    songs = await SongService.list_songs(db, skip=skip, limit=limit, query=query, jsonb_filter=jsonb_filter)
    return songs


@router.get("/recent", response_model=List[SongResponse])
async def get_recent_songs(
    limit: int = Query(10, ge=1, le=50, description="返回的记录数"),
    db: AsyncSession = Depends(get_db)
):
    """获取最近添加的歌曲"""
    songs = await SongService.get_recent_songs(db, limit=limit)
    return songs


@router.get("/search", response_model=List[SongResponse])
async def search_songs(
    q: str = Query(..., description="搜索关键词"),
    db: AsyncSession = Depends(get_db)
):
    """搜索歌曲"""
    songs = await SongService.search_songs(db, query=q)
    return songs


@router.get("/{song_id}", response_model=SongResponse)
async def get_song(
    song_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """获取单首歌曲详情"""
    song = await SongService.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    return song


@router.post("/", response_model=SongResponse, status_code=201)
async def create_song(
    song_data: SongCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建歌曲"""
    song = await SongService.create_song(db, song_data)
    return song


@router.patch("/{song_id}", response_model=SongResponse)
async def update_song(
    song_id: UUID,
    song_data: SongUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新歌曲"""
    song = await SongService.update_song(db, song_id, song_data)
    if not song:
        raise HTTPException(status_code=404, detail="歌曲不存在")
    return song


@router.delete("/{song_id}", status_code=204)
async def delete_song(
    song_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """删除歌曲"""
    success = await SongService.delete_song(db, song_id)
    if not success:
        raise HTTPException(status_code=404, detail="歌曲不存在")