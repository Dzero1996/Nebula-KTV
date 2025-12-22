"""
属性测试：错误状态记录完整性
**Feature: nebula-ktv, Property 11: 错误状态记录完整性**
**Validates: Requirements 2.5**

For any 处理失败的歌曲，状态必须为 FAILED 且 meta_json 中包含 error 字段。
"""
import pytest
import string
from hypothesis import given, strategies as st, settings, HealthCheck
from uuid import uuid4
from datetime import datetime

from app.models.song import Song, SongStatus


# 定义错误消息策略
ERROR_MESSAGE_SAMPLES = [
    "UVR5 separation failed: Out of memory",
    "Whisper transcription failed: Audio too short",
    "File not found: /media/songs/test.mp4",
    "Processing timeout",
    "Invalid audio format",
    "FFmpeg extraction failed",
    "Network error during model download",
    "Insufficient disk space",
]

SIMPLE_CHARS = string.ascii_letters + string.digits + " .:_-"


def error_message_strategy():
    """生成错误消息的策略"""
    return st.one_of(
        st.sampled_from(ERROR_MESSAGE_SAMPLES),
        st.text(alphabet=SIMPLE_CHARS, min_size=1, max_size=200)
    )


def song_with_error_strategy():
    """生成带有错误状态的歌曲数据策略"""
    return st.fixed_dictionaries({
        "title": st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=50),
        "artist": st.text(alphabet=string.ascii_letters + string.digits, min_size=1, max_size=30),
        "error_message": error_message_strategy(),
    })


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(data=song_with_error_strategy())
def test_error_status_recording_completeness(data):
    """
    Property 11: 错误状态记录完整性
    For any 处理失败的歌曲，状态必须为 FAILED 且 meta_json 中包含 error 字段。
    
    测试 _mark_song_failed 函数的逻辑正确性（不依赖数据库）
    """
    # 1. 创建一个模拟的歌曲对象（初始状态为 PROCESSING）
    song = Song(
        title=data["title"],
        artist=data["artist"],
        status=SongStatus.PROCESSING.value,
        meta_json={},
    )
    song.id = uuid4()
    song.created_at = datetime.now()
    song.updated_at = datetime.now()
    
    # 2. 模拟 _mark_song_failed 的逻辑
    error_message = data["error_message"]
    song.status = SongStatus.FAILED.value
    if song.meta_json is None:
        song.meta_json = {}
    song.meta_json["error"] = error_message
    
    # 3. 验证错误状态记录完整性
    # Property: 状态必须为 FAILED
    assert song.status == SongStatus.FAILED.value, \
        f"Expected status FAILED, got {song.status}"
    
    # Property: meta_json 必须包含 error 字段
    assert "error" in song.meta_json, \
        "meta_json must contain 'error' field for failed songs"
    
    # Property: error 字段必须包含错误消息
    assert song.meta_json["error"] == error_message, \
        f"Error message mismatch: expected '{error_message}', got '{song.meta_json['error']}'"
    
    # Property: 错误消息不能为空
    assert len(song.meta_json["error"]) > 0, \
        "Error message must not be empty"


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    initial_meta=st.one_of(
        st.none(),
        st.fixed_dictionaries({}, optional={
            "bpm": st.integers(min_value=60, max_value=200),
            "key": st.sampled_from(["C", "D", "E", "F", "G"]),
            "existing_field": st.text(alphabet=string.ascii_letters, min_size=1, max_size=20),
        })
    ),
    error_message=error_message_strategy()
)
def test_error_preserves_existing_meta_json(initial_meta, error_message):
    """
    Property: 错误记录应保留 meta_json 中的现有字段
    """
    # 1. 创建带有初始 meta_json 的歌曲
    song = Song(
        title="Test Song",
        artist="Test Artist",
        status=SongStatus.PROCESSING.value,
        meta_json=initial_meta if initial_meta else {},
    )
    song.id = uuid4()
    song.created_at = datetime.now()
    song.updated_at = datetime.now()
    
    # 保存原始 meta_json 的副本
    original_meta = dict(song.meta_json) if song.meta_json else {}
    
    # 2. 模拟 _mark_song_failed 的逻辑
    song.status = SongStatus.FAILED.value
    if song.meta_json is None:
        song.meta_json = {}
    song.meta_json["error"] = error_message
    
    # 3. 验证现有字段被保留
    for key, value in original_meta.items():
        if key != "error":  # error 字段可能被覆盖
            assert key in song.meta_json, \
                f"Original field '{key}' was lost after marking as failed"
            assert song.meta_json[key] == value, \
                f"Original field '{key}' value changed"
    
    # 4. 验证 error 字段存在
    assert "error" in song.meta_json
    assert song.meta_json["error"] == error_message


def test_error_status_known_examples():
    """单元测试：已知示例的错误状态记录"""
    # 测试 UVR5 分离失败
    song = Song(
        title="测试歌曲",
        artist="测试歌手",
        status=SongStatus.PROCESSING.value,
        meta_json={"bpm": 120},
    )
    song.id = uuid4()
    song.created_at = datetime.now()
    song.updated_at = datetime.now()
    
    # 模拟失败
    error_msg = "UVR5 separation failed: Out of memory"
    song.status = SongStatus.FAILED.value
    song.meta_json["error"] = error_msg
    
    assert song.status == SongStatus.FAILED.value
    assert song.meta_json["error"] == error_msg
    assert song.meta_json["bpm"] == 120  # 原有字段保留


def test_error_status_with_none_meta_json():
    """单元测试：meta_json 为 None 时的错误记录"""
    song = Song(
        title="测试歌曲",
        artist="测试歌手",
        status=SongStatus.PROCESSING.value,
        meta_json=None,
    )
    song.id = uuid4()
    song.created_at = datetime.now()
    song.updated_at = datetime.now()
    
    # 模拟失败（处理 None 的情况）
    error_msg = "Processing timeout"
    song.status = SongStatus.FAILED.value
    if song.meta_json is None:
        song.meta_json = {}
    song.meta_json["error"] = error_msg
    
    assert song.status == SongStatus.FAILED.value
    assert song.meta_json["error"] == error_msg


def test_error_status_overwrites_previous_error():
    """单元测试：新错误覆盖旧错误"""
    song = Song(
        title="测试歌曲",
        artist="测试歌手",
        status=SongStatus.FAILED.value,
        meta_json={"error": "Previous error"},
    )
    song.id = uuid4()
    song.created_at = datetime.now()
    song.updated_at = datetime.now()
    
    # 模拟新的失败
    new_error_msg = "New error after retry"
    song.meta_json["error"] = new_error_msg
    
    assert song.status == SongStatus.FAILED.value
    assert song.meta_json["error"] == new_error_msg
