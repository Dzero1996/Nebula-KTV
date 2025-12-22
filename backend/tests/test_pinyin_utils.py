"""
属性测试：拼音首字母生成一致性
**Feature: nebula-ktv, Property 2: 拼音首字母生成一致性**
**Validates: Requirements 1.2**
"""
import re
from hypothesis import given, strategies as st, settings, HealthCheck
from app.utils.pinyin_utils import to_pinyin_abbr


def is_chinese_char(char):
    """判断是否为中文字符"""
    return '\u4e00' <= char <= '\u9fff'


def count_chinese_chars(text):
    """统计中文字符数量"""
    return sum(1 for char in text if is_chinese_char(char))


def count_english_chars(text):
    """统计ASCII英文字符数量"""
    return sum(1 for char in text if char.isascii() and char.isalpha() and not is_chinese_char(char))


def count_digit_chars(text):
    """统计ASCII数字字符数量"""
    return sum(1 for char in text if char.isascii() and char.isdigit())


@settings(max_examples=100)
@given(text=st.text())
def test_pinyin_abbr_consistency(text):
    """
    Property 2: 拼音首字母生成一致性
    For any 中文字符串，拼音首字母转换函数应返回仅包含小写字母和数字的字符串，
    且长度等于输入字符串中中文字符、英文字符和数字字符的总数。
    """
    result = to_pinyin_abbr(text)
    
    # 结果应该只包含小写字母和数字
    assert re.match(r'^[a-z0-9]*$', result), f"Result contains invalid characters: {result}"
    
    # 计算预期长度：中文字符 + ASCII英文字符 + ASCII数字字符
    expected_length = (
        count_chinese_chars(text) + 
        count_english_chars(text) + 
        count_digit_chars(text)
    )
    
    # 结果长度应该等于预期长度
    assert len(result) == expected_length, (
        f"Length mismatch: expected {expected_length}, got {len(result)} "
        f"for input '{text}' -> '{result}'"
    )


def chinese_text_strategy():
    """生成包含至少一个中文字符的字符串策略"""
    # 使用中文字符范围生成
    chinese_char = st.characters(min_codepoint=0x4e00, max_codepoint=0x9fff)
    # 生成至少包含一个中文字符的字符串
    return st.text(alphabet=st.one_of(chinese_char, st.characters()), min_size=1).filter(
        lambda x: any(is_chinese_char(c) for c in x)
    )


@settings(max_examples=100, suppress_health_check=[HealthCheck.filter_too_much])
@given(chinese_text=chinese_text_strategy())
def test_pinyin_abbr_chinese_only_lowercase(chinese_text):
    """
    Property 2 扩展：对于包含中文的字符串，结果中的字母部分应该都是小写
    """
    result = to_pinyin_abbr(chinese_text)
    
    # 提取结果中的字母部分
    letters_in_result = ''.join(char for char in result if char.isalpha())
    
    # 如果有字母，所有字母都应该是小写
    if letters_in_result:
        assert letters_in_result.islower(), f"Result contains uppercase letters: {result}"


def test_pinyin_abbr_empty_string():
    """单元测试：空字符串"""
    assert to_pinyin_abbr("") == ""


def test_pinyin_abbr_known_examples():
    """单元测试：已知示例"""
    # 纯中文
    assert to_pinyin_abbr("周杰伦") == "zjl"
    
    # 中英混合 (世=shì→s, 界=jiè→j)
    result = to_pinyin_abbr("Hello世界")
    assert result == "hellosj"
    
    # 包含数字
    result = to_pinyin_abbr("123测试")
    assert result == "123cs"
    
    # 包含标点符号（应被忽略）
    result = to_pinyin_abbr("你好，世界！")
    assert result == "nhsj"