#!/bin/bash
# Linux打包脚本
# 需要在Linux系统上运行

echo "开始打包Linux版本..."

# 检查Python和PyInstaller
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3"
    exit 1
fi

# 安装依赖
echo "安装依赖..."
pip3 install -r requirements.txt

# 打包Linux二进制文件
echo "打包Linux二进制文件..."
python3 -m PyInstaller \
    --clean \
    --onefile \
    --name TrulyMEM \
    --console \
    --add-data "graph_memory_tui/styles/*.css:graph_memory_tui/styles" \
    --add-data "graph_memory_tui/web/templates/*.html:graph_memory_tui/web/templates" \
    --hidden-import textual \
    --hidden-import openai \
    --hidden-import flask \
    --hidden-import neo4j \
    graph_memory_tui/main.py

echo "打包完成！"
echo "可执行文件位于: dist/TrulyMEM"
