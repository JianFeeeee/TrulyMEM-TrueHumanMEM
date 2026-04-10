# TrueHumanMEM - Graph Memory TUI

> The More Human Choice.

一个让 AI 拥有自知、可塑、有分寸感长期记忆的图记忆系统，配备现代化终端用户界面。

## ✨ 特性

- 🖥️ **现代化TUI界面** - 基于Textual框架的终端界面
- 💾 **内嵌数据库** - SQLite实现，无需Docker/Neo4j
- 🌐 **Web接口** - 支持浏览器访问
- 🚀 **一键启动** - 3步骤完成，30秒启动
- 🌍 **跨平台** - 支持Windows/Linux/macOS
- 📊 **实时可视化** - 消息、工具调用实时显示
- 🔧 **完整功能** - 记忆检索、写入、删除、归档

## 📖 目录

- [快速开始](#快速开始)
- [使用方法](#使用方法)
- [功能说明](#功能说明)
- [API接口](#api接口)
- [配置说明](#配置说明)
- [开发指南](#开发指南)

---

## 快速开始

### 前置要求

- **Python 3.8+**
- **DeepSeek API Key**（或兼容OpenAI格式的API）

### 一键启动

#### Windows
```bash
# 双击运行
start.bat

# 或命令行
python start.py
```

#### Linux / macOS
```bash
# Shell脚本
chmod +x start.sh
./start.sh

# 或Python
python3 start.py
```

### 启动流程

```
[Step 1/3] 检查 Python
[Step 2/3] 设置虚拟环境
[Step 3/3] 启动应用

✅ 系统初始化成功！
• 数据库: 内嵌SQLite (graph_memory.db)
• API Key: 未配置
```

---

## 使用方法

### 1. 配置 API Key

1. 按 **F2** 展开侧边栏
2. 点击 **"配置"**
3. 输入你的 **DeepSeek API Key**
4. 按 **Enter** 保存

### 2. 开始对话

- 输入消息
- 按 **Enter** 发送
- 查看AI响应和工具调用

### 3. 快捷键

| 快捷键 | 功能 |
|--------|------|
| F1 | 帮助 |
| F2 | 切换侧边栏 |
| F3 | 工具详情 |
| F4 | 查询框 |
| F5 | 清屏 |
| F6 | 退出 |

---

## 功能说明

### 记忆管理工具

| 工具 | 功能 | 参数 |
|------|------|------|
| memory_recall | 检索记忆 | query_intent, depth |
| memory_commit | 写入记忆 | triplets, confidence |
| memory_purge | 删除记忆 | criteria, mode |
| memory_introspect | 查看状态 | - |
| memory_archive | 归档记忆 | days |
| memory_cleanup | 清理数据 | dry_run |

### 数据库

**内嵌SQLite数据库：**
- 文件：`graph_memory.db`
- 无需配置
- 自动创建
- 本地存储

**数据结构：**
- 实体（entities）：name, type, mention_count
- 关系（relations）：source, target, type, confidence, status

---

## API接口

### Web接口

启动后访问：`http://localhost:5000`

### REST API

```bash
# 检索记忆
POST /api/memory/recall
{
  "query_intent": "Python,AI"
}

# 写入记忆
POST /api/memory/commit
{
  "triplets": [
    {"subject": "用户", "relation": "喜欢", "object": "Python"}
  ]
}

# 查看状态
GET /api/memory/introspect

# 获取配置
GET /api/config
```

---

## 配置说明

### 环境变量

创建 `.env` 文件：

```bash
# API配置
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-chat

# 数据库配置（可选）
USE_EMBEDDED_DB=true
```

### 切换数据库

**使用内嵌数据库（默认）：**
```bash
USE_EMBEDDED_DB=true
```

**使用Neo4j（需要Docker）：**
```bash
USE_EMBEDDED_DB=false
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=graphmemory123
```

---

## 开发指南

### 项目结构

```
graph_enable_ability/
├── graph_memory_tui/      # TUI应用
│   ├── core/              # 核心逻辑
│   │   ├── embedded_db.py # 内嵌数据库
│   │   └── imports.py
│   ├── web/               # Web接口
│   ├── widgets/           # UI组件
│   ├── styles/            # 样式
│   └── app.py
├── tests/                 # 测试
├── docs/                  # 文档
├── start.bat              # Windows启动
├── start.sh               # Linux/macOS启动
└── start.py               # 跨平台启动
```

### 运行测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/
```

### 开发模式

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 运行应用
python -m graph_memory_tui.main
```

---

## 常见问题

### Q: 启动时显示"API Key 未配置"？

**A:** 按F2打开侧边栏，在配置区输入API Key，按Enter保存。

### Q: 数据保存在哪里？

**A:** 数据保存在 `graph_memory.db` 文件中，可以备份或迁移。

### Q: 如何查看数据库内容？

**A:** 使用SQLite工具打开 `graph_memory.db`，或使用 `memory_introspect` 工具。

### Q: 支持哪些API？

**A:** 支持所有兼容OpenAI格式的API，如DeepSeek、OpenAI等。

---

## 技术栈

- **Python 3.8+** - 编程语言
- **Textual** - TUI框架
- **SQLite** - 内嵌数据库
- **Flask** - Web框架
- **OpenAI SDK** - API调用

---

## 许可证

MIT License

---

## 贡献

欢迎提交Issue和Pull Request！

---

**TrueHumanMEM —— 让 AI 的记忆方式，更像人。**
