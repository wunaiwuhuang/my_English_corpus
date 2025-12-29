@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   数据库整合工具
echo ========================================
echo.

REM 检查input_db目录
if not exist "input_db" (
    echo 📁 创建 input_db 目录...
    mkdir input_db
    echo.
    echo ⚠️  请将需要整合的 .db 文件放入 input_db\ 目录
    echo    然后重新运行此脚本
    echo.
    pause
    exit /b
)

REM 检查是否有 .db 文件
dir /b input_db\*.db >nul 2>&1
if errorlevel 1 (
    echo ❌ 在 input_db\ 中未找到任何 .db 文件
    echo.
    echo 请将需要整合的数据库文件放入 input_db\ 目录
    echo 例如:
    echo   - dictionary_张三.db
    echo   - dictionary_李四.db
    echo   - dictionary_王五.db
    echo.
    pause
    exit /b
)

echo 📋 找到以下数据库文件:
echo.
dir /b input_db\*.db
echo.

echo 💡 整合说明:
echo   - 会整合 lemmas 和 examples
echo   - relations 不会整合（避免冲突）
echo   - 重复的lemma会跳过（保留第一个）
echo.

set /p confirm="是否继续整合? (y/n): "
if /i not "%confirm%"=="y" (
    echo 已取消
    pause
    exit /b
)

echo.
echo 🚀 开始整合...
echo.

REM 运行Python脚本
python integrate_databases.py

if errorlevel 1 (
    echo.
    echo ❌ 整合失败！请检查错误信息
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo.
echo 📌 整合完成！下一步:
echo.
echo 1. 检查整合结果:
echo    output_db\integrated.db
echo.
echo 2. 如果有冲突，查看:
echo    output_db\conflict_report_*.txt
echo.
echo 3. 如果满意，替换主数据库:
echo    copy output_db\integrated.db ..\data\dictionary.db
echo.
echo ========================================
echo.
pause