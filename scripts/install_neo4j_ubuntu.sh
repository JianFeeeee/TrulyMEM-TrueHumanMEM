#!/bin/bash
# =============================================================================
# Neo4j 一键安装配置脚本 - Ubuntu/Debian
# =============================================================================

set -e

echo "========================================"
echo "Neo4j 一键安装脚本 - Ubuntu/Debian"
echo "========================================"

# 检测是否为 root
if [ "$EUID" -eq 0 ]; then
    echo "[Info] Running as root"
    SUDO=""
else
    echo "[Info] Running as user, will use sudo"
    SUDO="sudo"
fi

# -------------------------------------------------------------------------
# 1. 检查 Java 环境
# -------------------------------------------------------------------------
echo "[1/6] 检查 Java 环境..."

if command -v java &> /dev/null; then
    java_version=$(java -version 2>&1 | head -n 1)
    echo "  已安装: $java_version"
else
    echo "  未检测到 Java，安装 OpenJDK 17..."
    $SUDO apt update
    $SUDO apt install -y openjdk-17-jre-headless
    echo "  Java 安装完成"
fi

# -------------------------------------------------------------------------
# 2. 添加 Neo4j apt 源
# -------------------------------------------------------------------------
echo "[2/6] 添加 Neo4j apt 源..."

# 安装依赖
$SUDO apt install -y curl gnupg

# 添加 GPG key
curl -fsSL https://debian.neo4j.com/neotechnology.gpg.key | $SUDO gpg --dearmor -o /usr/share/keyrings/neo4j.gpg

# 添加 repository
echo "deb [signed-by=/usr/share/keyrings/neo4j.gpg] https://debian.neo4j.com stable latest" | $SUDO tee /etc/apt/sources.list.d/neo4j.list
echo "deb [signed-by=/usr/share/keyrings/neo4j.gpg] https://debian.neo4j.com 5.0 latest" | $SUDO tee -a /etc/apt/sources.list.d/neo4j.list

$SUDO apt update

# -------------------------------------------------------------------------
# 3. 安装 Neo4j
# -------------------------------------------------------------------------
echo "[3/6] 安装 Neo4j Community Edition..."

# 安装 neo4j (会同时安装依赖)
$SUDO apt install -y neo4j

# -------------------------------------------------------------------------
# 4. 配置 Neo4j
# -------------------------------------------------------------------------
echo "[4/6] 配置 Neo4j..."

# 允许远程访问
$SUDO sed -i 's/#server.default_listen_address=0.0.0.0/server.default_listen_address=0.0.0.0/' /etc/neo4j/neo4j.conf

# 设置初始密码 (默认用户: neo4j)
# 如果需要设置密码，取消下面注释并修改密码
# echo "neo4j:你的密码" | $SUDO tee /etc/neo4j/neo4j-auth

# 关闭增强监控（开发环境）
$SUDO sed -i 's/#dbms.security.procedures.unrestricted=.*/dbms.security.procedures.unrestricted=apoc.*/' /etc/neo4j/neo4j.conf

# 启用 APOC
$SUDO sed -i 's/#dbms.security.procedures.unallowed=.*/dbms.security.procedures.unallowed=apoc.*/' /etc/neo4j/neo4j.conf

# -------------------------------------------------------------------------
# 5. 启动 Neo4j
# -------------------------------------------------------------------------
echo "[5/6] 启动 Neo4j 服务..."

$SUDO systemctl enable neo4j
$SUDO systemctl start neo4j

# 等待启动
sleep 5

# 检查状态
if $SUDO systemctl is-active --quiet neo4j; then
    echo "  Neo4j 已启动"
else
    echo "  警告: Neo4j 启动可能失败，请检查: sudo systemctl status neo4j"
fi

# -------------------------------------------------------------------------
# 6. 安装 Python 依赖
# -------------------------------------------------------------------------
echo "[6/6] 配置 Python 虚拟环境..."

# 创建项目目录和虚拟环境
PROJECT_DIR="$HOME/openclaw"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 创建虚拟环境（使用 virtualenv 以保证兼容性）
if ! command -v virtualenv &> /dev/null; then
    $SUDO apt install -y python3-virtualenv
fi
python3 -m virtualenv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install neo4j openai

# 创建环境变量文件
cat > .env << 'EOF'
DEEPSEEK_API_KEY=your-api-key-here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j
EOF

echo "  虚拟环境已创建: $PROJECT_DIR/venv"
echo "  激活: source $PROJECT_DIR/venv/bin/activate"

# -------------------------------------------------------------------------
# 完成
# -------------------------------------------------------------------------
echo ""
echo "========================================"
echo "安装完成!"
echo "========================================"
echo ""
echo "Neo4j 控制台: http://localhost:7474"
echo "默认用户: neo4j"
echo "初始密码: neo4j (首次登录需修改)"
echo ""
echo "启动对话:"
echo "  cd $PROJECT_DIR"
echo "  source venv/bin/activate"
echo "  python ~/openclaw_demo.py"
echo ""
echo "或直接运行 Demo:"
echo "  source $PROJECT_DIR/venv/bin/activate"
echo "  python /home/program/graph_enable_ability/openclaw_neo4j_demo.py"