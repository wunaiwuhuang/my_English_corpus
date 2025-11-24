#!/bin/bash

echo "========================================"
echo "  English Dictionary Warehouse Backup"
echo "========================================"
echo

# 设置备份目录
BACKUP_DIR="backups"
DATA_FILE="data/dictionary.db"

# 检查数据文件是否存在
if [ ! -f "$DATA_FILE" ]; then
    echo "[错误] 找不到数据库文件: $DATA_FILE"
    echo "请确保在项目根目录运行此脚本"
    exit 1
fi

# 创建备份目录（如果不存在）
if [ ! -d "$BACKUP_DIR" ]; then
    echo "[创建] 备份目录: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
fi

# 生成备份文件名（格式：dictionary_backup_20241124_153020.db）
BACKUP_NAME="dictionary_backup_$(date +%Y%m%d_%H%M%S).db"

# 执行备份
echo "[备份中] 正在备份数据库..."
cp "$DATA_FILE" "$BACKUP_DIR/$BACKUP_NAME"

if [ $? -eq 0 ]; then
    echo "[成功] 备份完成！"
    echo
    echo "备份文件: $BACKUP_DIR/$BACKUP_NAME"
    
    # 显示文件大小
    FILE_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_NAME" | cut -f1)
    echo "文件大小: $FILE_SIZE"
    
    # 统计备份数量
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/dictionary_backup_*.db 2>/dev/null | wc -l)
    echo "总备份数: $BACKUP_COUNT"
    
    echo
    echo "[提示] 建议定期清理旧备份，保留最近10个即可"
else
    echo "[失败] 备份失败！"
    echo "错误代码: $?"
    exit 1
fi

echo
echo "========================================"