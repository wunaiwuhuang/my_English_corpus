# English Dictionary Warehouse 📚

一个功能完整的英语词典管理系统，用于构建个人英语语料库。使用Streamlit + SQLite构建，界面简洁，操作便捷。

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ 功能特性

### 📚 核心功能
- **Lemma管理**: 添加、编辑、删除单词词条，支持多词性和多义项
- **Example管理**: 添加例句并智能关联到单词
- **Relation管理**: 建立单词之间的语义关系网络
- **智能检索**: 按字母、topic、关键词快速搜索

### 🎯 特色功能
- ✅ 自动lemma格式化（空格转下划线，统一小写）
- ✅ Example与Lemma智能关联（自动验证，灰色显示未找到的lemma）
- ✅ 新增lemma时自动刷新所有example的有效性
- ✅ Relation严格验证lemma存在性（避免脏数据）
- ✅ 关系网络可视化（支持多层深度探索）
- ✅ 超紧凑列表显示（一行展示，按需展开）
- ✅ 内联编辑所有字段（包括POS/Meanings）
- ✅ 自定义CSS样式（可调整行高、间距）

## 🚀 快速开始

### 环境要求
- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

#### 1. 创建项目目录
```bash
mkdir english_dictionary
cd english_dictionary
```

#### 2. 创建所有子目录
```bash
# Windows
mkdir database services ui\components utils data

# Mac/Linux
mkdir -p database services ui/components utils data
```

#### 3. 创建所有 `__init__.py` 文件
```bash
# Windows
type nul > database\__init__.py
type nul > services\__init__.py
type nul > ui\__init__.py
type nul > ui\components\__init__.py
type nul > utils\__init__.py

# Mac/Linux
touch database/__init__.py
touch services/__init__.py
touch ui/__init__.py
touch ui/components/__init__.py
touch utils/__init__.py
```

#### 4. 复制所有代码文件
将提供的代码依次复制到对应文件中：

**根目录文件：**
- `config.py`
- `app.py`
- `requirements.txt`
- `README.md`
- `backup.bat` (Windows) 或 `backup.sh` (Mac/Linux)

**database/ 目录：**
- `schema.sql`
- `models.py`
- `db_manager.py`

**services/ 目录：**
- `lemma_service.py`
- `example_service.py`
- `relation_service.py`

**utils/ 目录：**
- `validators.py`
- `helpers.py`

**ui/ 目录：**
- `browser.py`
- `add_lemma.py`
- `add_example.py`
- `add_relation.py`

#### 5. 安装依赖
```bash
pip install -r requirements.txt
```

#### 6. 运行应用
```bash
streamlit run app.py
```

应用将在浏览器中自动打开，默认地址为 `http://localhost:8501`

## 📖 使用指南

### 添加Lemma (词条)
1. 点击侧边栏 **"📝 Add Lemma"**
2. 填写基础信息：
   - **Lemma**: 词条（空格自动转为下划线）
   - **Pronunciation**: 英式发音（可选）
   - **Spell Nuance**: 拼写差异（可选，英左美右）
   - **Collocation**: 搭配（可选）
   - **Topic**: 主题分类（可选）
3. 配置词性和意思：
   - 选择词性（n., v., adj. 等）
   - 每行输入一个意思
   - 可添加多个词性
4. 可选填写：
   - **Inflection**: 不规则变形（格式：`verb: past, past_participle | noun: plural`）
   - **Derivation**: 派生词（格式：`word:meaning`，每行一个）
5. 点击 **"💾 Save"** 保存

**示例：**
```
Lemma: break down
Pronunciation: breɪk daʊn
Topic: phrasal_verbs

POS 1: v.
Meanings:
- (of a machine) stop working
- lose control of emotions
- analyze into components

Inflection: verb: broke down, broken down
Derivation: breakdown: noun form
```

### 添加Example (例句)
1. 点击侧边栏 **"📖 Add Example"**
2. 输入例句内容
3. 输入关联的lemmas（逗号分隔）
4. 系统自动验证：
   - ✅ **绿色**：lemma存在
   - ⚠️ **灰色**：lemma不存在（稍后添加lemma后会自动关联）
5. 点击 **"💾 Save"** 保存

**示例：**
```
Example: My car broke down on the highway yesterday.
Lemmas: break_down, car, highway
```

### 添加Relation (关系)
1. 点击侧边栏 **"🔗 Add Relation"**
2. 输入第一个词条：
   - Lemma 1: 词条名（必须已存在）
   - Specific Word 1: 特定用法（单个词）
3. 输入第二个词条：
   - Lemma 2: 词条名（必须已存在）
   - Specific Word 2: 特定用法（单个词）
4. 选择关系类型：
   - **Interchangeable**: 可互换
   - **Contextual Synonym**: 语境同义词
5. 添加备注说明（可选）
6. 点击 **"💾 Save"** 保存

**示例：**
```
Lemma 1: provide        Specific Word 1: provide
Lemma 2: postulate      Specific Word 2: postulate
Type: contextual_synonym
Note: 'provide' in law, 'postulate' in academic
```

### 浏览Dictionary (词典)
1. 点击侧边栏 **"🔍 Browse"**
2. 使用搜索和过滤：
   - 🔎 搜索框：输入关键词
   - 📚 Topic过滤：选择特定主题
   - 🔤 排序：字母序/最近添加/Topic
3. 词条操作（一行显示）：
   - **👁️**: 展开查看详细信息
   - **✏️**: 编辑词条（所有字段可编辑）
   - **🗑️**: 删除词条
   - **🕸️**: 查看关系网络（如有关系）
4. 展开后可查看：
   - 完整的词性和意思
   - Inflection、Derivation、Collocation
   - 关联的Examples
   - 相关的Relations

## 🗄️ 数据库结构

### lemmas表（词条）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | UUID主键 |
| lemma | TEXT | 唯一词条（空格转下划线） |
| pronunciation_british | TEXT | 英式发音 |
| spell_nuance | TEXT | 拼写差异 |
| pos_meaning | TEXT | JSON格式的词性和意思 |
| inflection | TEXT | JSON格式的变形 |
| derivation | TEXT | JSON格式的派生词 |
| collocation | TEXT | 搭配 |
| topic | TEXT | 主题分类 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### examples表（例句）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | UUID主键 |
| example | TEXT | 例句内容 |
| created_at | TIMESTAMP | 创建时间 |

### example_lemma_links表（例句-词条关联）
| 字段 | 类型 | 说明 |
|------|------|------|
| example_id | TEXT | 例句ID（外键） |
| lemma | TEXT | 词条（外键） |
| is_valid | INTEGER | 是否有效（1=存在，0=不存在） |

### relations表（词条关系）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增主键 |
| lemma1 | TEXT | 第一个词条（外键） |
| specific_word1 | TEXT | 第一个特定词 |
| lemma2 | TEXT | 第二个词条（外键） |
| specific_word2 | TEXT | 第二个特定词 |
| relation_type | TEXT | 关系类型 |
| note | TEXT | 备注 |
| created_at | TIMESTAMP | 创建时间 |

## 💾 数据备份

### 自动备份脚本

**Windows用户：**
```bash
# 双击运行
backup.bat

# 或命令行运行
.\backup.bat
```

**Mac/Linux用户：**
```bash
# 添加执行权限（首次）
chmod +x backup.sh

# 运行备份
./backup.sh
```

备份文件将保存在 `backups/` 目录，命名格式：
```
dictionary_backup_20241124_153020.db
```

### 手动备份

**方法1：直接复制文件**
```bash
# Windows
copy data\dictionary.db backups\dictionary_backup.db

# Mac/Linux
cp data/dictionary.db backups/dictionary_backup.db
```

**方法2：使用SQLite导出**
```bash
sqlite3 data/dictionary.db .dump > backup.sql
```

### 恢复数据
```bash
# 方法1：替换文件
copy backups\dictionary_backup_20241124.db data\dictionary.db

# 方法2：从SQL导入
sqlite3 data/dictionary.db < backup.sql
```

## 🔧 自定义样式

### 调整行高和间距
在 `ui/browser.py` 的开头可以自定义CSS：

```python
st.markdown("""
    <style>
    /* 调整这些值来改变显示效果 */
    .element-container {
        margin-bottom: -10px !important;  /* 元素间距 */
    }
    .stButton button {
        height: 2rem !important;          /* 按钮高度 */
    }
    .stMarkdown p {
        line-height: 1.3 !important;      /* 行高 */
    }
    </style>
""", unsafe_allow_html=True)
```

### 调整列宽比例
在 `ui/browser.py` 约85行修改：

```python
col1, col2 = st.columns([8, 2])  # lemma区:按钮区 = 8:2
```

## 🛠️ 技术栈

- **前端框架**: Streamlit 1.28+
- **数据库**: SQLite3
- **后端语言**: Python 3.8+
- **数据格式**: JSON (灵活字段存储)
- **架构模式**: MVC分层架构

## 📁 项目结构

```
english_dictionary/
├── app.py                      # 主应用入口（路由）
├── config.py                   # 全局配置
├── requirements.txt            # Python依赖
├── backup.bat / backup.sh      # 备份脚本
├── README.md                   # 项目文档
│
├── database/                   # 数据库层
│   ├── __init__.py
│   ├── schema.sql              # 表结构定义
│   ├── db_manager.py           # 数据库操作封装
│   └── models.py               # 数据模型
│
├── services/                   # 业务逻辑层
│   ├── __init__.py
│   ├── lemma_service.py        # Lemma业务逻辑
│   ├── example_service.py      # Example业务逻辑
│   └── relation_service.py     # Relation业务逻辑
│
├── ui/                         # 用户界面层
│   ├── __init__.py
│   ├── browser.py              # 浏览器界面
│   ├── add_lemma.py            # 添加Lemma界面
│   ├── add_example.py          # 添加Example界面
│   ├── add_relation.py         # 添加Relation界面
│   └── components/             # UI组件
│       └── __init__.py
│
├── utils/                      # 工具函数
│   ├── __init__.py
│   ├── validators.py           # 数据验证
│   └── helpers.py              # 辅助函数
│
├── data/                       # 数据目录
│   └── dictionary.db           # SQLite数据库（自动生成）
│
└── backups/                    # 备份目录（自动创建）
    └── dictionary_backup_*.db  # 备份文件
```

## 🔍 查看数据

### 使用DB Browser (推荐)
1. 下载 [DB Browser for SQLite](https://sqlitebrowser.org/)
2. 打开 `data/dictionary.db`
3. 图形化查看和编辑所有表

### 使用命令行
```bash
sqlite3 data/dictionary.db

# 查看所有表
.tables

# 查看lemmas
SELECT lemma, pronunciation_british, topic FROM lemmas;

# 退出
.quit
```

## 🚧 未来扩展

- [ ] 交互式关系网络图（NetworkX + Plotly）
- [ ] 数据导入/导出（JSON、CSV、Excel）
- [ ] 批量导入单词功能
- [ ] 学习进度追踪
- [ ] 生词本功能
- [ ] Anki卡片导出
- [ ] 多用户支持
- [ ] 云端同步

## ❓ 常见问题

### Q: 如何迁移到另一台电脑？
**A:** 只需复制整个项目文件夹，特别是 `data/dictionary.db` 文件。

### Q: 数据存储在哪里？
**A:** 所有数据存储在 `data/dictionary.db` 这一个SQLite文件中。

### Q: 如何清理旧备份？
**A:** 手动删除 `backups/` 目录中的旧文件，建议保留最近10个备份。

### Q: 可以同时运行多个实例吗？
**A:** 不建议。SQLite不支持高并发写入，可能导致数据冲突。

### Q: 如何重置所有数据？
**A:** 删除 `data/dictionary.db` 文件，重新运行应用会自动创建空数据库。

## 📄 许可证

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.

## 🤝 贡献

欢迎提交Issue和Pull Request！

如果这个项目对你有帮助，请给个⭐Star支持一下！

---

**Built with ❤️ using Streamlit and SQLite**
