"""
拼音转换工具
支持首字母缩写和完整拼音生成
"""
import re
from pypinyin import lazy_pinyin, Style


# ASCII小写字母集合，用于验证输出
ASCII_LOWERCASE = set('abcdefghijklmnopqrstuvwxyz')
ASCII_DIGITS = set('0123456789')


def to_pinyin_abbr(text: str) -> str:
    """
    将中文字符串转换为拼音首字母缩写
    
    Args:
        text: 输入的中文字符串
        
    Returns:
        拼音首字母字符串，仅包含ASCII小写字母(a-z)和数字(0-9)
        
    Examples:
        >>> to_pinyin_abbr("周杰伦")
        "zjl"
        >>> to_pinyin_abbr("Hello 世界")
        "hellosz"
        >>> to_pinyin_abbr("123测试")
        "123cs"
    """
    if not text:
        return ""
    
    result = []
    
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
            # 获取拼音首字母
            pinyin_list = lazy_pinyin(char, style=Style.FIRST_LETTER)
            if pinyin_list:
                first_letter = pinyin_list[0].lower()
                # 严格验证：必须是ASCII小写字母(a-z)
                if first_letter in ASCII_LOWERCASE:
                    result.append(first_letter)
        elif char.isascii() and char.isalpha():
            # 仅处理ASCII英文字符，直接转小写
            result.append(char.lower())
        elif char.isascii() and char.isdigit():
            # 仅处理ASCII数字字符
            result.append(char)
        # 其他字符（标点符号、非ASCII字符如À等）忽略
    
    return ''.join(result)


def to_pinyin_full(text: str) -> str:
    """
    将中文字符串转换为完整拼音（空格分隔）
    
    Args:
        text: 输入的中文字符串
        
    Returns:
        完整拼音字符串，单词之间用空格分隔
        
    Examples:
        >>> to_pinyin_full("周杰伦")
        "zhou jie lun"
        >>> to_pinyin_full("七里香")
        "qi li xiang"
        >>> to_pinyin_full("Hello 世界")
        "hello shi jie"
    """
    if not text:
        return ""
    
    result = []
    current_word = []
    
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
            # 如果之前有英文单词，先保存
            if current_word:
                result.append(''.join(current_word))
                current_word = []
            
            # 获取完整拼音
            pinyin_list = lazy_pinyin(char, style=Style.NORMAL)
            if pinyin_list:
                result.append(pinyin_list[0].lower())
        elif char.isascii() and char.isalpha():
            # 英文字符累积成单词
            current_word.append(char.lower())
        elif char.isspace():
            # 空格：保存当前单词
            if current_word:
                result.append(''.join(current_word))
                current_word = []
        elif char.isascii() and char.isdigit():
            # 数字：保存当前单词，然后添加数字
            if current_word:
                result.append(''.join(current_word))
                current_word = []
            result.append(char)
        # 其他字符忽略
    
    # 保存最后的单词
    if current_word:
        result.append(''.join(current_word))
    
    return ' '.join(result)