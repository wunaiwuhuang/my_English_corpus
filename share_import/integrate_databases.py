"""
数据库整合工具
专用于整合多人分别录入的dictionary.db文件

特点：
- 不整合relations（避免冲突）
- 智能处理lemma和example重复
- 详细的冲突报告

使用方法：
1. 将所有 .db 文件放入 share_import/input_db/ 目录
2. 运行此脚本
3. 整合结果保存在 share_import/output_db/integrated.db
"""

import sqlite3
import os
import shutil
from datetime import datetime
from pathlib import Path


class DatabaseIntegrator:
    """数据库整合器"""
    
    def __init__(self):
        # 设置路径
        self.base_dir = Path(__file__).parent
        self.input_dir = self.base_dir / "input_db"
        self.output_dir = self.base_dir / "output_db"
        self.output_db = self.output_dir / "integrated.db"
        
        # 统计信息
        self.stats = {
            'total_sources': 0,
            'lemmas': {
                'added': 0,
                'skipped': 0,
                'conflicts': []
            },
            'examples': {
                'added': 0,
                'merged': 0,
                'links_added': 0
            },
            'relations': {
                'skipped': 0
            }
        }
        
        # 冲突详情
        self.conflict_details = []
    
    def integrate(self):
        """执行整合"""
        print("=" * 70)
        print("  数据库整合工具 - Database Integrator")
        print("=" * 70)
        print()
        
        # 1. 检查并准备目录
        if not self._prepare_directories():
            return False
        
        # 2. 查找所有数据库文件
        db_files = self._find_db_files()
        if not db_files:
            return False
        
        # 3. 准备输出数据库
        self._prepare_output_db()
        
        # 4. 逐个整合
        for i, db_path in enumerate(db_files, 1):
            print(f"\n[{i}/{len(db_files)}] 整合: {db_path.name}")
            print("-" * 70)
            self._integrate_single_db(db_path)
        
        # 5. 生成报告
        self._generate_report()
        
        # 6. 保存冲突详情
        if self.conflict_details:
            self._save_conflict_report()
        
        print("\n" + "=" * 70)
        print("✅ 整合完成！")
        print(f"输出文件: {self.output_db}")
        print("=" * 70)
        
        return True
    
    def _prepare_directories(self):
        """准备目录结构"""
        # 创建input_db目录
        if not self.input_dir.exists():
            self.input_dir.mkdir(parents=True)
            print(f"📁 已创建目录: {self.input_dir}")
            print(f"\n⚠️  请将需要整合的 .db 文件放入此目录")
            print(f"   然后重新运行脚本")
            return False
        
        # 创建output_db目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        return True
    
    def _find_db_files(self):
        """查找所有数据库文件"""
        db_files = list(self.input_dir.glob("*.db"))
        
        if not db_files:
            print(f"❌ 在 {self.input_dir} 中未找到任何 .db 文件")
            print(f"\n请将需要整合的数据库文件放入此目录")
            return []
        
        self.stats['total_sources'] = len(db_files)
        
        print(f"📋 找到 {len(db_files)} 个数据库文件:")
        for i, db in enumerate(db_files, 1):
            # 显示文件大小
            size = db.stat().st_size / 1024  # KB
            print(f"  {i}. {db.name} ({size:.1f} KB)")
        
        print()
        confirm = input("是否继续整合? (y/n): ").lower()
        if confirm != 'y':
            print("已取消")
            return []
        
        return db_files
    
    def _prepare_output_db(self):
        """准备输出数据库"""
        # 如果输出文件已存在，备份
        if self.output_db.exists():
            backup_name = self.output_db.parent / f"integrated_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy(self.output_db, backup_name)
            print(f"\n📦 已备份现有文件: {backup_name.name}")
            self.output_db.unlink()
        
        # 从schema创建新数据库
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        
        if not schema_path.exists():
            print(f"\n❌ 错误: 找不到 {schema_path}")
            exit(1)
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        
        conn = sqlite3.connect(self.output_db)
        conn.executescript(schema)
        conn.commit()
        conn.close()
        
        print(f"📝 创建新数据库: {self.output_db.name}\n")
    
    def _integrate_single_db(self, source_path):
        """整合单个数据库"""
        try:
            source_conn = sqlite3.connect(source_path)
            source_conn.row_factory = sqlite3.Row
            target_conn = sqlite3.connect(self.output_db)
            
            # 1. 整合lemmas
            print("  → 整合 lemmas...")
            lemma_stats = self._integrate_lemmas(source_conn, target_conn, source_path.stem)
            print(f"     ✅ 新增: {lemma_stats['added']}, ⏭️ 跳过: {lemma_stats['skipped']}")
            
            # 2. 整合examples
            print("  → 整合 examples...")
            example_stats = self._integrate_examples(source_conn, target_conn)
            print(f"     ✅ 新增: {example_stats['added']}, 🔗 链接: {example_stats['links']}")
            
            # 3. 跳过relations
            relation_count = source_conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
            if relation_count > 0:
                print(f"  → 跳过 relations ({relation_count} 条)")
                self.stats['relations']['skipped'] += relation_count
            
            target_conn.commit()
            
        except Exception as e:
            print(f"  ❌ 错误: {str(e)}")
            target_conn.rollback()
        finally:
            source_conn.close()
            target_conn.close()
    
    def _integrate_lemmas(self, source, target, source_name):
        """整合lemmas"""
        added = 0
        skipped = 0
        
        cursor = source.cursor()
        cursor.execute("SELECT * FROM lemmas")
        
        for row in cursor.fetchall():
            lemma = row['lemma']
            
            # 检查是否已存在
            existing = target.execute(
                "SELECT * FROM lemmas WHERE lemma = ?",
                (lemma,)
            ).fetchone()
            
            if existing:
                # 记录冲突
                skipped += 1
                self.stats['lemmas']['skipped'] += 1
                self.stats['lemmas']['conflicts'].append(lemma)
                
                # 保存冲突详情
                self.conflict_details.append({
                    'lemma': lemma,
                    'source': source_name,
                    'reason': 'lemma已存在'
                })
            else:
                # 插入新lemma
                target.execute("""
                    INSERT INTO lemmas (
                        id, lemma, pronunciation_british, spell_nuance,
                        pos_meaning, inflection, derivation, collocation, topic,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['id'], row['lemma'], row['pronunciation_british'],
                    row['spell_nuance'], row['pos_meaning'], row['inflection'],
                    row['derivation'], row['collocation'], row['topic'],
                    row['created_at'], row['updated_at']
                ))
                added += 1
                self.stats['lemmas']['added'] += 1
        
        return {'added': added, 'skipped': skipped}
    
    def _integrate_examples(self, source, target):
        """整合examples"""
        added = 0
        merged = 0
        links_added = 0
        
        cursor = source.cursor()
        cursor.execute("SELECT * FROM examples")
        
        for row in cursor.fetchall():
            example_text = row['example']
            old_example_id = row['id']
            
            # 检查example内容是否已存在
            existing = target.execute(
                "SELECT id FROM examples WHERE example = ?",
                (example_text,)
            ).fetchone()
            
            if existing:
                # 使用已存在的example_id
                new_example_id = existing[0]
                merged += 1
                self.stats['examples']['merged'] += 1
            else:
                # 插入新example
                new_example_id = row['id']
                target.execute("""
                    INSERT INTO examples (id, example, created_at)
                    VALUES (?, ?, ?)
                """, (new_example_id, example_text, row['created_at']))
                added += 1
                self.stats['examples']['added'] += 1
            
            # 整合example_lemma_links
            link_cursor = source.cursor()
            link_cursor.execute("""
                SELECT lemma, is_valid FROM example_lemma_links
                WHERE example_id = ?
            """, (old_example_id,))
            
            for link_row in link_cursor.fetchall():
                lemma = link_row['lemma']
                
                # 检查链接是否已存在
                link_exists = target.execute("""
                    SELECT 1 FROM example_lemma_links
                    WHERE example_id = ? AND lemma = ?
                """, (new_example_id, lemma)).fetchone()
                
                if not link_exists:
                    # 验证lemma是否存在于目标数据库
                    lemma_exists = target.execute(
                        "SELECT 1 FROM lemmas WHERE lemma = ?",
                        (lemma,)
                    ).fetchone()
                    
                    is_valid = 1 if lemma_exists else 0
                    
                    target.execute("""
                        INSERT INTO example_lemma_links (example_id, lemma, is_valid)
                        VALUES (?, ?, ?)
                    """, (new_example_id, lemma, is_valid))
                    links_added += 1
                    self.stats['examples']['links_added'] += 1
        
        return {'added': added, 'merged': merged, 'links': links_added}
    
    def _generate_report(self):
        """生成整合报告"""
        print("\n" + "=" * 70)
        print("  整合报告")
        print("=" * 70)
        
        print(f"\n📊 数据源: {self.stats['total_sources']} 个数据库文件")
        
        print(f"\n📖 Lemmas:")
        print(f"  ✅ 新增: {self.stats['lemmas']['added']}")
        print(f"  ⏭️  跳过（冲突）: {self.stats['lemmas']['skipped']}")
        
        if self.stats['lemmas']['conflicts']:
            print(f"\n  ⚠️  冲突的lemmas (前10个):")
            for lemma in self.stats['lemmas']['conflicts'][:10]:
                print(f"     - {lemma}")
            if len(self.stats['lemmas']['conflicts']) > 10:
                remaining = len(self.stats['lemmas']['conflicts']) - 10
                print(f"     ... 还有 {remaining} 个 (详见冲突报告)")
        
        print(f"\n📝 Examples:")
        print(f"  ✅ 新增: {self.stats['examples']['added']}")
        print(f"  🔗 合并到已有: {self.stats['examples']['merged']}")
        print(f"  🔗 新增链接: {self.stats['examples']['links_added']}")
        
        print(f"\n🔗 Relations:")
        print(f"  ⏭️  跳过（按要求不整合）: {self.stats['relations']['skipped']}")
        
        # 最终统计
        conn = sqlite3.connect(self.output_db)
        total_lemmas = conn.execute("SELECT COUNT(*) FROM lemmas").fetchone()[0]
        total_examples = conn.execute("SELECT COUNT(*) FROM examples").fetchone()[0]
        conn.close()
        
        print(f"\n📈 整合后总计:")
        print(f"  Lemmas: {total_lemmas}")
        print(f"  Examples: {total_examples}")
    
    def _save_conflict_report(self):
        """保存冲突报告到文件"""
        report_path = self.output_dir / f"conflict_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("  冲突报告 - Conflict Report\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"冲突总数: {len(self.conflict_details)}\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("冲突详情:\n")
            f.write("-" * 70 + "\n\n")
            
            for i, conflict in enumerate(self.conflict_details, 1):
                f.write(f"{i}. Lemma: {conflict['lemma']}\n")
                f.write(f"   来源: {conflict['source']}\n")
                f.write(f"   原因: {conflict['reason']}\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("处理建议:\n")
            f.write("1. 检查是否是同一个词但拼写略有不同\n")
            f.write("2. 如果是不同含义，考虑用不同的lemma名称\n")
            f.write("3. 如果确实重复，保留质量更好的那个\n")
            f.write("4. 使用 DB Browser for SQLite 手动处理冲突\n")
        
        print(f"\n📄 冲突报告已保存: {report_path.name}")


def main():
    """主函数"""
    integrator = DatabaseIntegrator()
    
    print()
    print("💡 提示:")
    print("  - 此工具会整合 lemmas 和 examples")
    print("  - relations 不会被整合（避免冲突）")
    print("  - 冲突的lemma会被跳过（保留第一个）")
    print()
    
    success = integrator.integrate()
    
    if success:
        print()
        print("📌 下一步:")
        print(f"  1. 检查整合结果: {integrator.output_db}")
        print("  2. 如果有冲突，查看冲突报告")
        print("  3. 如果满意，可以替换主数据库:")
        print(f"     copy {integrator.output_db} ..\\data\\dictionary.db")
        print()


if __name__ == "__main__":
    main()