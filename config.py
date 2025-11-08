"""
配置文件 - 存储所有项目常量和配置
"""
import os

# 项目路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'dictionary.db')

# 确保data目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 词性选项
POS_OPTIONS = [
    'n.',      # 名词
    'v.',      # 动词
    'adj.',    # 形容词
    'adv.',    # 副词
    'prep.',   # 介词
    'conj.',   # 连词
    'pron.',   # 代词
    'interj.', # 感叹词
    'aux.',    # 助动词
    'det.',    # 限定词
]

# 关系类型
RELATION_TYPES = [
    'interchangeable',      # 可互换
    'contextual_synonym',   # 语境同义词
]

# UI配置
PAGE_TITLE = "English Dictionary Warehouse"
PAGE_ICON = "📚"
LAYOUT = "wide"

# 数据库配置
DB_TIMEOUT = 30  # 数据库连接超时（秒）