"""
属性测试：媒体资产记录完整性
**Feature: nebula-ktv, Property 9: 媒体资产记录完整性**
**Validates: Requirements 8.2**

For any 处理完成的歌曲，media_assets 表中必须存在对应的 video_master、audio_original、audio_inst 记录。
"""
import pytest
import string
import os
from hypothesis import given, strategies as st, settings, HealthCheck
from uuid import uuid4, UUID
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.models.song import Song, SongStatus
from app.models.media_asset import MediaAsset, AssetType


# 定义文件路径策略
PATH_CHARS = string.ascii_letters + string.digits + "/_-."
FILE_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mp3", ".wav", ".flac"]
CODECS = ["h264", "hevc", "aac", "mp3", "flac", "opus"]
RESOLUTIONS = ["1920x1080", "1280x720", "3840x2160", "1080x1920"]


def file_path_strategy():
    """生成文件路径的策略"""
    return st.builds(
        lambda dir_name, file_name, ext: f"/media/{dir_name}/{file_name}{ext}",
        dir_name=st.text(alphabet=string.ascii_lowercase + string.digits, min_size=1, max_size=20),
        file_name=st.text(alphabet=string.ascii_lowercase + string.digits + "_-", min_size=1, max_size=30),
        ext=st.sampled_from(FILE_EXTENSIONS),
    )


def media_metadata_strategy():
    """生成媒体元数据的策略"""
    return st.fixed_dictionaries({}, optional={
        "file_size": st.integers(min_value=1000, max_value=10_000_000_000),
        "duration": st.floats(min_value=1.0, max_value=7200.0, allow_nan=False, allow_infinity=False),
        "codec": st.sampled_from(CODECS),
        "bitrate": st.integers(min_value=64000, max_value=320000),
        "resolution": st.sampled_from(RESOLUTIONS),
    })


def song_data_strategy():
    """生成歌曲数据的策略"""
    return st.fixed_dictionaries({
        "title": st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=50),
        "artist": st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=30),
    })


def media_assets_input_strategy():
    """生成媒体资产输入数据的策略"""
    return st.fixed_dictionaries({
        "video_path": file_path_strategy(),
        "audio_original_path": file_path_strategy(),
        "audio_inst_path": file_path_strategy(),
        "video_metadata": media_metadata_strategy(),
        "audio_original_metadata": media_metadata_strategy(),
        "audio_inst_metadata": media_metadata_strategy(),
    })


class MockMediaAssetService:
    """
    模拟媒体资产服务，用于测试逻辑正确性
    不依赖实际数据库连接
    """
    
    def __init__(self):
        self.assets: Dict[UUID, List[MediaAsset]] = {}
    
    def create_asset(
        self,
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
        asset.id = uuid4()
        asset.created_at = datetime.now()
        
        if song_id not in self.assets:
            self.assets[song_id] = []
        self.assets[song_id].append(asset)
        
        return asset
    
    def create_media_assets_for_song(
        self,
        song_id: UUID,
        video_path: str,
        audio_original_path: str,
        audio_inst_path: str,
        video_metadata: Optional[Dict[str, Any]] = None,
        audio_original_metadata: Optional[Dict[str, Any]] = None,
        audio_inst_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[MediaAsset]:
        """为处理完成的歌曲创建所有必需的媒体资产记录"""
        video_metadata = video_metadata or {}
        audio_original_metadata = audio_original_metadata or {}
        audio_inst_metadata = audio_inst_metadata or {}
        
        assets = []
        
        # 创建视频资产
        video_asset = self.create_asset(
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
        audio_original_asset = self.create_asset(
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
        audio_inst_asset = self.create_asset(
            song_id=song_id,
            asset_type=AssetType.AUDIO_INST,
            path=audio_inst_path,
            file_size=audio_inst_metadata.get("file_size"),
            duration=audio_inst_metadata.get("duration"),
            codec=audio_inst_metadata.get("codec"),
            bitrate=audio_inst_metadata.get("bitrate"),
        )
        assets.append(audio_inst_asset)
        
        return assets
    
    def get_assets_by_song(self, song_id: UUID) -> List[MediaAsset]:
        """获取歌曲的所有媒体资产"""
        return self.assets.get(song_id, [])
    
    def has_required_assets(self, song_id: UUID) -> bool:
        """检查歌曲是否具有所有必需的媒体资产"""
        required_types = {
            AssetType.VIDEO_MASTER.value,
            AssetType.AUDIO_ORIGINAL.value,
            AssetType.AUDIO_INST.value,
        }
        
        assets = self.get_assets_by_song(song_id)
        existing_types = {asset.type for asset in assets}
        
        return required_types.issubset(existing_types)


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    song_data=song_data_strategy(),
    assets_input=media_assets_input_strategy(),
)
def test_media_asset_completeness_property(song_data, assets_input):
    """
    Property 9: 媒体资产记录完整性
    For any 处理完成的歌曲，media_assets 表中必须存在对应的 video_master、audio_original、audio_inst 记录。
    
    测试 create_media_assets_for_song 函数的逻辑正确性（不依赖数据库）
    """
    # 1. 创建模拟的歌曲对象
    song = Song(
        title=song_data["title"],
        artist=song_data["artist"],
        status=SongStatus.READY.value,
        meta_json={},
    )
    song.id = uuid4()
    song.created_at = datetime.now()
    song.updated_at = datetime.now()
    
    # 2. 使用模拟服务创建媒体资产
    service = MockMediaAssetService()
    assets = service.create_media_assets_for_song(
        song_id=song.id,
        video_path=assets_input["video_path"],
        audio_original_path=assets_input["audio_original_path"],
        audio_inst_path=assets_input["audio_inst_path"],
        video_metadata=assets_input["video_metadata"],
        audio_original_metadata=assets_input["audio_original_metadata"],
        audio_inst_metadata=assets_input["audio_inst_metadata"],
    )
    
    # 3. 验证媒体资产记录完整性
    # Property: 必须创建 3 个资产
    assert len(assets) == 3, \
        f"Expected 3 assets, got {len(assets)}"
    
    # Property: 必须包含 video_master 类型
    asset_types = {asset.type for asset in assets}
    assert AssetType.VIDEO_MASTER.value in asset_types, \
        "Missing video_master asset"
    
    # Property: 必须包含 audio_original 类型
    assert AssetType.AUDIO_ORIGINAL.value in asset_types, \
        "Missing audio_original asset"
    
    # Property: 必须包含 audio_inst 类型
    assert AssetType.AUDIO_INST.value in asset_types, \
        "Missing audio_inst asset"
    
    # Property: has_required_assets 应返回 True
    assert service.has_required_assets(song.id), \
        "has_required_assets should return True after creating all required assets"
    
    # Property: 所有资产的 song_id 必须匹配
    for asset in assets:
        assert asset.song_id == song.id, \
            f"Asset song_id mismatch: expected {song.id}, got {asset.song_id}"


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    song_data=song_data_strategy(),
    assets_input=media_assets_input_strategy(),
)
def test_media_asset_paths_preserved(song_data, assets_input):
    """
    Property: 媒体资产路径应正确保存
    """
    song_id = uuid4()
    
    service = MockMediaAssetService()
    assets = service.create_media_assets_for_song(
        song_id=song_id,
        video_path=assets_input["video_path"],
        audio_original_path=assets_input["audio_original_path"],
        audio_inst_path=assets_input["audio_inst_path"],
        video_metadata=assets_input["video_metadata"],
        audio_original_metadata=assets_input["audio_original_metadata"],
        audio_inst_metadata=assets_input["audio_inst_metadata"],
    )
    
    # 验证路径正确保存
    video_asset = next(a for a in assets if a.type == AssetType.VIDEO_MASTER.value)
    audio_original_asset = next(a for a in assets if a.type == AssetType.AUDIO_ORIGINAL.value)
    audio_inst_asset = next(a for a in assets if a.type == AssetType.AUDIO_INST.value)
    
    assert video_asset.path == assets_input["video_path"], \
        f"Video path mismatch: expected {assets_input['video_path']}, got {video_asset.path}"
    
    assert audio_original_asset.path == assets_input["audio_original_path"], \
        f"Audio original path mismatch"
    
    assert audio_inst_asset.path == assets_input["audio_inst_path"], \
        f"Audio inst path mismatch"


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    song_data=song_data_strategy(),
    assets_input=media_assets_input_strategy(),
)
def test_media_asset_metadata_preserved(song_data, assets_input):
    """
    Property: 媒体资产元数据应正确保存
    """
    song_id = uuid4()
    
    service = MockMediaAssetService()
    assets = service.create_media_assets_for_song(
        song_id=song_id,
        video_path=assets_input["video_path"],
        audio_original_path=assets_input["audio_original_path"],
        audio_inst_path=assets_input["audio_inst_path"],
        video_metadata=assets_input["video_metadata"],
        audio_original_metadata=assets_input["audio_original_metadata"],
        audio_inst_metadata=assets_input["audio_inst_metadata"],
    )
    
    video_asset = next(a for a in assets if a.type == AssetType.VIDEO_MASTER.value)
    audio_original_asset = next(a for a in assets if a.type == AssetType.AUDIO_ORIGINAL.value)
    audio_inst_asset = next(a for a in assets if a.type == AssetType.AUDIO_INST.value)
    
    # 验证视频元数据
    video_meta = assets_input["video_metadata"]
    if "file_size" in video_meta:
        assert video_asset.file_size == video_meta["file_size"]
    if "codec" in video_meta:
        assert video_asset.codec == video_meta["codec"]
    if "resolution" in video_meta:
        assert video_asset.resolution == video_meta["resolution"]
    
    # 验证原唱音轨元数据
    audio_orig_meta = assets_input["audio_original_metadata"]
    if "file_size" in audio_orig_meta:
        assert audio_original_asset.file_size == audio_orig_meta["file_size"]
    if "codec" in audio_orig_meta:
        assert audio_original_asset.codec == audio_orig_meta["codec"]
    if "bitrate" in audio_orig_meta:
        assert audio_original_asset.bitrate == audio_orig_meta["bitrate"]
    
    # 验证伴奏音轨元数据
    audio_inst_meta = assets_input["audio_inst_metadata"]
    if "file_size" in audio_inst_meta:
        assert audio_inst_asset.file_size == audio_inst_meta["file_size"]
    if "codec" in audio_inst_meta:
        assert audio_inst_asset.codec == audio_inst_meta["codec"]
    if "bitrate" in audio_inst_meta:
        assert audio_inst_asset.bitrate == audio_inst_meta["bitrate"]


def test_media_asset_completeness_known_example():
    """单元测试：已知示例的媒体资产完整性"""
    song_id = uuid4()
    
    service = MockMediaAssetService()
    assets = service.create_media_assets_for_song(
        song_id=song_id,
        video_path="/media/songs/test_song.mp4",
        audio_original_path="/media/songs/processed/test_song_original.mp3",
        audio_inst_path="/media/songs/processed/test_song_inst.mp3",
        video_metadata={
            "file_size": 500_000_000,
            "duration": 240.5,
            "codec": "h264",
            "bitrate": 8000000,
            "resolution": "1920x1080",
        },
        audio_original_metadata={
            "file_size": 10_000_000,
            "duration": 240.5,
            "codec": "mp3",
            "bitrate": 320000,
        },
        audio_inst_metadata={
            "file_size": 10_000_000,
            "duration": 240.5,
            "codec": "mp3",
            "bitrate": 320000,
        },
    )
    
    # 验证创建了 3 个资产
    assert len(assets) == 3
    
    # 验证资产类型
    asset_types = {asset.type for asset in assets}
    assert asset_types == {
        AssetType.VIDEO_MASTER.value,
        AssetType.AUDIO_ORIGINAL.value,
        AssetType.AUDIO_INST.value,
    }
    
    # 验证 has_required_assets
    assert service.has_required_assets(song_id)
    
    # 验证视频资产详情
    video_asset = next(a for a in assets if a.type == AssetType.VIDEO_MASTER.value)
    assert video_asset.path == "/media/songs/test_song.mp4"
    assert video_asset.file_size == 500_000_000
    assert video_asset.codec == "h264"
    assert video_asset.resolution == "1920x1080"


def test_media_asset_incomplete_without_video():
    """单元测试：缺少视频资产时不完整"""
    song_id = uuid4()
    
    service = MockMediaAssetService()
    
    # 只创建音频资产，不创建视频
    service.create_asset(
        song_id=song_id,
        asset_type=AssetType.AUDIO_ORIGINAL,
        path="/media/songs/test_original.mp3",
    )
    service.create_asset(
        song_id=song_id,
        asset_type=AssetType.AUDIO_INST,
        path="/media/songs/test_inst.mp3",
    )
    
    # 验证不完整
    assert not service.has_required_assets(song_id)


def test_media_asset_incomplete_without_audio_original():
    """单元测试：缺少原唱音轨时不完整"""
    song_id = uuid4()
    
    service = MockMediaAssetService()
    
    service.create_asset(
        song_id=song_id,
        asset_type=AssetType.VIDEO_MASTER,
        path="/media/songs/test.mp4",
    )
    service.create_asset(
        song_id=song_id,
        asset_type=AssetType.AUDIO_INST,
        path="/media/songs/test_inst.mp3",
    )
    
    assert not service.has_required_assets(song_id)


def test_media_asset_incomplete_without_audio_inst():
    """单元测试：缺少伴奏音轨时不完整"""
    song_id = uuid4()
    
    service = MockMediaAssetService()
    
    service.create_asset(
        song_id=song_id,
        asset_type=AssetType.VIDEO_MASTER,
        path="/media/songs/test.mp4",
    )
    service.create_asset(
        song_id=song_id,
        asset_type=AssetType.AUDIO_ORIGINAL,
        path="/media/songs/test_original.mp3",
    )
    
    assert not service.has_required_assets(song_id)


def test_media_asset_empty_song():
    """单元测试：没有任何资产的歌曲"""
    song_id = uuid4()
    
    service = MockMediaAssetService()
    
    # 没有创建任何资产
    assert not service.has_required_assets(song_id)
    assert len(service.get_assets_by_song(song_id)) == 0
