# TrulyMEM - TrueHumanMEM

<p align="center">
  <img src="pic/image.png" alt="TrulyMEM Logo" width="200">
</p>

> **📜 开源协议**: [GNU General Public License v3.0 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0)

> **English**: [README_EN.md](./README_EN.md)

**让 AI 拥有自知、可塑、有分寸感的长期记忆** — *The More Human Choice.*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 一句话

TrulyMEM 将记忆权交还给 LLM。通过图数据库（三元组）替代传统 messages 数组，让 LLM 自主决定记什么、忘什么。

---

## 快速开始

```bash
python trulymem_entry.py    # 从源码
./dist/TrulyMEM             # 打包后
```

首次启动 → TUI 登录页面 → 创建/登录账号 → 按 **F2** 配置 API Key → 开始聊天

📖 **详细启动文档**: [docs/zh/quick_start.md](docs/zh/quick_start.md)

---

## 主要特性

| 特性 | 说明 |
|------|------|
| 🧠 **图记忆** | 三元组存储，LLM 自主推理跳转 |
| 🔐 **多用户** | 用户隔离 + Admin/User 角色权限 |
| 🌐 **Web 可视化** | 内嵌 Flask 服务（线程模式），实时浏览知识图谱 |
| 🎮 **TUI 界面** | Textual 终端界面，F2 配置面板 |
| 📦 **单文件打包** | PyInstaller 打包，Web 服务内嵌于主二进制 |

---

## 文档索引

| 文档 | 内容 |
|------|------|
| [docs/zh/quick_start.md](docs/zh/quick_start.md) | 🔥 **完整启动指南**（含 Web、多用户、打包） |
| [docs/zh/architecture.md](docs/zh/architecture.md) | 系统架构和技术设计 |
| [docs/zh/memory.md](docs/zh/memory.md) | 内部记忆工作机制 |
| [docs/zh/persona.md](docs/zh/persona.md) | 人设图机制 |
| [docs/zh/api.md](docs/zh/api.md) | 后端 API 接口 |
| [docs/zh/prompts.md](docs/zh/prompts.md) | 提示词管理模块 |

---

## 特别鸣谢

- [Prof. Meiting Wang](https://www.xxmu.edu.cn/yxgcxy/info/1260/4252.htm) — 学术指导
- [逝水秋生白](https://atomgit.com/cenber) — 架构支持
- anzhitinglan — 测试资源支持
- 崔莉萍老师 — 理论指导
- Annie — 专业指导
- 王梓沣、马悦华、隆梦婷 — 神经科学理论支持

---

## 许可证

GNU General Public License v3.0 (GPLv3)
