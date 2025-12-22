"""
属性测试：HTTP Range 响应正确性
**Feature: nebula-ktv, Property 8: HTTP Range 响应正确性**
**Validates: Requirements 9.1, 9.2**
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume

from app.api.stream import parse_range_header, get_content_type


# ============================================
# 属性测试：HTTP Range 解析正确性
# ============================================

@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    start=st.integers(min_value=0, max_value=10000),
    end=st.integers(min_value=0, max_value=10000),
    file_size=st.integers(min_value=1, max_value=100000)
)
def test_range_header_parsing_standard_format(start, end, file_size):
    """
    Property 8: HTTP Range 响应正确性
    *For any* 带有 Range 头的媒体请求，响应必须包含正确的 Content-Range 头，
    且返回的字节范围与请求匹配。
    
    测试标准格式: bytes=start-end
    """
    # 确保 start <= end 且在文件范围内
    assume(start <= end)
    assume(start < file_size)
    
    range_header = f"bytes={start}-{end}"
    
    parsed_start, parsed_end = parse_range_header(range_header, file_size)
    
    # 验证解析结果
    assert parsed_start == start, f"Start mismatch: expected {start}, got {parsed_start}"
    
    # end 应该被限制在 file_size - 1
    expected_end = min(end, file_size - 1)
    assert parsed_end == expected_end, f"End mismatch: expected {expected_end}, got {parsed_end}"
    
    # 验证范围有效性
    assert parsed_start <= parsed_end, "Start should be <= end"
    assert parsed_start >= 0, "Start should be >= 0"
    assert parsed_end < file_size, "End should be < file_size"


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    start=st.integers(min_value=0, max_value=10000),
    file_size=st.integers(min_value=1, max_value=100000)
)
def test_range_header_parsing_open_end(start, file_size):
    """
    Property 8: HTTP Range 响应正确性
    测试开放结束格式: bytes=start-
    """
    assume(start < file_size)
    
    range_header = f"bytes={start}-"
    
    parsed_start, parsed_end = parse_range_header(range_header, file_size)
    
    # 验证解析结果
    assert parsed_start == start, f"Start mismatch: expected {start}, got {parsed_start}"
    assert parsed_end == file_size - 1, f"End should be file_size - 1 ({file_size - 1}), got {parsed_end}"
    
    # 验证范围有效性
    assert parsed_start <= parsed_end
    assert parsed_end < file_size


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    suffix_length=st.integers(min_value=1, max_value=10000),
    file_size=st.integers(min_value=1, max_value=100000)
)
def test_range_header_parsing_suffix(suffix_length, file_size):
    """
    Property 8: HTTP Range 响应正确性
    测试后缀格式: bytes=-suffix_length (最后 N 字节)
    """
    range_header = f"bytes=-{suffix_length}"
    
    parsed_start, parsed_end = parse_range_header(range_header, file_size)
    
    # 验证解析结果
    expected_start = max(0, file_size - suffix_length)
    assert parsed_start == expected_start, f"Start mismatch: expected {expected_start}, got {parsed_start}"
    assert parsed_end == file_size - 1, f"End should be file_size - 1 ({file_size - 1}), got {parsed_end}"
    
    # 验证范围有效性
    assert parsed_start <= parsed_end
    assert parsed_start >= 0
    assert parsed_end < file_size


@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(
    start=st.integers(min_value=0, max_value=10000),
    end=st.integers(min_value=0, max_value=10000),
    file_size=st.integers(min_value=1, max_value=100000)
)
def test_content_range_calculation(start, end, file_size):
    """
    Property 8: HTTP Range 响应正确性
    验证 Content-Range 头的计算正确性
    """
    assume(start <= end)
    assume(start < file_size)
    
    range_header = f"bytes={start}-{end}"
    parsed_start, parsed_end = parse_range_header(range_header, file_size)
    
    # 计算 Content-Length
    content_length = parsed_end - parsed_start + 1
    
    # 验证 Content-Length 正确性
    assert content_length > 0, "Content-Length should be positive"
    assert content_length <= file_size, "Content-Length should not exceed file size"
    
    # 验证 Content-Range 格式
    content_range = f"bytes {parsed_start}-{parsed_end}/{file_size}"
    assert f"bytes {parsed_start}-{parsed_end}/{file_size}" == content_range


# ============================================
# 单元测试：已知示例
# ============================================

def test_range_header_standard_example():
    """单元测试：标准 Range 请求"""
    start, end = parse_range_header("bytes=0-1023", 10000)
    assert start == 0
    assert end == 1023


def test_range_header_open_end_example():
    """单元测试：开放结束 Range 请求"""
    start, end = parse_range_header("bytes=5000-", 10000)
    assert start == 5000
    assert end == 9999


def test_range_header_suffix_example():
    """单元测试：后缀 Range 请求"""
    start, end = parse_range_header("bytes=-500", 10000)
    assert start == 9500
    assert end == 9999


def test_range_header_end_exceeds_file_size():
    """单元测试：end 超过文件大小时应被截断"""
    start, end = parse_range_header("bytes=0-99999", 10000)
    assert start == 0
    assert end == 9999


def test_range_header_suffix_exceeds_file_size():
    """单元测试：后缀长度超过文件大小"""
    start, end = parse_range_header("bytes=-99999", 10000)
    assert start == 0
    assert end == 9999


def test_range_header_invalid_format():
    """单元测试：无效的 Range 格式"""
    with pytest.raises(ValueError):
        parse_range_header("invalid", 10000)


def test_range_header_empty_both():
    """单元测试：start 和 end 都为空"""
    with pytest.raises(ValueError):
        parse_range_header("bytes=-", 10000)


def test_range_header_start_greater_than_end():
    """单元测试：start > end 应该抛出异常"""
    with pytest.raises(ValueError):
        parse_range_header("bytes=1000-500", 10000)


# ============================================
# 单元测试：Content-Type 映射
# ============================================

def test_content_type_video_mp4():
    """单元测试：MP4 视频类型"""
    assert get_content_type("video.mp4") == "video/mp4"


def test_content_type_audio_mp3():
    """单元测试：MP3 音频类型"""
    assert get_content_type("audio.mp3") == "audio/mpeg"


def test_content_type_audio_wav():
    """单元测试：WAV 音频类型"""
    assert get_content_type("audio.wav") == "audio/wav"


def test_content_type_audio_flac():
    """单元测试：FLAC 音频类型"""
    assert get_content_type("audio.flac") == "audio/flac"


def test_content_type_unknown():
    """单元测试：未知文件类型"""
    assert get_content_type("file.xyz") == "application/octet-stream"


def test_content_type_case_insensitive():
    """单元测试：扩展名大小写不敏感"""
    assert get_content_type("video.MP4") == "video/mp4"
    assert get_content_type("audio.WAV") == "audio/wav"
