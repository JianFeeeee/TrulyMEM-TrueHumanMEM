@echo off
REM Windows打包脚本

echo 开始打包Windows版本...

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到python
    exit /b 1
)

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

REM 打包Windows exe文件
echo 打包Windows exe文件...
python -m PyInstaller ^
    --clean ^
    --onefile ^
    --name TrulyMEM ^
    --console ^
    --add-data "graph_memory_tui/styles/*.css;graph_memory_tui/styles" ^
    --add-data "graph_memory_tui/web/templates/*.html;graph_memory_tui/web/templates" ^
    --hidden-import textual ^
    --hidden-import openai ^
    --hidden-import flask ^
    --hidden-import neo4j ^
    graph_memory_tui/main.py

echo 打包完成！
echo 可执行文件位于: dist\TrulyMEM.exe
pause
