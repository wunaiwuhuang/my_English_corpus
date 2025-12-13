"""
导出Lemma列表工具
可以导出指定数据库中的所有lemma到CSV文件

使用方法：
1. 直接运行: python export_lemmas.py
2. 指定数据库: python export_lemmas.py --db path/to/database.db
3. 指定输出: python export_lemmas.py --output my_lemmas.csv
"""

import sqlite3
import csv
import os
import argparse
from datetime import datetime


class LemmaExporter:
    """Lemma导出器"""
    
    def __init__(self, db_path="data/dictionary.db"):
        self.db_path = db_path
        self.stats = {
            'total': 0,
            'with_topic': 0,
            'topics': set()
        }
    
    def export_simple(self, output_file):
        """
        导出简单列表（仅lemma）
        
        适合：快速查看已录入的词条
        """
        print("=" * 60)
        print("  Lemma列表导出工具 - Simple Mode")
        print("=" * 60)
        print()
        
        if not os.path.exists(self.db_path):
            print(f"❌ 错误: 找不到数据库文件 {self.db_path}")
            return False
        
        print(f"📂 数据库: {self.db_path}")
        print(f"📄 输出文件: {output_file}")
        print()
        
        # 连接数据库
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查询所有lemmas（按字母排序）
        cursor.execute("SELECT lemma FROM lemmas ORDER BY lemma")
        lemmas = cursor.fetchall()
        
        if not lemmas:
            print("⚠️  数据库中没有任何lemma")
            conn.close()
            return False
        
        # 写入CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['lemma'])  # 表头
            
            for row in lemmas:
                writer.writerow([row['lemma']])
                self.stats['total'] += 1
        
        conn.close()
        
        print(f"✅ 导出成功！")
        print(f"   共 {self.stats['total']} 个lemma")
        print()
        
        return True
    
    def export_detailed(self, output_file):
        """
        导出详细列表（lemma + topic + POS）
        
        适合：了解词条分布情况
        """
        print("=" * 60)
        print("  Lemma列表导出工具 - Detailed Mode")
        print("=" * 60)
        print()
        
        if not os.path.exists(self.db_path):
            print(f"❌ 错误: 找不到数据库文件 {self.db_path}")
            return False
        
        print(f"📂 数据库: {self.db_path}")
        print(f"📄 输出文件: {output_file}")
        print()
        
        # 连接数据库
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查询所有lemmas
        cursor.execute("""
            SELECT lemma, topic, pos_meaning, pronunciation_british
            FROM lemmas 
            ORDER BY lemma
        """)
        lemmas = cursor.fetchall()
        
        if not lemmas:
            print("⚠️  数据库中没有任何lemma")
            conn.close()
            return False
        
        # 写入CSV
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['lemma', 'topic', 'pos', 'pronunciation'])  # 表头
            
            for row in lemmas:
                lemma = row['lemma']
                topic = row['topic'] or ''
                pronunciation = row['pronunciation_british'] or ''
                
                # 解析POS
                pos_list = []
                if row['pos_meaning']:
                    import json
                    try:
                        pos_meanings = json.loads(row['pos_meaning'])
                        pos_list = [pm['pos'] for pm in pos_meanings]
                    except:
                        pass
                
                pos = ', '.join(pos_list) if pos_list else ''
                
                writer.writerow([lemma, topic, pos, pronunciation])
                
                self.stats['total'] += 1
                if topic:
                    self.stats['with_topic'] += 1
                    self.stats['topics'].add(topic)
        
        conn.close()
        
        # 打印统计
        print(f"✅ 导出成功！")
        print()
        print(f"📊 统计信息:")
        print(f"   总lemma数: {self.stats['total']}")
        print(f"   有topic的: {self.stats['with_topic']}")
        print(f"   topic种类: {len(self.stats['topics'])}")
        
        if self.stats['topics']:
            print(f"\n📚 Topics列表:")
            for topic in sorted(self.stats['topics']):
                print(f"   - {topic}")
        
        print()
        
        return True
    
    def export_by_topic(self, output_dir="exports_by_topic"):
        """
        按topic分别导出（每个topic一个CSV文件）
        
        适合：按主题分配给不同的人
        """
        print("=" * 60)
        print("  Lemma列表导出工具 - By Topic Mode")
        print("=" * 60)
        print()
        
        if not os.path.exists(self.db_path):
            print(f"❌ 错误: 找不到数据库文件 {self.db_path}")
            return False
        
        print(f"📂 数据库: {self.db_path}")
        print(f"📁 输出目录: {output_dir}")
        print()
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 连接数据库
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取所有topics
        cursor.execute("SELECT DISTINCT topic FROM lemmas WHERE topic IS NOT NULL ORDER BY topic")
        topics = [row['topic'] for row in cursor.fetchall()]
        
        if not topics:
            print("⚠️  数据库中没有任何topic分类")
            conn.close()
            return False
        
        print(f"找到 {len(topics)} 个topics:")
        for topic in topics:
            print(f"  - {topic}")
        print()
        
        # 为每个topic导出
        topic_stats = {}
        
        for topic in topics:
            cursor.execute("""
                SELECT lemma FROM lemmas 
                WHERE topic = ? 
                ORDER BY lemma
            """, (topic,))
            
            lemmas = cursor.fetchall()
            count = len(lemmas)
            topic_stats[topic] = count
            
            # 写入CSV
            output_file = os.path.join(output_dir, f"{topic}.csv")
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['lemma'])
                
                for row in lemmas:
                    writer.writerow([row['lemma']])
            
            print(f"  ✅ {topic}: {count} 个lemma -> {output_file}")
        
        # 导出无topic的lemmas
        cursor.execute("""
            SELECT lemma FROM lemmas 
            WHERE topic IS NULL 
            ORDER BY lemma
        """)
        no_topic_lemmas = cursor.fetchall()
        
        if no_topic_lemmas:
            output_file = os.path.join(output_dir, "_no_topic.csv")
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['lemma'])
                
                for row in no_topic_lemmas:
                    writer.writerow([row['lemma']])
            
            print(f"  ✅ (无topic): {len(no_topic_lemmas)} 个lemma -> {output_file}")
            topic_stats['(无topic)'] = len(no_topic_lemmas)
        
        conn.close()
        
        # 总结
        print()
        print(f"📊 统计:")
        total = sum(topic_stats.values())
        print(f"   总计: {total} 个lemma")
        for topic, count in sorted(topic_stats.items(), key=lambda x: -x[1]):
            percentage = (count / total * 100) if total > 0 else 0
            print(f"   {topic}: {count} ({percentage:.1f}%)")
        
        print()
        
        return True

def main():
    """主函数"""
    # 创建exports目录
    EXPORT_DIR = "share_export"
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    parser = argparse.ArgumentParser(description='导出Lemma列表工具')
    parser.add_argument('--db', default='data/dictionary.db', 
                       help='数据库文件路径 (默认: data/dictionary.db)')
    parser.add_argument('--output', default=None,
                       help='输出CSV文件名')
    parser.add_argument('--mode', choices=['simple', 'detailed', 'by-topic'], 
                       default='simple',
                       help='导出模式: simple(仅lemma), detailed(详细信息), by-topic(按主题分类)')
    
    args = parser.parse_args()
    
    exporter = LemmaExporter(args.db)
    
    # 根据模式导出（统一到exports目录）
    if args.mode == 'simple':
        output = args.output or os.path.join(EXPORT_DIR, f'lemmas_list_{datetime.now().strftime("%Y%m%d")}.csv')
        exporter.export_simple(output)
        
    elif args.mode == 'detailed':
        output = args.output or os.path.join(EXPORT_DIR, f'lemmas_detailed_{datetime.now().strftime("%Y%m%d")}.csv')
        exporter.export_detailed(output)
        
    elif args.mode == 'by-topic':
        output_dir = args.output or os.path.join(EXPORT_DIR, f'by_topic_{datetime.now().strftime("%Y%m%d")}')
        exporter.export_by_topic(output_dir)
    
    print("=" * 60)
    print("💡 提示:")
    print(f"   - 导出文件保存在: {EXPORT_DIR}/ 目录")
    print("   - 用Excel打开CSV文件")
    print("   - 发送给团队成员避免重复录入")
    print("=" * 60)

if __name__ == "__main__":
    main()
