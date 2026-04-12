# TrulyMEM - TrueHumanMEM

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

打包后会生成独立可执行文件，可直接运行：

```bash
# Windows: TrulyMEM.exe
# Linux/macOS: TrulyMEM
chmod +x TrulyMEM
./TrulyMEM
```

### 方式二：从源码运行

```bash
# 克隆仓库
git clone <repo-url>
cd TrulyMEM-TrueHumanMEM

# 安装依赖
pip install -r requirements.txt

# 运行应用
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
├── trulymem_entry.py          # 打包入口
├── graph_memory_tui/          # 核心应用
│   ├── app.py                 # TUI 主应用
│   ├── main.py                # 模块入口
│   ├── core/                  # 核心逻辑
│   │   ├── embedded_db.py     # SQLite 图数据库
│   │   ├── graph_client.py    # Neo4j 客户端（可选）
│   │   ├── imports.py         # 动态导入
│   │   ├── prompts/           # 提示词管理
│   │   └── tools/             # 工具定义
│   ├── models/                # 数据模型
│   ├── services/              # 服务层
│   ├── handlers/              # 事件处理
│   ├── widgets/                # TUI 组件
│   └── styles/                # 样式文件
├── tests/                      # 测试
├── docs/                       # 文档
├── requirements.txt           # 依赖清单
└── LICENSE                    # 许可证
```

---

## 技术栈

- **Python 3.8+** - 编程语言
- **Textual** - TUI 框架
- **SQLite** - 内嵌图数据库
- **OpenAI SDK** - API 调用（兼容 DeepSeek）

---

## 开发指南

### 环境设置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 运行测试

```bash
pytest tests/
```

### 打包应用

```bash
# Windows
python build_windows.bat

# Linux
bash build_linux.sh
```

---

## 许可证

本项目采用 **GNU General Public License v3.0 (GPLv3)** 许可证开源。

详见 [LICENSE](LICENSE) 文件。

### 许可证要点

- 可以自由使用、修改和分发
- 必须保留版权声明和许可证
- 修改后的作品必须以相同许可证发布
- 必须提供源代码

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
