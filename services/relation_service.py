"""
Relation业务逻辑服务 (Sheet 3)
"""
from typing import List, Tuple, Dict, Optional, Set
from database.db_manager import db
from services.lemma_service import lemma_service
from utils.validators import validate_specific_word, validate_relation_type


class RelationService:
    """Relation服务"""
    
    def create_relation(self, lemma1: str, specific_word1: str, lemma2: str, 
                       specific_word2: str, relation_type: str, 
                       note: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
        """
        创建新的relation
        
        Returns:
            (成功标志, 消息, relation_id)
        """
        # 验证lemmas必须存在
        if not lemma_service.lemma_exists(lemma1):
            return False, f"Lemma '{lemma1}' 不存在，请先创建", None
        
        if not lemma_service.lemma_exists(lemma2):
            return False, f"Lemma '{lemma2}' 不存在，请先创建", None
        
        # 验证specific words
        valid1, word1, error1 = validate_specific_word(specific_word1)
        if not valid1:
            return False, f"Specific word 1: {error1}", None
        
        valid2, word2, error2 = validate_specific_word(specific_word2)
        if not valid2:
            return False, f"Specific word 2: {error2}", None
        
        # 验证relation type
        if not validate_relation_type(relation_type):
            return False, f"无效的关系类型: {relation_type}", None
        
        # 插入数据库
        query = """
            INSERT INTO relations (lemma1, specific_word1, lemma2, specific_word2, 
                                  relation_type, note)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            relation_id = db.execute_insert(query, (lemma1, word1, lemma2, word2, 
                                                   relation_type, note))
            return True, "Relation创建成功", relation_id
        except Exception as e:
            return False, f"创建失败: {str(e)}", None
    
    def get_relation(self, relation_id: int) -> Optional[Dict]:
        """获取单个relation"""
        query = "SELECT * FROM relations WHERE id = ?"
        results = db.execute_query(query, (relation_id,))
        
        if not results:
            return None
        
        return self._row_to_dict(results[0])
    
    def get_all_relations(self) -> List[Dict]:
        """获取所有relations"""
        query = "SELECT * FROM relations ORDER BY created_at DESC"
        results = db.execute_query(query)
        
        return [self._row_to_dict(row) for row in results]
    
    def get_relations_by_lemma(self, lemma: str, specific_word: Optional[str] = None) -> List[Dict]:
        """
        获取某个lemma相关的所有relations
        
        Args:
            lemma: lemma名称
            specific_word: 可选，指定specific word则只返回该词的关系
        """
        if specific_word:
            query = """
                SELECT * FROM relations
                WHERE (lemma1 = ? AND specific_word1 = ?) 
                   OR (lemma2 = ? AND specific_word2 = ?)
                ORDER BY created_at DESC
            """
            results = db.execute_query(query, (lemma, specific_word, lemma, specific_word))
        else:
            query = """
                SELECT * FROM relations
                WHERE lemma1 = ? OR lemma2 = ?
                ORDER BY created_at DESC
            """
            results = db.execute_query(query, (lemma, lemma))
        
        return [self._row_to_dict(row) for row in results]
    
    def get_relation_network(self, lemma: str, specific_word: str, 
                           max_depth: int = 2) -> Dict:
        """
        获取关系网络数据（用于绘图）
        
        Args:
            lemma: 起始lemma
            specific_word: 起始specific word
            max_depth: 最大递归深度
            
        Returns:
            {
                'nodes': [{'id': 'lemma-word', 'lemma': 'xxx', 'word': 'xxx'}, ...],
                'edges': [{'source': 'node1', 'target': 'node2', 'type': 'xxx', 'note': 'xxx'}, ...]
            }
        """
        nodes = {}  # key: 'lemma-word', value: node dict
        edges = []
        visited = set()
        
        def make_node_id(l: str, w: str) -> str:
            return f"{l}-{w}"
        
        def add_node(l: str, w: str):
            node_id = make_node_id(l, w)
            if node_id not in nodes:
                nodes[node_id] = {
                    'id': node_id,
                    'lemma': l,
                    'word': w
                }
            return node_id
        
        def explore(l: str, w: str, depth: int):
            if depth > max_depth:
                return
            
            node_id = make_node_id(l, w)
            if node_id in visited:
                return
            
            visited.add(node_id)
            add_node(l, w)
            
            # 获取相关的relations
            relations = self.get_relations_by_lemma(l, w)
            
            for rel in relations:
                # 确定另一端的节点
                if rel['lemma1'] == l and rel['specific_word1'] == w:
                    other_lemma = rel['lemma2']
                    other_word = rel['specific_word2']
                else:
                    other_lemma = rel['lemma1']
                    other_word = rel['specific_word1']
                
                other_id = add_node(other_lemma, other_word)
                
                # 添加边
                edge = {
                    'source': node_id,
                    'target': other_id,
                    'type': rel['relation_type'],
                    'note': rel['note']
                }
                edges.append(edge)
                
                # 递归探索
                explore(other_lemma, other_word, depth + 1)
        
        # 从起始节点开始探索
        explore(lemma, specific_word, 0)
        
        return {
            'nodes': list(nodes.values()),
            'edges': edges
        }
    
    def update_relation(self, relation_id: int, **kwargs) -> Tuple[bool, str]:
        """更新relation"""
        # 检查是否存在
        query = "SELECT COUNT(*) as count FROM relations WHERE id = ?"
        result = db.execute_query(query, (relation_id,))[0]
        
        if result['count'] == 0:
            return False, f"Relation ID {relation_id} 不存在"
        
        # 构建更新语句
        update_fields = []
        params = []
        
        valid_fields = ['lemma1', 'specific_word1', 'lemma2', 'specific_word2', 
                       'relation_type', 'note']
        
        for field in valid_fields:
            if field in kwargs:
                # 验证lemma存在性
                if field in ['lemma1', 'lemma2']:
                    if not lemma_service.lemma_exists(kwargs[field]):
                        return False, f"Lemma '{kwargs[field]}' 不存在"
                
                # 验证specific word
                if field in ['specific_word1', 'specific_word2']:
                    valid, word, error = validate_specific_word(kwargs[field])
                    if not valid:
                        return False, error
                    kwargs[field] = word
                
                # 验证relation type
                if field == 'relation_type':
                    if not validate_relation_type(kwargs[field]):
                        return False, f"无效的关系类型: {kwargs[field]}"
                
                update_fields.append(f"{field} = ?")
                params.append(kwargs[field])
        
        if not update_fields:
            return False, "没有需要更新的字段"
        
        params.append(relation_id)
        query = f"UPDATE relations SET {', '.join(update_fields)} WHERE id = ?"
        
        try:
            db.execute_update(query, tuple(params))
            return True, "更新成功"
        except Exception as e:
            return False, f"更新失败: {str(e)}"
    
    def delete_relation(self, relation_id: int) -> Tuple[bool, str]:
        """删除relation"""
        query = "DELETE FROM relations WHERE id = ?"
        try:
            rows = db.execute_delete(query, (relation_id,))
            if rows == 0:
                return False, f"Relation ID {relation_id} 不存在"
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def _row_to_dict(self, row) -> Dict:
        """将数据库行转换为字典"""
        return {
            'id': row['id'],
            'lemma1': row['lemma1'],
            'specific_word1': row['specific_word1'],
            'lemma2': row['lemma2'],
            'specific_word2': row['specific_word2'],
            'relation_type': row['relation_type'],
            'note': row['note'],
            'created_at': row['created_at']
        }


# 全局服务实例
relation_service = RelationService()