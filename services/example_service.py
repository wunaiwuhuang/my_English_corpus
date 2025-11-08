"""
Example业务逻辑服务 (Sheet 2)
"""
from typing import List, Tuple, Dict, Optional
from database.db_manager import db
from services.lemma_service import lemma_service
from utils.helpers import generate_uuid


class ExampleService:
    """Example服务"""
    
    def create_example(self, example: str, lemmas: List[str]) -> Tuple[bool, str, Optional[str]]:
        """
        创建新的example并关联lemmas
        
        Args:
            example: 例句内容
            lemmas: 关联的lemma列表
            
        Returns:
            (成功标志, 消息, example_id)
        """
        if not example or not example.strip():
            return False, "Example不能为空", None
        
        # 生成UUID
        example_id = generate_uuid()
        
        # 插入example
        query = "INSERT INTO examples (id, example) VALUES (?, ?)"
        try:
            db.execute_insert(query, (example_id, example.strip()))
            
            # 关联lemmas
            if lemmas:
                self._link_lemmas(example_id, lemmas)
            
            return True, "Example创建成功", example_id
        except Exception as e:
            return False, f"创建失败: {str(e)}", None
    
    def get_example(self, example_id: str) -> Optional[Dict]:
        """获取example详情"""
        query = "SELECT * FROM examples WHERE id = ?"
        results = db.execute_query(query, (example_id,))
        
        if not results:
            return None
        
        row = results[0]
        
        # 获取关联的lemmas
        lemmas = self.get_linked_lemmas(example_id)
        
        return {
            'id': row['id'],
            'example': row['example'],
            'lemmas': lemmas,
            'created_at': row['created_at']
        }
    
    def get_all_examples(self) -> List[Dict]:
        """获取所有examples"""
        query = "SELECT * FROM examples ORDER BY created_at DESC"
        results = db.execute_query(query)
        
        examples = []
        for row in results:
            lemmas = self.get_linked_lemmas(row['id'])
            examples.append({
                'id': row['id'],
                'example': row['example'],
                'lemmas': lemmas,
                'created_at': row['created_at']
            })
        
        return examples
    
    def get_examples_by_lemma(self, lemma: str) -> List[Dict]:
        """获取某个lemma的所有examples"""
        query = """
            SELECT e.* FROM examples e
            JOIN example_lemma_links el ON e.id = el.example_id
            WHERE el.lemma = ?
            ORDER BY e.created_at DESC
        """
        results = db.execute_query(query, (lemma,))
        
        examples = []
        for row in results:
            lemmas = self.get_linked_lemmas(row['id'])
            examples.append({
                'id': row['id'],
                'example': row['example'],
                'lemmas': lemmas,
                'created_at': row['created_at']
            })
        
        return examples
    
    def get_linked_lemmas(self, example_id: str) -> List[Dict]:
        """
        获取example关联的所有lemmas
        
        Returns:
            [{'lemma': 'xxx', 'is_valid': True/False}, ...]
        """
        query = """
            SELECT lemma, is_valid FROM example_lemma_links
            WHERE example_id = ?
        """
        results = db.execute_query(query, (example_id,))
        
        return [{'lemma': row['lemma'], 'is_valid': bool(row['is_valid'])} 
                for row in results]
    
    def update_example(self, example_id: str, example: Optional[str] = None, 
                      lemmas: Optional[List[str]] = None) -> Tuple[bool, str]:
        """更新example"""
        query = "SELECT COUNT(*) as count FROM examples WHERE id = ?"
        result = db.execute_query(query, (example_id,))[0]
        
        if result['count'] == 0:
            return False, f"Example ID '{example_id}' 不存在"
        
        # 更新example文本
        if example is not None:
            query = "UPDATE examples SET example = ? WHERE id = ?"
            db.execute_update(query, (example.strip(), example_id))
        
        # 更新lemma关联
        if lemmas is not None:
            # 删除旧关联
            db.execute_delete("DELETE FROM example_lemma_links WHERE example_id = ?", 
                            (example_id,))
            # 添加新关联
            self._link_lemmas(example_id, lemmas)
        
        return True, "更新成功"
    
    def delete_example(self, example_id: str) -> Tuple[bool, str]:
        """删除example"""
        query = "DELETE FROM examples WHERE id = ?"
        try:
            rows = db.execute_delete(query, (example_id,))
            if rows == 0:
                return False, f"Example ID '{example_id}' 不存在"
            return True, "删除成功"
        except Exception as e:
            return False, f"删除失败: {str(e)}"
    
    def _link_lemmas(self, example_id: str, lemmas: List[str]):
        """
        关联example和lemmas
        自动检测lemma是否存在并设置is_valid标志
        """
        if not lemmas:
            return
        
        links = []
        for lemma in lemmas:
            lemma = lemma.strip().lower()
            if lemma:
                # 检查lemma是否存在
                is_valid = lemma_service.lemma_exists(lemma)
                links.append((example_id, lemma, 1 if is_valid else 0))
        
        if links:
            query = """
                INSERT INTO example_lemma_links (example_id, lemma, is_valid)
                VALUES (?, ?, ?)
            """
            db.execute_many(query, links)
    
    def refresh_lemma_validity(self):
        """
        刷新所有example-lemma链接的有效性
        当新增lemma后调用，更新之前无效的链接
        """
        # 获取所有无效的链接
        query = "SELECT DISTINCT lemma FROM example_lemma_links WHERE is_valid = 0"
        results = db.execute_query(query)
        
        # 检查这些lemma现在是否存在
        for row in results:
            lemma = row['lemma']
            if lemma_service.lemma_exists(lemma):
                # 更新为有效
                update_query = """
                    UPDATE example_lemma_links 
                    SET is_valid = 1 
                    WHERE lemma = ?
                """
                db.execute_update(update_query, (lemma,))


# 全局服务实例
example_service = ExampleService()