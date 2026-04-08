#!/bin/bash
# Neo4j 一键安装脚本 - CentOS/RHEL/Fedora

set -e

echo "========================================"
echo "Neo4j 一键安装脚本 - CentOS/RHEL/Fedora"
echo "========================================"

if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

# 1. 检查 Java
echo "[1/5] 检查 Java 环境..."
if command -v java &> /dev/null; then
    echo "  已安装: $(java -version 2>&1 | head -n 1)"
else
    echo "  安装 OpenJDK 17..."
    $SUDO yum install -y java-17-openjdk-headless
fi

# 2. 添加 Neo4j 源
echo "[2/5] 添加 Neo4j 源..."
$SUDO cat > /etc/yum.repos.d/neo4j.repo << 'EOF'
[neo4j]
name=Neo4j Repository
baseurl=https://yum.neo4j.com/stable
enabled=1
gpgcheck=1
gpgkey=https://debian.neo4j.com/neotechnology.gpg.key
EOF

# 3. 安装
echo "[3/5] 安装 Neo4j..."
$SUDO yum install -y neo4j

# 4. 配置
echo "[4/5] 配置 Neo4j..."
$SUDO sed -i 's/#server.default_listen_address=0.0.0.0/server.default_listen_address=0.0.0.0/' /etc/neo4j/neo4j.conf

# 5. 启动
echo "[5/5] 启动 Neo4j..."
$SUDO systemctl enable neo4j
$SUDO systemctl start neo4j
sleep 3

# 6. 配置 Python 虚拟环境
echo "[6/6] 配置 Python 虚拟环境..."
PROJECT_DIR="$HOME/openclaw"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
python3 -m venv venv
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
echo "安装完成!"
echo "========================================"
echo "控制台: http://localhost:7474"
echo "连接: cypher-shell -u neo4j -p neo4j"
echo ""
echo "启动对话:"
echo "  cd $PROJECT_DIR && source venv/bin/activate"
echo "  python -m openclaw_neo4j_demo"