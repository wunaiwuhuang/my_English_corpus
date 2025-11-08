"""
数据模型定义
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class POSMeaning:
    """词性和意思"""
    pos: str
    meanings: List[str] = field(default_factory=list)


@dataclass
class Derivation:
    """派生词"""
    word: str
    meaning: Optional[str] = None


@dataclass
class Lemma:
    """Lemma数据模型 (Sheet 1)"""
    id: str
    lemma: str
    pronunciation_british: Optional[str] = None
    spell_nuance: Optional[str] = None
    pos_meaning: List[POSMeaning] = field(default_factory=list)
    inflection: Optional[Dict[str, List[str]]] = None
    derivation: List[Derivation] = field(default_factory=list)
    collocation: Optional[str] = None
    topic: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class Example:
    """Example数据模型 (Sheet 2)"""
    id: str
    example: str
    lemmas: List[str] = field(default_factory=list)  # 关联的lemma列表
    created_at: Optional[datetime] = None


@dataclass
class Relation:
    """Relation数据模型 (Sheet 3)"""
    id: Optional[int]
    lemma1: str
    specific_word1: str
    lemma2: str
    specific_word2: str
    relation_type: str
    note: Optional[str] = None
    created_at: Optional[datetime] = None