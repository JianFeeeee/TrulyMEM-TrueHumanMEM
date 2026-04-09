# OpenClaw Docker 部署

一键启动 OpenClaw 纯图数据库对话 Demo。

## 快速开始

```bash
cd docker
chmod +x start.sh
./start.sh

# 或者直接使用 docker compose
docker compose up -d
```

## 前置要求

- Docker
- Docker Compose v2 (或 docker-compose)

## 启动后

- Neo4j Browser: http://localhost:7474
- 登录用户: neo4j / openclaw123
- 应用运行在终端交互模式

## 停止

```bash
cd docker
docker compose down
```

## 配置

编辑 `.env` 文件修改 DeepSeek API Key：
```
DEEPSEEK_API_KEY=sk-xxx
```

## 文件说明

```
docker/
├── docker-compose.yml   # 容器编排 (Neo4j + 应用)
├── start.sh            # 一键启动脚本
├── .env.example        # 环境变量模板
└── README.md           # 本文件
```