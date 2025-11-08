# English Dictionary Warehouse

一个功能完整的英语词典管理系统，用于构建个人英语语料库。

## 功能特性

### 📚 核心功能
- **Lemma管理**: 添加、编辑、删除单词词条
- **Example管理**: 添加例句并关联到单词
- **Relation管理**: 建立单词之间的语义关系
- **智能检索**: 按字母、topic、关键词搜索

### 🎯 特色功能
- 自动lemma格式化（空格转下划线）
- Example与Lemma的智能关联（灰色显示未找到的lemma）
- 新增lemma时自动刷新example有效性
- Relation必须验证lemma存在性
- 关系网络可视化（基础版本）

## 项目结构

```
english_dictionary/
├── app.py                      # 主应用入口
├── config.py                   # 配置文件
├── requirements.txt            # 依赖包
├── database/
│   ├── __init__.py
│   ├── schema.sql              # 数据库结构
│   ├── db_manager.py           # 数据库管理器
│   └── models.py               # 数据模型
├── services/
│   ├── __init__.py
│   ├── lemma_service.py        # Lemma业务逻辑
│   ├── example_service.py      # Example业务逻辑
│   └── relation_service.py     # Relation业务逻辑
├── ui/
│   ├── __init__.py
│   ├── browser.py              # 浏览器界面
│   ├── add_lemma.py            # 添加Lemma界面
│   ├── add_example.py          # 添加Example界面
│   ├── add_relation.py         # 添加Relation界面
│   └── components/
│       └── __init__.py
├── utils/
│   ├── __init__.py
│   ├── validators.py           # 数据验证
│   └── helpers.py              # 辅助函数
└── data/
    └── dictionary.db           # SQLite数据库
```

## 安装步骤

### 1. 创建项目目录
```bash
mkdir english_dictionary
cd english_dictionary
```

### 2. 创建所有子目录
```bash
mkdir -p database services ui/components utils data
```

### 3. 创建所有 `__init__.py` 文件
```bash
touch database/__init__.py
touch services/__init__.py
touch ui/__init__.py
touch ui/components/__init__.py
touch utils/__init__.py
```

### 4. 复制所有代码文件
将提供的代码依次复制到对应文件中：
- `config.py`
- `database/schema.sql`
- `database/models.py`
- `database/db_manager.py`
- `services/lemma_service.py`
- `services/example_service.py`
- `services/relation_service.py`
- `utils/validators.py`
- `utils/helpers.py`
- `ui/browser.py`
- `ui/add_lemma.py`
- `ui/add_example.py`
- `ui/add_relation.py`
- `app.py`
- `requirements.txt`

### 5. 安装依赖
```bash
pip install -r requirements.txt
```

### 6. 运行应用
```bash
streamlit run app.py
```

应用将在浏览器中自动打开，默认地址为 `http://localhost:8501`

## 使用指南

### 添加Lemma
1. 点击侧边栏 "📝 Add Lemma"
2. 填写lemma（空格会自动转为下划线）
3. 添加词性和意思（可添加多个POS）
4. 可选填写：发音、拼写差异、变形、派生词、搭配、主题
5. 点击"Save"保存

### 添加Example
1. 点击侧边栏 "📖 Add Example"
2. 输入例句
3. 输入关联的lemmas（逗号分隔）
4. 系统会自动验证lemma是否存在：
   - ✅ 绿色：lemma存在
   - ⚠️ 灰色：lemma不存在（稍后添加lemma后会自动关联）
5. 点击"Save"保存

### 添加Relation
1. 点击侧边栏 "🔗 Add Relation"
2. 输入两个lemma及其specific word
3. 系统会验证lemma是否存在（不存在会报错）
4. 选择关系类型（可互换/语境同义词）
5. 可选添加note说明
6. 点击"Save"保存

### 浏览Dictionary
1. 点击侧边栏 "🔍 Browse"
2. 可以：
   - 搜索特定lemma
   - 按topic过滤
   - 按字母/时间/topic排序
3. 点击"Examples"查看该lemma的所有例句
4. 点击"Relations"查看该lemma的所有关系
5. 点击"View Network"可查看关系网络

## 数据库结构

### lemmas表
- id: UUID主键
- lemma: 唯一的词条（空格转为下划线）
- pronunciation_british: 英式发音
- spell_nuance: 拼写差异
- pos_meaning: JSON格式的词性和意思
- inflection: JSON格式的变形
- derivation: JSON格式的派生词
- collocation: 搭配
- topic: 主题分类

### examples表
- id: UUID主键
- example: 例句内容

### example_lemma_links表（多对多）
- example_id: 关联example
- lemma: 关联lemma
- is_valid: 标记lemma是否存在（1=存在，0=不存在）

### relations表
- lemma1, specific_word1: 第一个词条
- lemma2, specific_word2: 第二个词条
- relation_type: 关系类型
- note: 备注

## 技术栈

- **前端**: Streamlit
- **数据库**: SQLite3
- **后端逻辑**: Python 3.8+
- **数据格式**: JSON（灵活字段存储）

## 维护建议

### 数据备份
定期备份 `data/dictionary.db` 文件：
```bash
cp data/dictionary.db data/dictionary_backup_$(date +%Y%m%d).db
```

### 数据导出
可以使用SQLite工具导出数据：
```bash
sqlite3 data/dictionary.db .dump > backup.sql
```

### 扩展功能
当前是MVP版本，未来可以添加：
- 使用NetworkX + Plotly绘制交互式关系网络图
- 导入/导出功能（JSON、CSV）
- 批量导入单词
- 笔记功能
- 学习进度跟踪
- Anki卡片导出

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！
