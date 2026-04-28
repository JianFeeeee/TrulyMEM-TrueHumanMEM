# TrulyMEM 启动指南

## 运行方式

### 从源码运行

```bash
git clone <repo-url>
cd TrulyMEM-TrueHumanMEM

pip install -r requirements.txt

python trulymem_entry.py
```

### 打包后运行

打包后会生成可执行文件：

```bash
# Linux/macOS
chmod +x TrulyMEM
./TrulyMEM

# Windows
TrulyMEM.exe
```

## 系统要求

- **Python 3.8+**
- **API Key**（DeepSeek、OpenAI 或其他兼容 API）

## 首次配置

1. 运行应用
2. 按 **F2** 展开侧边栏
3. 输入 **API Key**、**模型**、**Base URL**
4. 按 **Enter** 保存

配置会自动保存到 `~/.trulymem/config.json`，下次启动自动加载。

### Web 可视化界面（可选）

TrulyMEM 提供 Web 星图可视化界面，支持实时浏览知识图谱：

```bash
# 启动 Web 服务
python web_api.py --port 4096
```

然后打开浏览器访问 `http://localhost:4096`。

**登录配置：**
1. 复制 `web_config.example.json` 为 `web_config.json`
2. 设置登录密码（使用 SHA256）和 secret key
3. Web 服务会自动读取该配置

默认端口 4096，可通过 `--port` 参数修改。

---

## 快捷键

| 按键 | 功能 |
|------|------|
| F1 | 帮助 |
| F2 | 切换侧边栏 |
| F3 | 工具详情 |
| F5 | 清屏 |
| F6 | 退出 |

## 数据存储

### 源码运行模式

| 数据 | 位置 |
|------|------|
| 图数据库 | 项目目录 `graph_memory.db` |
| 配置文件 | 项目目录 `config.json`（如存在） |
| 数据库格式 | SQLite |

### 打包运行模式

| 数据 | 位置 |
|------|------|
| 图数据库 | `~/.trulymem/graph_memory.db` |
| 配置文件 | `~/.trulymem/config.json` |
| 数据库格式 | SQLite |

> **说明**：后端统一管理配置。前端仅负责消息展示，配置修改通过后端持久化到文件系统。

## 架构说明

### 通信协议

UI 与后端通过 **Packet 协议** 通信：

```
UI (Textual TUI)
    ↓ BackendClient
Packet → queue.Queue → BackendServer (独立线程)
    ↓
处理请求 → 返回响应
```

### 配置管理

- **存储位置**: `~/.trulymem/config.json`
- **自动加载**: 启动时从文件读取配置
- **动态更新**: 运行时修改配置立即生效
- **持久化**: 修改后自动保存到文件

## 常见问题

### Python 未找到

安装 Python 3.8+：https://www.python.org/downloads/

### 依赖安装失败

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### API Key 无效

检查 API Key 格式，确保无多余空格。

## 开发命令

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/

# 打包
bash build/build_windows.bat   # Windows
bash build/build_linux.sh       # Linux
```