# TrulyMEM 文档

欢迎来到 TrulyMEM 项目文档。

## 文档目录

| 文档 | 内容 |
|------|------|
| [架构设计](架构.md) | 系统架构和技术设计 |
| [快速开始](一键启动指南.md) | 完整启动指南与配置说明 |
| [记忆机制](记忆机制.md) | 内部记忆工作机制、人设图、工作记忆链 |
| [工作记忆链](工作记忆链机制说明.md) | 连续性任务处理机制 |
| [BackendServer API](api.md) | 后端 API 接口文档（供扩展开发） |
| [提示词管理](prompts.md) | 提示词管理模块 |

## English Documentation

| Document | Content |
|----------|---------|
| [Architecture](架构_EN.md) | System architecture and technical design |
| [Quick Start](一键启动指南_EN.md) | Complete startup guide and configuration |
| [Memory Mechanism](记忆机制_EN.md) | Internal memory working mechanism |
| [Working Memory Chain](工作记忆链_EN.md) | Continuous task handling |
| [BackendServer API](api_EN.md) | Backend API reference |
| [Prompt Manager](prompts_EN.md) | Prompt management module |

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