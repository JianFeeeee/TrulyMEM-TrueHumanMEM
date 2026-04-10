#!/bin/bash

echo ""
echo "========================================"
echo "  Graph Memory TUI - One-Click Start"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check and Start Docker
echo "[Step 1/5] Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR] Docker not found!${NC}"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo -e "${YELLOW}[INFO] Docker daemon not running, trying to start...${NC}"
    
    # Try to start Docker daemon
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        open -a Docker
    else
        # Linux
        sudo systemctl start docker
    fi
    
    # Wait for Docker to start
    echo "[INFO] Waiting for Docker to start..."
    count=0
    while ! docker info &> /dev/null; do
        sleep 2
        ((count++))
        if [ $count -gt 30 ]; then
            echo -e "${RED}[ERROR] Docker failed to start after 60 seconds${NC}"
            exit 1
        fi
        echo "[INFO] Still waiting... ($count/30)"
    done
    echo -e "${GREEN}[OK] Docker started successfully${NC}"
else
    echo -e "${GREEN}[OK] Docker is running${NC}"
fi

# Step 2: Start Neo4j
echo ""
echo "[Step 2/5] Starting Neo4j database..."

# Check if neo4j container exists
if ! docker ps -a | grep -q neo4j; then
    echo "[INFO] Creating Neo4j container..."
    docker run -d \
        --name neo4j \
        -p 7474:7474 \
        -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/graphmemory123 \
        -e NEO4J_PLUGINS='["apoc"]' \
        neo4j:latest
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create Neo4j container${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK] Neo4j container created${NC}"
else
    # Check if running
    if ! docker ps | grep -q neo4j; then
        echo "[INFO] Starting existing Neo4j container..."
        docker start neo4j
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}[ERROR] Failed to start Neo4j container${NC}"
            exit 1
        fi
        echo -e "${GREEN}[OK] Neo4j container started${NC}"
    else
        echo -e "${GREEN}[OK] Neo4j container already running${NC}"
    fi
fi

# Wait for Neo4j to be ready
echo "[INFO] Waiting for Neo4j to be ready..."
sleep 5

# Step 3: Check Python
echo ""
echo "[Step 3/5] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR] Python3 not found!${NC}"
    echo "Please install Python 3.8+ from: https://www.python.org/downloads/"
    exit 1
fi
echo -e "${GREEN}[OK] Python found${NC}"

# Step 4: Setup Virtual Environment
echo ""
echo "[Step 4/5] Setting up virtual environment..."

if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK] Virtual environment created${NC}"
else
    echo -e "${GREEN}[OK] Virtual environment exists${NC}"
fi

# Activate venv
source venv/bin/activate

# Check dependencies
if ! pip show textual &> /dev/null; then
    echo "[INFO] Installing dependencies..."
    pip install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR] Failed to install dependencies${NC}"
        exit 1
    fi
    echo -e "${GREEN}[OK] Dependencies installed${NC}"
else
    echo -e "${GREEN}[OK] Dependencies already installed${NC}"
fi

# Step 5: Start Application
echo ""
echo "[Step 5/5] Starting Graph Memory TUI..."
echo ""
echo "========================================"
echo "  All systems ready!"
echo "========================================"
echo ""
echo "Neo4j Connection:"
echo "  - Browser: http://localhost:7474"
echo "  - Bolt:    bolt://localhost:7687"
echo "  - User:    neo4j"
echo "  - Pass:    graphmemory123"
echo ""
echo "Starting TUI application..."
echo ""

python -m graph_memory_tui.main

# Cleanup
deactivate

echo ""
echo "Application closed."
