@echo off
chcp 65001 >nul
echo ========================================
echo   Lemma列表导出工具
echo ========================================
echo.

REM 检查数据库文件
if not exist "data\dictionary.db" (
    echo ❌ 错误: 找不到 data\dictionary.db
    echo.
    pause
    exit /b 1
)

echo 请选择导出模式:
echo.
echo   1. 简单模式 - 仅导出lemma列表
echo   2. 详细模式 - 包含topic和词性
echo   3. 按Topic分类 - 每个topic一个文件
echo   4. 导出指定数据库
echo.
set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" goto simple
if "%choice%"=="2" goto detailed
if "%choice%"=="3" goto by_topic
if "%choice%"=="4" goto custom
goto invalid

:simple
echo.
echo 🚀 正在导出简单列表...
python export_lemmas.py --mode simple
goto end

:detailed
echo.
echo 🚀 正在导出详细列表...
python export_lemmas.py --mode detailed
goto end

:by_topic
echo.
echo 🚀 正在按topic分类导出...
python export_lemmas.py --mode by-topic
goto end

:custom
echo.
set /p db_path="请输入数据库路径: "
if not exist "%db_path%" (
    echo ❌ 文件不存在: %db_path%
    echo.
    pause
    exit /b 1
)
echo.
echo 🚀 正在导出...
python export_lemmas.py --db "%db_path%" --mode simple
goto end

:invalid
echo.
echo ❌ 无效选项
echo.
pause
exit /b 1

:end
echo.
if errorlevel 1 (
    echo ❌ 导出失败
) else (
    echo ✅ 导出成功！
    echo.
    echo 📌 下一步:
    echo   - 用Excel打开CSV文件
    echo   - 发送给团队成员
    echo   - 避免重复录入
)
echo.
pause
