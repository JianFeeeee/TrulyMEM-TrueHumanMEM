# TrulyMEM - TrueHumanMEM

**让 AI 拥有自知、可塑、有分寸感的长期记忆**

*The More Human Choice.*

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/yourusername/trulymem)

---

## 简介

TrulyMEM（TrueHumanMEM）是一个让 AI 拥有长期记忆能力的图记忆系统。通过图数据库存储实体关系，让AI能够像人类一样记忆、回忆和管理信息。

### 核心特性

- 🧠 **长期记忆** - 基于图数据库的持久化记忆存储
- 🎭 **人设图机制** - AI角色保持和角色扮演支持
- 🖥️ **现代化TUI** - 基于Textual框架的终端用户界面
- 💾 **内嵌数据库** - SQLite实现，无需Docker/Neo4j
- 🌐 **Web接口** - 支持浏览器访问
- 🚀 **流式显示** - 实时显示AI响应，减少等待
- 📦 **独立部署** - 支持打包为独立可执行文件
- 🌍 **跨平台** - 支持Windows/Linux/macOS

---

## 快速开始

### 方式一：使用可执行文件（推荐）

**Windows:**
```bash
# 下载 TrulyMEM.exe
# 双击运行或命令行执行
./TrulyMEM.exe
```

**Linux:**
```bash
# 下载 TrulyMEM
chmod +x TrulyMEM
./TrulyMEM
```

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/yourusername/trulymem.git
cd trulymem

# 安装依赖
pip install -r requirements.txt

# 运行应用
python -m graph_memory_tui.main
```

### 配置

1. 按 **F2** 展开侧边栏
2. 输入 **API Key**（支持DeepSeek、OpenAI等）
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

### 人设图机制

AI会在每轮对话前查询人设图，严格按照人设回复，确保角色一致性。

**使用示例：**
```
用户：以猫娘的语气跟我说话
AI：喵~好的主人！我会用可爱的猫娘语气跟你说话的喵！(≧ω≦)
```

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| F1 | 帮助 |
| F2 | 切换侧边栏 |
| F3 | 工具详情 |
| F4 | 查询框 |
| F5 | 清屏 |
| F6 | 退出 |

---

## 项目结构

```
trulymem/
├── graph_memory_tui/      # TUI应用
│   ├── core/              # 核心逻辑
│   ├── handlers/          # 事件处理
│   ├── models/            # 数据模型
│   ├── services/          # 服务层
│   ├── widgets/           # UI组件
│   └── styles/            # 样式文件
├── docs/                  # 文档
├── tests/                 # 测试
├── requirements.txt       # 依赖清单
├── LICENSE               # 许可证
└── README.md             # 说明文档
```

---

## 技术栈

- **Python 3.8+** - 编程语言
- **Textual** - TUI框架
- **SQLite** - 内嵌数据库
- **Flask** - Web框架
- **OpenAI SDK** - API调用

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

### 许可证要点：

- ✅ 可以自由使用、修改和分发
- ✅ 必须保留版权声明和许可证
- ✅ 修改后的作品必须以相同许可证发布
- ✅ 必须提供源代码

---

## 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 作者

**jianf** - 项目设计与开发

---

## 致谢

感谢所有为这个项目做出贡献的开发者和用户。

---

<div align="center">

**TrulyMEM —— 让 AI 的记忆方式，更像人。**

*Made with ❤️ by jianf*

</div>
