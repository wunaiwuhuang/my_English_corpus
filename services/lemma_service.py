"""
Lemma业务逻辑服务 (Sheet 1)
"""
from typing import List, Optional, Dict, Tuple
from database.db_manager import db
from database.models import Lemma, POSMeaning, Derivation
from utils.helpers import generate_uuid, to_json, from_json
from utils.validators import validate_lemma
from datetime import datetime


class LemmaService:
    """Lemma服务"""
    
    def create_lemma(self, lemma: str, pronunciation_british: Optional[str] = None,
                    spell_nuance: Optional[str] = None, pos_meaning: List[Dict] = None,
                    inflection: Optional[Dict] = None, derivation: List[Dict] = None,
                    collocation: Optional[str] = None, topic: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """
        创建新的lemma
        
        Returns:
            (成功标志, 消息, lemma_id)
        """
        # 验证lemma格式
        valid, formatted_lemma, error_msg = validate_lemma(lemma)
        if not valid:
            return False, error_msg, None
        
        # 检查是否已存在
        if self.lemma_exists(formatted_lemma):
            return False, f"Lemma '{formatted_lemma}' 已存在", None
        
        # 生成UUID
        lemma_id = generate_uuid()
        
        # 转换为JSON
        pos_meaning_json = to_json(pos_meaning) if pos_meaning else None
        inflection_json = to_json(inflection) if inflection else None
        derivation_json = to_json(derivation) if derivation else None
        
        # 插入数据库
        query = """
            INSERT INTO lemmas (id, lemma, pronunciation_british, spell_nuance, 
                               pos_meaning, inflection, derivation, collocation, topic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        try:
            db.execute_insert(query, (lemma_id, formatted_lemma, pronunciation_british,
                                     spell_nuance, pos_meaning_json, inflection_json,
                                     derivation_json, collocation, topic))
            return True, "Lemma创建成功", lemma_id
        except Exception as e:
            return False, f"创建失败: {str(e)}", None
    
    def get_lemma(self, lemma: str) -> Optional[Dict]:
        """根据lemma获取完整信息"""
        query = "SELECT * FROM lemmas WHERE lemma = ?"
        results = db.execute_query(query, (lemma,))
        
        if not results:
            return None
        
        row = results[0]
        return self._row_to_dict(row)
    
    def get_lemma_by_id(self, lemma_id: str) -> Optional[Dict]:
        """根据ID获取lemma"""
        query = "SELECT * FROM lemmas WHERE id = ?"
        results = db.execute_query(query, (lemma_id,))
        
        if not results:
            return None
        
        return self._row_to_dict(results[0])
    
    def get_all_lemmas(self, sort_by: str = 'lemma') -> List[Dict]:
        """
        获取所有lemmas
        
        Args:
            sort_by: 排序字段 ('lemma', 'created_at', 'topic')
        """
        valid_sorts = {'lemma', 'created_at', 'topic'}
        if sort_by not in valid_sorts:
            sort_by = 'lemma'
        
        query = f"SELECT * FROM lemmas ORDER BY {sort_by}"
        results = db.execute_query(query)
        
        return [self._row_to_dict(row) for row in results]
    
    def search_lemmas(self, keyword: str) -> List[Dict]:
        """搜索lemmas（模糊匹配）"""
        query = "SELECT * FROM lemmas WHERE lemma LIKE ? ORDER BY lemma"
        results = db.execute_query(query, (f"%{keyword}%",))
        
        return [self._row_to_dict(row) for row in results]
    
    def get_lemmas_by_topic(self, topic: str) -> List[Dict]:
        """根据topic获取lemmas"""
        query = "SELECT * FROM lemmas WHERE topic = ? ORDER BY lemma"
        results = db.execute_query(query, (topic,))
        
        return [self._row_to_dict(row) for row in results]
    
    def get_all_topics(self) -> List[str]:
        """获取所有不同的topics"""
        query = "SELECT DISTINCT topic FROM lemmas WHERE topic IS NOT NULL ORDER BY topic"
        results = db.execute_query(query)
        
        return [row['topic'] for row in results]
    
    def count_lemmas(self) -> int:
        """统计lemma总数"""
        query = "SELECT COUNT(*) as count FROM lemmas"
        result = db.execute_query(query)[0]
        return result['count']
    
    def count_lemmas_by_topic(self, topic: str) -> int:
        """统计特定topic下的lemma数量"""
        query = "SELECT COUNT(*) as count FROM lemmas WHERE topic = ?"
        result = db.execute_query(query, (topic,))[0]
        return result['count']
    
    def lemma_exists(self, lemma: str) -> bool:
        """检查lemma是否存在"""
        query = "SELECT COUNT(*) as count FROM lemmas WHERE lemma = ?"
        result = db.execute_query(query, (lemma,))[0]
        return result['count'] > 0
    
    def update_lemma(self, lemma: str, **kwargs) -> Tuple[bool, str]:
        """更新lemma信息"""
        if not self.lemma_exists(lemma):
            return False, f"Lemma '{lemma}' 不存在"
        
        # 构建更新语句
        update_fields = []
        params = []
        
        field_mapping = {
            'pronunciation_british': 'pronunciation_british',
            'spell_nuance': 'spell_nuance',
            'pos_meaning': 'pos_meaning',
            'inflection': 'inflection',
            'derivation': 'derivation',
            'collocation': 'collocation',
            'topic': 'topic'
        }
        
        for key, db_field in field_mapping.items():
            if key in kwargs:
                value = kwargs[key]
                # JSON字段需要序列化
                if key in ['pos_meaning', 'inflection', 'derivation']:
                    value = to_json(value)
                update_fields.append(f"{db_field} = ?")
                params.append(value)
        
        if not update_fields:
            return False, "没有需要更新的字段"
        
        # 添加updated_at
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(lemma)
        
        query = f"UPDATE lemmas SET {', '.join(update_fields)} WHERE lemma = ?"
        
        try:
            db.execute_update(query, tuple(params))
            return True, "更新成功"
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def delete_lemma(self, lemma: str) -> Tuple[bool, str]:
        """删除lemma"""
        if not self.lemma_exists(lemma):
            return False, f"Lemma '{lemma}' 不存在"
        
        query = "DELETE FROM lemmas WHERE lemma = ?"
        try:
            db.execute_delete(query, (lemma,))
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def _row_to_dict(self, row) -> Dict:
        """将数据库行转换为字典"""
        return {
            'id': row['id'],
            'lemma': row['lemma'],
            'pronunciation_british': row['pronunciation_british'],
            'spell_nuance': row['spell_nuance'],
            'pos_meaning': from_json(row['pos_meaning']),
            'inflection': from_json(row['inflection']),
            'derivation': from_json(row['derivation']),
            'collocation': row['collocation'],
            'topic': row['topic'],
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }


# 全局服务实例
lemma_service = LemmaService()