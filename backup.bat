@echo off
chcp 65001 >nul
echo ========================================
echo   English Dictionary Warehouse Backup
echo ========================================
echo.

REM 设置备份目录
set BACKUP_DIR=backups
set DATA_FILE=data\dictionary.db

REM 检查数据文件是否存在
if not exist "%DATA_FILE%" (
    echo [错误] 找不到数据库文件: %DATA_FILE%
    echo 请确保在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 创建备份目录（如果不存在）
if not exist "%BACKUP_DIR%" (
    echo [创建] 备份目录: %BACKUP_DIR%
    mkdir "%BACKUP_DIR%"
)

REM 生成备份文件名（格式：dictionary_backup_20241124_153020.db）
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do (
    set backup_date=%%a%%b%%c
)
for /f "tokens=1-2 delims=: " %%a in ('time /t') do (
    set backup_time=%%a%%b
)
set backup_time=%backup_time::=%
set BACKUP_NAME=dictionary_backup_%backup_date: =0%_%backup_time: =0%.db

REM 执行备份
echo [备份中] 正在备份数据库...
copy "%DATA_FILE%" "%BACKUP_DIR%\%BACKUP_NAME%" >nul

if %errorlevel% equ 0 (
    echo [成功] 备份完成！
    echo.
    echo 备份文件: %BACKUP_DIR%\%BACKUP_NAME%
    
    REM 显示文件大小
    for %%A in ("%BACKUP_DIR%\%BACKUP_NAME%") do (
        echo 文件大小: %%~zA 字节
    )
    
    REM 统计备份数量
    dir /b "%BACKUP_DIR%\dictionary_backup_*.db" 2>nul | find /c ".db" > temp_count.txt
    set /p backup_count=<temp_count.txt
    del temp_count.txt
    echo 总备份数: %backup_count%
    
    echo.
    echo [提示] 建议定期清理旧备份，保留最近10个即可
) else (
    echo [失败] 备份失败！
    echo 错误代码: %errorlevel%
)

echo.
echo ========================================
pause