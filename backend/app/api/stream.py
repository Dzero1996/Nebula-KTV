"""
媒体流 API 路由
支持 HTTP Range Requests 协议，用于视频和音频流式传输
"""
import os
import re
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.media_asset import MediaAsset, MediaAssetResponse, AssetType
from app.services.media_asset_service import MediaAssetService

router = APIRouter(prefix="/api/stream", tags=["stream"])

# 媒体文件存储根目录
MEDIA_ROOT = os.getenv("MEDIA_ROOT", "/data/media")

# MIME 类型映射
MIME_TYPES = {
    # 视频格式
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mkv": "video/x-matroska",
    ".avi": "video/x-msvideo",
    ".mov": "video/quicktime",
    # 音频格式
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".flac": "audio/flac",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
    ".m4a": "audio/mp4",
}


def get_content_type(file_path: str) -> str:
    """根据文件扩展名获取 Content-Type"""
    ext = os.path.splitext(file_path)[1].lower()
    return MIME_TYPES.get(ext, "application/octet-stream")


def parse_range_header(range_header: str, file_size: int) -> tuple[int, int]:
    """
    解析 HTTP Range 请求头
    
    Args:
        range_header: Range 请求头值，格式如 "bytes=0-1023"
        file_size: 文件总大小
        
    Returns:
        (start, end) 字节范围元组
        
    Raises:
        ValueError: 无效的 Range 格式
    """
    # 匹配 "bytes=start-end" 格式
    match = re.match(r"bytes=(\d*)-(\d*)", range_header)
    if not match:
        raise ValueError(f"Invalid Range header format: {range_header}")
    
    start_str, end_str = match.groups()
    
    if start_str == "" and end_str == "":
        raise ValueError("Both start and end cannot be empty")
    
    if start_str == "":
        # 格式: bytes=-500 (最后 500 字节)
        suffix_length = int(end_str)
        start = max(0, file_size - suffix_length)
        end = file_size - 1
    elif end_str == "":
        # 格式: bytes=500- (从 500 到文件末尾)
        start = int(start_str)
        end = file_size - 1
    else:
        # 格式: bytes=0-1023
        start = int(start_str)
        end = int(end_str)
    
    # 验证范围有效性
    if start < 0:
        start = 0
    if end >= file_size:
        end = file_size - 1
    if start > end:
        raise ValueError(f"Invalid range: start ({start}) > end ({end})")
    
    return start, end


def file_iterator(file_path: str, start: int, end: int, chunk_size: int = 8192):
    """
    文件分块迭代器，用于流式传输
    
    Args:
        file_path: 文件路径
        start: 起始字节位置
        end: 结束字节位置
        chunk_size: 每次读取的块大小
        
    Yields:
        文件数据块
    """
    with open(file_path, "rb") as f:
        f.seek(start)
        remaining = end - start + 1
        
        while remaining > 0:
            read_size = min(chunk_size, remaining)
            data = f.read(read_size)
            if not data:
                break
            remaining -= len(data)
            yield data


async def get_media_asset(db: AsyncSession, asset_id: UUID) -> Optional[MediaAsset]:
    """从数据库获取媒体资产记录"""
    result = await db.execute(
        select(MediaAsset).where(MediaAsset.id == asset_id)
    )
    return result.scalar_one_or_none()


@router.get("/{asset_id}")
async def stream_media(
    asset_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    流式传输媒体资产
    
    支持 HTTP Range Requests 协议，允许客户端请求文件的特定字节范围。
    这对于视频/音频播放器的跳转功能至关重要。
    
    Args:
        asset_id: 媒体资产 UUID
        request: FastAPI Request 对象，用于获取 Range 头
        db: 数据库会话
        
    Returns:
        StreamingResponse: 流式响应
        
    Raises:
        HTTPException: 404 资产不存在，416 Range 无效
    """
    # 1. 从数据库获取媒体资产信息
    asset = await get_media_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="媒体资产不存在")
    
    # 2. 构建完整文件路径
    file_path = os.path.join(MEDIA_ROOT, asset.path)
    
    # 3. 检查文件是否存在
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="媒体文件不存在")
    
    # 4. 获取文件大小和 Content-Type
    file_size = os.path.getsize(file_path)
    content_type = get_content_type(file_path)
    
    # 5. 解析 Range 请求头
    range_header = request.headers.get("Range")
    
    if range_header:
        try:
            start, end = parse_range_header(range_header, file_size)
        except ValueError as e:
            raise HTTPException(
                status_code=416,
                detail=str(e),
                headers={"Content-Range": f"bytes */{file_size}"}
            )
        
        # 返回 206 Partial Content
        content_length = end - start + 1
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Type": content_type,
        }
        
        return StreamingResponse(
            file_iterator(file_path, start, end),
            status_code=206,
            headers=headers,
            media_type=content_type
        )
    else:
        # 无 Range 头，返回完整文件
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Content-Type": content_type,
        }
        
        return StreamingResponse(
            file_iterator(file_path, 0, file_size - 1),
            status_code=200,
            headers=headers,
            media_type=content_type
        )


@router.head("/{asset_id}")
async def head_media(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    获取媒体资产元信息（不返回内容）
    
    用于客户端预检文件大小和类型
    """
    asset = await get_media_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="媒体资产不存在")
    
    file_path = os.path.join(MEDIA_ROOT, asset.path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="媒体文件不存在")
    
    file_size = os.path.getsize(file_path)
    content_type = get_content_type(file_path)
    
    return Response(
        content=b"",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(file_size),
            "Content-Type": content_type,
        }
    )


# ============================================
# 媒体资产查询 API
# ============================================

@router.get("/song/{song_id}/assets", response_model=list[MediaAssetResponse])
async def get_song_assets(
    song_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    获取歌曲的所有媒体资产
    
    Args:
        song_id: 歌曲 UUID
        db: 数据库会话
        
    Returns:
        媒体资产列表
    """
    assets = await MediaAssetService.get_assets_by_song(db, song_id)
    return assets


@router.get("/song/{song_id}/video", response_model=MediaAssetResponse)
async def get_song_video(
    song_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    获取歌曲的主视频资产
    
    Args:
        song_id: 歌曲 UUID
        db: 数据库会话
        
    Returns:
        视频媒体资产
        
    Raises:
        HTTPException: 404 视频资产不存在
    """
    asset = await MediaAssetService.get_asset_by_song_and_type(
        db, song_id, AssetType.VIDEO_MASTER
    )
    if not asset:
        raise HTTPException(status_code=404, detail="视频资产不存在")
    return asset


@router.get("/song/{song_id}/audio/original", response_model=MediaAssetResponse)
async def get_song_original_audio(
    song_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    获取歌曲的原唱音轨资产
    
    Args:
        song_id: 歌曲 UUID
        db: 数据库会话
        
    Returns:
        原唱音轨媒体资产
        
    Raises:
        HTTPException: 404 原唱音轨不存在
    """
    asset = await MediaAssetService.get_asset_by_song_and_type(
        db, song_id, AssetType.AUDIO_ORIGINAL
    )
    if not asset:
        raise HTTPException(status_code=404, detail="原唱音轨不存在")
    return asset


@router.get("/song/{song_id}/audio/instrumental", response_model=MediaAssetResponse)
async def get_song_instrumental_audio(
    song_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    获取歌曲的伴奏音轨资产
    
    Args:
        song_id: 歌曲 UUID
        db: 数据库会话
        
    Returns:
        伴奏音轨媒体资产
        
    Raises:
        HTTPException: 404 伴奏音轨不存在
    """
    asset = await MediaAssetService.get_asset_by_song_and_type(
        db, song_id, AssetType.AUDIO_INST
    )
    if not asset:
        raise HTTPException(status_code=404, detail="伴奏音轨不存在")
    return asset


@router.get("/asset/{asset_id}/info", response_model=MediaAssetResponse)
async def get_asset_info(
    asset_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    获取媒体资产详细信息（不流式传输）
    
    Args:
        asset_id: 媒体资产 UUID
        db: 数据库会话
        
    Returns:
        媒体资产详细信息
        
    Raises:
        HTTPException: 404 资产不存在
    """
    asset = await MediaAssetService.get_asset(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="媒体资产不存在")
    return asset
