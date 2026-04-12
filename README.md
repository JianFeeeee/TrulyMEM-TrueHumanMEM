# TrulyMEM - TrueHumanMEM

> **📜 开源协议**: [GNU General Public License v3.0 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0)  
> 本项目自由开源，可自由使用、修改和分发，但修改后的作品必须以相同许可证发布。

**让 AI 拥有自知、可塑、有分寸感的长期记忆**

*The More Human Choice.*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

---

## 简介

TrulyMEM (TrueHumanMEM) 是一个让 AI 拥有长期记忆能力的图记忆系统。通过 SQLite 内嵌图数据库存储实体关系，让 AI 能够像人类一样记忆、回忆和管理信息。

### 核心特性

- 🧠 **长期记忆** - 基于 SQLite 图数据库的持久化存储，开箱即用
- 🎭 **人设图机制** - AI 角色保持和角色扮演支持
- 🔗 **工作记忆链** - 维持对话连贯性的任务跟踪机制
- 🖥️ **现代化 TUI** - 基于 Textual 框架的终端用户界面，键盘驱动
- 💾 **内嵌数据库** - SQLite 实现，无需 Docker/Neo4j
- 📦 **独立部署** - 支持打包为独立可执行文件
- 🌍 **跨平台** - 支持 Windows/Linux/macOS

---

## 快速开始

### 方式一：打包后的可执行文件

```bash
# Windows: TrulyMEM.exe
# Linux/macOS: TrulyMEM
chmod +x TrulyMEM
./TrulyMEM
```

### 方式二：从源码运行

```bash
git clone <repo-url>
cd TrulyMEM-TrueHumanMEM

pip install -r requirements.txt

python trulymem_entry.py
```

### 配置

1. 按 **F2** 展开侧边栏
2. 输入 **API Key**（支持 DeepSeek、OpenAI 等兼容 API）
3. 按 **Enter** 保存配置
4. 开始对话！

---

## 功能说明

### 记忆管理工具

| 工具 | 功能 | 说明 |
|------|------|------|
| `memory_recall` | 检索记忆 | 根据意图查询相关记忆 |
| `memory_commit` | 写入记忆 | 将信息存储为图结构 |
| `memory_purge` | 删除记忆 | 删除过期或错误信息 |
| `memory_introspect` | 查看状态 | 查看记忆系统状态 |
| `memory_archive` | 归档记忆 | 归档旧记忆 |
| `memory_cleanup` | 清理数据 | 清理无效数据 |

### 人设工具

| 工具 | 功能 | 说明 |
|------|------|------|
| `persona_update` | 更新人设 | 修改 AI 的角色、性格、语气 |
| `persona_clear` | 清除人设 | 恢复默认身份 |

### 任务工具（工作记忆链）

| 工具 | 功能 | 说明 |
|------|------|------|
| `task_create` | 创建任务 | 跟踪连续性任务 |
| `task_set_state` | 设置状态 | 更新任务状态 |
| `task_delete` | 删除任务 | 清理完成任务 |
| `task_link_info` | 关联信息 | 连接任务与记忆 |

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| F1 | 帮助 |
| F2 | 切换侧边栏 |
| F3 | 工具详情 |
| F4 | 聚焦查询框 |
| F5 | 清屏 |
| F6 | 退出 |

---

## 项目结构

```
TrulyMEM-TrueHumanMEM/
├── trulymem_entry.py    # 入口：先启动 core → 再启动 ui
├── core/               # 后端/业务逻辑
│   ├── __init__.py
│   ├── server.py       # BackendServer (多线程)
│   ├── client.py      # BackendClient
│   ├── embedded_db.py # SQLite 图数据库
│   ├── graph_client.py
│   ├── tool_executor.py
│   ├── tool_limiter.py
│   ├── memory_tools.py
│   ├── prompts/
│   └── tools/        # TOOLS 定义
├── ui/               # TUI 显示层
│   ├── __init__.py
│   ├── app.py
│   ├── widgets/
│   ├── handlers/
│   ├── models/
│   ├── services/
│   └── styles/
└── tests/            # 测试 (38 tests)
```

---

## 技术栈

- **Python 3.8+** - 编程语言
- **Textual** - TUI 框架
- **SQLite** - 内嵌图数据库
- **OpenAI SDK** - API 调用（兼容 DeepSeek）

---

## 架构说明

### TUI 与后端通信

```
trulymem_entry.py
    │
    ├─ 1. BackendServer.start() → 启动独立线程
    │
    ├─ 2. GraphMemoryApp(backend_server=server)
    │
    └─ 3. BackendClient ← Queue → BackendServer
```

- **core/** - 业务逻辑（数据库、API调用、工具执行）
- **ui/** - 显示逻辑（Textual 组件）
- 多线程 Queue 通信解耦

---

## 开发指南

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt

pytest tests/
```

---

## 许可证

本项目采用 **GNU General Public License v3.0 (GPLv3)** 许可证开源。

详见 [LICENSE](LICENSE) 文件。

> **⚠️ 使用本项目即表示您同意：**
> - 可以自由使用、修改和分发
> - 必须保留版权声明和许可证
> - 修改后的作品必须以 GPLv3 许可证发布
> - 必须提供源代码

---

## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 文档

更多文档见 [docs/](docs/) 目录：

- [架构设计](docs/架构.md) - 系统架构和技术设计
- [快速开始](docs/一键启动指南.md) - 启动指南
- [工作记忆链机制说明](docs/工作记忆链机制说明.md) - 连续性任务处理