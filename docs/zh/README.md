# TrulyMEM 文档

欢迎来到 TrulyMEM 项目中文文档。

> [Switch to English version](../en/README.md)

## 文档目录

| 文档 | 内容 |
|------|------|
| [architecture.md](architecture.md) | 系统架构和技术设计 |
| [quick_start.md](quick_start.md) | 完整启动指南与配置说明 |
| [memory.md](memory.md) | 内部记忆工作机制 |
| [persona.md](persona.md) | 人设图机制 |
| [working_memory.md](working_memory.md) | 连续性任务处理机制 |
| [api.md](api.md) | 后端 API 接口文档（供扩展开发） |
| [prompts.md](prompts.md) | 提示词管理模块 |

## 项目简介

TrulyMEM (TrueHumanMEM) 是一个让 AI 拥有长期记忆能力的图记忆系统，通过图数据库存储实体关系，让 AI 能够像人类一样记忆、回忆和管理信息。

## 核心特性

- **长期记忆存储**: 基于 SQLite 内嵌图数据库，开箱即用
- **人设图机制**: 支持角色扮演和性格设定
- **工作记忆链**: 维持对话连贯性的任务跟踪机制
- **TUI 与后端分离**: 多线程 Queue 通信
- **键盘驱动 TUI**: 无需鼠标，全键盘操作
- **跨平台支持**: Windows / Linux / macOS
- **独立部署**: 支持打包为可执行文件