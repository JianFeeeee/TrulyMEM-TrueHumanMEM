# Graph Memory Demo

纯图数据库记忆存储 Demo - 验证无上下文对话系统

## 概述

本 Demo 验证使用 Neo4j 图数据库替代传统上下文窗口的可行性。每轮对话通过 DeepSeek API Tool Calls 实现自主记忆存取。

## 核心工具

| 工具 | 功能 |
|------|------|
| memory_recall | 检索历史记忆 |
| memory_commit | 写入记忆（三元组） |
| memory_purge | 修正/删除记忆 |
| memory_introspect | 查看会话状态 |
| memory_archive | 归档旧关系 |
| memory_cleanup | 物理清理 |

## 快速开始

### 1. 安装 Neo4j

```bash
# Ubuntu/Debian
bash scripts/install_neo4j_ubuntu.sh

# CentOS/RHEL
bash scripts/install_neo4j_centos.sh

# openEuler
bash scripts/install_neo4j_openeuler.sh

# Docker
bash scripts/start_neo4j_docker.sh
```

### 2. 配置环境变量

```bash
export DEEPSEEK_API_KEY="your-api-key"
export NEO4J_PASSWORD="neo4j"
```

### 3. 运行 Demo

```bash
python graph_memory_demo.py
```

### 4. Docker 一键部署

```bash
cd docker
./start.sh
```

## 架构说明

- **无上下文**: 每次请求仅带当前输入，不含历史消息
- **图数据库**: 所有记忆存储在 Neo4j 图中
- **自主决策**: 模型自主判断何时查询/写入记忆

## 文件结构

```
.
├── graph_memory_demo.py     # 主程序
├── scripts/                # 各发行版安装脚本
│   ├── install_neo4j_ubuntu.sh
│   ├── install_neo4j_centos.sh
│   ├── install_neo4j_openeuler.sh
│   └── start_neo4j_docker.sh
├── docker/                 # Docker 部署
│   ├── docker-compose.yml
│   ├── start.sh
│   └── .env.example
└── README.md
```

## Neo4j 配置

- HTTP: http://localhost:7474
- Bolt: bolt://localhost:7687
- 用户: neo4j / (设置密码)

## 测试验证

```bash
# 测试 Neo4j 连接
cypher-shell -u neo4j -p your_password "MATCH (n) RETURN count(n)"
```
