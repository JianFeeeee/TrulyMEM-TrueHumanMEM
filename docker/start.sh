#!/bin/bash
# OpenClaw Docker 一键启动脚本

set -e

echo "========================================"
echo "OpenClaw Docker 一键启动"
echo "========================================"

# 检查 Docker 和 Docker Compose
if ! command -v docker &> /dev/null; then
    echo "Error: Docker 未安装"
    exit 1
fi

# 检查 docker compose 插件或 docker-compose
DOCKER_COMPOSE="docker compose"
if ! docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
    if ! command -v docker-compose &> /dev/null; then
        echo "Error: Docker Compose 未安装"
        exit 1
    fi
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR/docker"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo ""
    read -p "请输入 DeepSeek API Key: " user_api_key
    [ -z "$user_api_key" ] && user_api_key="your-api-key-here"
    
    cat > .env << EOF
DEEPSEEK_API_KEY=${user_api_key}
EOF
    echo "  已保存配置到 .env"
fi

# 启动服务
echo ""
echo "启动 Neo4j 和 OpenClaw 应用..."
$DOCKER_COMPOSE up -d

# 等待 Neo4j 就绪
echo "等待 Neo4j 启动..."
sleep 10

# 检查状态
echo ""
echo "========================================"
echo "启动完成!"
echo "========================================"
echo ""
echo "服务状态:"
$DOCKER_COMPOSE ps
echo ""
echo "访问地址:"
echo "  Neo4j Browser: http://localhost:7474"
echo "  Neo4j 用户: neo4j / openclaw123"
echo ""
echo "停止服务: docker compose down"
echo "查看日志: docker compose logs -f"