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

# 添加 repository - 只使用 stable latest（5.0 已不可用）
echo "deb [signed-by=/usr/share/keyrings/neo4j.gpg] https://debian.neo4j.com stable latest" | $SUDO tee /etc/apt/sources.list.d/neo4j.list

# 允许 apt update 失败继续，但只关注 Neo4j
$SUDO apt update -o Dir::Etc::sourcelist="sources.list.d/neo4j.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="false" 2>/dev/null || true

# -------------------------------------------------------------------------
# 3. 安装 Neo4j
# -------------------------------------------------------------------------
echo "[3/6] 安装 Neo4j Community Edition..."

# 尝试通过 apt 安装，如果失败则使用备用方案
if $SUDO apt install -y neo4j 2>/dev/null; then
    echo "  Neo4j 通过 apt 安装成功"
else
    echo "  apt 安装失败，尝试使用 Docker..."
    
    # 检查并安装 Docker（如果未安装）
    if ! command -v docker &> /dev/null; then
        echo "  安装 Docker..."
        $SUDO apt install -y docker.io 2>/dev/null || true
    fi
    
    # 如果 Docker 可用，使用 Docker 启动 Neo4j
    if command -v docker &> /dev/null; then
        docker run -d --name neo4j \
            -p 7474:7474 -p 7687:7687 \
            -e NEO4J_AUTH=neo4j/neo4j \
            -e NEO4J_PLUGINS='["apoc"]' \
            neo4j:5 || true
        echo "  Neo4j Docker 容器已启动"
    else
        echo "  无法安装 Neo4j，请手动安装或使用 Docker"
        exit 1
    fi
fi

# -------------------------------------------------------------------------
# 4. 配置 Neo4j
# -------------------------------------------------------------------------
echo "[4/6] 配置 Neo4j..."

# 检测是否使用 Docker
if command -v docker &> /dev/null && docker ps 2>/dev/null | grep -q neo4j; then
    echo "  检测到 Neo4j Docker 容器，跳过配置步骤"
    NEO4J_IS_DOCKER=true
else
    NEO4J_IS_DOCKER=false
    
    # 允许远程访问
    $SUDO sed -i 's/#server.default_listen_address=0.0.0.0/server.default_listen_address=0.0.0.0/' /etc/neo4j/neo4j.conf 2>/dev/null || true
    
    # 关闭增强监控（开发环境）
    $SUDO sed -i 's/#dbms.security.procedures.unrestricted=.*/dbms.security.procedures.unrestricted=apoc.*/' /etc/neo4j/neo4j.conf 2>/dev/null || true
    
    # 启用 APOC
    $SUDO sed -i 's/#dbms.security.procedures.unallowed=.*/dbms.security.procedures.unallowed=apoc.*/' /etc/neo4j/neo4j.conf 2>/dev/null || true
fi

# -------------------------------------------------------------------------
# 5. 启动 Neo4j
# -------------------------------------------------------------------------
echo "[5/6] 启动 Neo4j 服务..."

if [ "$NEO4J_IS_DOCKER" = "true" ]; then
    docker start neo4j 2>/dev/null || true
    sleep 5
    echo "  Neo4j Docker 容器已启动"
else
    $SUDO systemctl enable neo4j 2>/dev/null || true
    $SUDO systemctl start neo4j 2>/dev/null || true
    sleep 5
    
    if $SUDO systemctl is-active --quiet neo4j 2>/dev/null; then
        echo "  Neo4j 已启动"
    else
        echo "  警告: Neo4j 启动可能失败"
    fi
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
# 检查是否需要立即运行
# -------------------------------------------------------------------------
if [ "$1" = "--run" ] || [ "$1" = "-r" ]; then
    echo ""
    echo "========================================"
    echo "启动 OpenClaw 对话 Demo..."
    echo "========================================"
    echo "请设置 DEEPSEEK_API_KEY 后按回车继续..."
    read -p "输入 API Key (或直接回车跳过): " user_api_key
    
    if [ -n "$user_api_key" ]; then
        export DEEPSEEK_API_KEY="$user_api_key"
    fi
    
    source venv/bin/activate
    cd /home/program/graph_enable_ability
    python openclaw_neo4j_demo.py
    exit 0
fi

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
echo "默认密码: neo4j"
echo ""
echo "快速启动:"
echo "  $0 --run          # 安装后直接运行 Demo"
echo ""
echo "或手动启动:"
echo "  cd $PROJECT_DIR"
echo "  source venv/bin/activate"
echo "  python /home/program/graph_enable_ability/openclaw_neo4j_demo.py"