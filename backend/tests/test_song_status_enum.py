"""
属性测试：歌曲状态枚举约束
**Feature: nebula-ktv, Property 3: 歌曲状态枚举约束**
**Validates: Requirements 1.4**
"""
import pytest
from hypothesis import given, strategies as st, settings
from app.models.song import SongStatus, SongUpdate


# 定义有效的状态值
VALID_STATUSES = [status.value for status in SongStatus]


@settings(max_examples=100)
@given(status_value=st.sampled_from(VALID_STATUSES))
def test_song_status_enum_constraint_valid_values(status_value):
    """
    Property 3: 歌曲状态枚举约束
    For any 歌曲状态更新操作，状态值必须是 PENDING、PROCESSING、READY、PARTIAL 或 FAILED 之一。
    """
    # 测试有效状态值可以成功创建 SongStatus 枚举
    status_enum = SongStatus(status_value)
    assert status_enum.value in VALID_STATUSES
    
    # 测试有效状态值可以用于 SongUpdate
    song_update = SongUpdate(status=status_enum)
    assert song_update.status.value in VALID_STATUSES


@settings(max_examples=100)
@given(invalid_status=st.text().filter(lambda x: x not in VALID_STATUSES))
def test_song_status_enum_constraint_invalid_values(invalid_status):
    """
    Property 3: 歌曲状态枚举约束 - 测试无效值
    For any 无效的状态值，应该抛出 ValueError
    """
    # 测试无效状态值会抛出异常
    with pytest.raises(ValueError):
        SongStatus(invalid_status)


def test_song_status_enum_all_required_values():
    """
    单元测试：确保所有必需的状态值都存在
    """
    expected_statuses = {"PENDING", "PROCESSING", "READY", "PARTIAL", "FAILED"}
    actual_statuses = {status.value for status in SongStatus}
    assert actual_statuses == expected_statuses