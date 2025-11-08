"""
辅助函数
"""
import json
import uuid
from typing import Any, Optional


def generate_uuid() -> str:
    """生成UUID"""
    return str(uuid.uuid4())


def to_json(obj: Any) -> str:
    """将对象转换为JSON字符串"""
    if obj is None:
        return None
    return json.dumps(obj, ensure_ascii=False)


def from_json(json_str: Optional[str]) -> Any:
    """将JSON字符串转换为对象"""
    if not json_str:
        return None
    try:
        return json.loads(json_str)
    except:
        return None


def safe_get(dictionary: dict, key: str, default=None) -> Any:
    """安全地从字典获取值"""
    return dictionary.get(key, default) if dictionary else default