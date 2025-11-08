"""
数据库管理器 - 处理所有数据库操作
"""
import sqlite3
from typing import List, Optional, Tuple, Any
import config


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = config.DB_PATH):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库，创建表"""
        import os
        schema_path = os.path.join(config.BASE_DIR, 'database', 'schema.sql')
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        
        conn = self.get_connection()
        try:
            conn.executescript(schema)
            conn.commit()
        finally:
            conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path, timeout=config.DB_TIMEOUT)
        conn.row_factory = sqlite3.Row  # 允许通过列名访问
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """执行查询并返回所有结果"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            conn.close()
    
    def execute_insert(self, query: str, params: tuple = ()) -> Optional[int]:
        """执行插入并返回lastrowid"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise ValueError(f"数据库约束错误: {str(e)}")
        finally:
            conn.close()
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """执行更新并返回影响的行数"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()
    
    def execute_delete(self, query: str, params: tuple = ()) -> int:
        """执行删除并返回影响的行数"""
        return self.execute_update(query, params)
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """批量执行SQL"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()


# 全局数据库实例
db = DatabaseManager()