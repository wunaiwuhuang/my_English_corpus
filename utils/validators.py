"""
数据验证函数
"""
import re
from typing import Tuple


def validate_lemma(lemma: str) -> Tuple[bool, str, str]:
    """
    验证并格式化lemma
    
    Args:
        lemma: 原始输入的lemma
        
    Returns:
        (是否有效, 格式化后的lemma, 错误信息)
    """
    if not lemma or not lemma.strip():
        return False, "", "Lemma不能为空"
    
    # 替换空格为下划线
    formatted = lemma.strip().replace(' ', '_')
    
    # 验证只包含字母、'和_
    if not re.match(r"^[a-zA-Z'_]+$", formatted):
        return False, "", "Lemma只能包含字母、单引号(')和下划线(_)"
    
    # 转换为小写
    formatted = formatted.lower()
    
    return True, formatted, ""


def validate_specific_word(word: str) -> Tuple[bool, str, str]:
    """
    验证specific word（只能是单个词）
    
    Args:
        word: 输入的词
        
    Returns:
        (是否有效, 格式化后的词, 错误信息)
    """
    if not word or not word.strip():
        return False, "", "Specific word不能为空"
    
    formatted = word.strip().lower()
    
    # 检查是否包含空格（只能是单个词）
    if ' ' in formatted or '_' in formatted:
        return False, "", "Specific word只能是单个词，不能包含空格"
    
    # 验证只包含字母和单引号
    if not re.match(r"^[a-zA-Z']+$", formatted):
        return False, "", "Specific word只能包含字母和单引号(')"
    
    return True, formatted, ""


def validate_relation_type(relation_type: str) -> bool:
    """验证关系类型是否有效"""
    from config import RELATION_TYPES
    return relation_type in RELATION_TYPES


def validate_pos(pos: str) -> bool:
    """验证词性是否有效"""
    from config import POS_OPTIONS
    return pos in POS_OPTIONS