# TrulyMEM - TrueHumanMEM

<p align="center">
  <img src="pic/image.png" alt="TrulyMEM Logo" width="200">
</p>

> **📜 开源协议**: [GNU General Public License v3.0 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0)  
> 本项目自由开源，可自由使用、修改和分发，但修改后的作品必须以相同许可证发布。

> **English**: [Switch to English version](./README_EN.md)

**让 AI 拥有自知、可塑、有分寸感的长期记忆**

*The More Human Choice.*


[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()
[![Branch](https://img.shields.io/badge/branch-main-orange.svg)]()

---

## 故事的开头

行业普遍认为，LLM 海量参数让其涌现了智能。但这个智能是「死的」——它不会真的记住，也不理解「记住」的概念。它输出的一切，都是当前输入的全部文本经历无数次前向传播计算出的概率最优解。LLM 不会因为某次对话意识到错误而去修正权重，也无法因此针对模型进行一次反向传播。它的意识是被冻结的，展现出的智能只是冻结的意识的回响。

现在的所谓记忆系统，只是将记忆外化，让「系统」去替 LLM 记住。或者就是粗暴地将一切上下文文本丢给 LLM。这就是对模型输入的浪费。

**TrulyMEM 想，既然 LLM 无法实时纠正模型权重，为什么不把记忆权交还给 LLM 呢？**

我们提供一系列机制，让 LLM 决定它要记住什么、遗忘，什么是重点、什么是糟粕。LLM 推理的过程，就是思考的过程，也是回忆的过程。完全摒弃传统的 messages 数组上下文，将全部记忆以**三元组（图）**的形式保存在图数据库中。在 LLM 思考时，可以按照图数据库的链接自主跳转、联想相关关系，让 LLM 自然地实现联想与回忆。

赋予 LLM 真正的记忆。

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

## 文档索引

详细技术文档请参阅 [docs/zh/](docs/zh/) 目录：

| 文档 | 内容 |
|------|------|
| [docs/zh/architecture.md](docs/zh/architecture.md) | 系统架构和技术设计 |
| [docs/zh/quick_start.md](docs/zh/quick_start.md) | 完整启动指南与配置说明 |
| [docs/zh/memory.md](docs/zh/memory.md) | 内部记忆工作机制 |
| [docs/zh/persona.md](docs/zh/persona.md) | 人设图机制 |
| [docs/zh/working_memory.md](docs/zh/working_memory.md) | 连续性任务处理机制 |
| [docs/zh/api.md](docs/zh/api.md) | 后端 API 接口（供扩展开发） |
| [docs/zh/prompts.md](docs/zh/prompts.md) | 提示词管理模块 |

---

## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 许可证

本项目采用 **GNU General Public License v3.0 (GPLv3)** 许可证开源。  
详见 [LICENSE](LICENSE) 文件。

---

## 特别鸣谢

- [Prof. Meiting Wang](https://www.xxmu.edu.cn/yxgcxy/info/1260/4252.htm) — 学术指导
- [逝水秋生白](https://atomgit.com/cenber) — 架构支持
- anzhitinglan — 测试资源支持
- 崔莉萍老师 — 理论指导
- Annie — 专业指导
- 王梓沣、马悦华、隆梦婷 — 神经科学理论支持