#!/bin/bash
set -e

echo "========================================"
echo "Neo4j 一键安装脚本 - openEuler"
echo "========================================"

if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

echo "[1/5] 检查 Java 环境..."
if command -v java &> /dev/null; then
    echo "  已安装: $(java -version 2>&1 | head -n 1)"
else
    echo "  安装 OpenJDK 17..."
    $SUDO dnf install -y java-17-openjdk-headless
fi

echo "[2/5] 添加 Neo4j 源..."
$SUDO cat > /etc/yum.repos.d/neo4j.repo << 'EOF'
[neo4j]
name=Neo4j Repository
baseurl=https://yum.neo4j.com/stable
enabled=1
gpgcheck=1
gpgkey=https://debian.neo4j.com/neotechnology.gpg.key
EOF

echo "[3/5] 安装 Neo4j..."
$SUDO dnf install -y neo4j

echo "[4/5] 启动 Neo4j..."
$SUDO systemctl enable neo4j
$SUDO systemctl start neo4j
sleep 5

echo "[5/5] 配置 Python 虚拟环境..."
PROJECT_DIR="$HOME/openclaw"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install neo4j openai

# Neo4j 连接配置
NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-neo4j}"

if [ -n "$NEO4J_URI" ] && [ "$NEO4J_URI" != "bolt://localhost:7687" ]; then
    echo "  使用远程 Neo4j: $NEO4J_URI"
else
    RUNNING=$(docker ps --filter "name=neo4j" --format "{{.Names}}" 2>/dev/null | head -1)
    if [ -n "$RUNNING" ]; then
        NEO4J_AUTH=$(docker inspect "$RUNNING" --format '{{.Config.Env}}' 2>/dev/null | tr ' ' '\n' | grep NEO4J_AUTH | cut -d'=' -f2)
        NEO4J_PASSWORD=$(echo "$NEO4J_AUTH" | cut -d'/' -f2)
    fi
    NEO4J_URI="bolt://localhost:7687"
fi

cat > .env << EOF
DEEPSEEK_API_KEY=your-api-key-here
NEO4J_URI=${NEO4J_URI}
NEO4J_USER=${NEO4J_USER}
NEO4J_PASSWORD=${NEO4J_PASSWORD}
EOF

echo ""
echo "========================================"
echo "安装完成!"
echo "========================================"
echo "控制台: http://localhost:7474"
echo ""
echo "远程 Neo4j 配置示例:"
echo "  NEO4J_URI=bolt://192.168.1.100:7687 \\"
echo "  NEO4J_PASSWORD=your_password \\"
echo "  python /home/program/graph_enable_ability/openclaw_neo4j_demo.py"
echo ""
echo "带参数运行: $0 --run"

if [ "$1" = "--run" ] || [ "$1" = "-r" ]; then
    echo ""
    echo "========================================"
    echo "启动 OpenClaw 对话 Demo..."
    echo "========================================"
    read -p "输入 API Key: " user_api_key
    read -p "Neo4j URI (直接回车使用本地): " input_neo4j_uri
    [ -z "$input_neo4j_uri" ] && input_neo4j_uri="bolt://localhost:7687"
    
    [ -n "$user_api_key" ] && export DEEPSEEK_API_KEY="$user_api_key"
    export NEO4J_URI="$input_neo4j_uri"
    export NEO4J_PASSWORD="$NEO4J_PASSWORD"
    
    cat > "$PROJECT_DIR/.env" << ENVEOF
DEEPSEEK_API_KEY=${user_api_key}
NEO4J_URI=${input_neo4j_uri}
NEO4J_USER=neo4j
NEO4J_PASSWORD=${NEO4J_PASSWORD}
ENVEOF
    
    source venv/bin/activate
    cd /home/program/graph_enable_ability
    python openclaw_neo4j_demo.py
    exit 0
fi