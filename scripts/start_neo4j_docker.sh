#!/bin/bash
# Neo4j Docker 一键启动脚本

set -e

echo "========================================"
echo "Neo4j Docker 启动脚本"
echo "========================================"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker 未安装"
    exit 1
fi

# 检查并停止现有容器
if docker ps -a | grep -q openclaw-neo4j; then
    echo "[Info] 停止现有容器..."
    docker stop openclaw-neo4j 2>/dev/null || true
    docker rm openclaw-neo4j 2>/dev/null || true
fi

# 启动 Neo4j
echo "[Info] 启动 Neo4j 容器..."
docker run -d \
    --name openclaw-neo4j \
    -p 7474:7474 \
    -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/neo4j \
    -e NEO4J_PLUGINS='["apoc"]' \
    neo4j:5

echo "[Info] 等待 Neo4j 启动..."
sleep 15

# 配置 Python 虚拟环境
echo "[Info] 配置 Python 虚拟环境..."
PROJECT_DIR="$HOME/openclaw"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
python3 -m venv venv 2>/dev/null || python3 -m virtualenv venv
source venv/bin/activate
pip install --upgrade pip
pip install neo4j openai

cat > .env << 'EOF'
DEEPSEEK_API_KEY=your-api-key-here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j
EOF

echo ""
echo "========================================"
echo "启动完成!"
echo "========================================"
echo "HTTP: http://localhost:7474"
echo "Bolt: bolt://localhost:7687"
echo "用户: neo4j / neo4j"
echo ""
echo "启动对话:"
echo "  cd $PROJECT_DIR && source venv/bin/activate"
echo "  python /home/program/graph_enable_ability/openclaw_neo4j_demo.py"