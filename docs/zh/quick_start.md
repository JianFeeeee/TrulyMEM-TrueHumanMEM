# TrulyMEM 启动指南

> **版本**: 多用户版 (v2) — 支持 TUI 登录、多用户隔离、Web 服务内嵌

---

## 运行方式

### 快速启动（推荐）

```bash
# 从源码
python trulymem_entry.py

# 或打包后
./dist/TrulyMEM
```

### 首次使用 —— 登录流程

首次启动会自动检查是否需要迁移旧数据，然后进入**登录页面**：

1. **新部署** → 直接输入用户名和密码创建账户（首个用户自动成为管理员）
2. **旧版升级** → 自动检测 `~/.trulymem/config.json`，引导设置用户名密码，迁移数据
3. **已有账户** → 直接登录进入聊天界面

> 💡 所有用户数据隔离存储：`~/.trulymem/{用户名}/`

### 聊天配置

登录后按 **F2** 展开右侧配置面板：

1. **API Key** — 必须（支持 DeepSeek、OpenAI 等）
2. **模型** — 可选，默认已配置
3. **Base URL** — 可选

配置自动保存，下次启动自动加载。

---

## Web 可视化界面

TrulyMEM 的 Web 服务现在**内嵌在主进程中**（无需独立启动子进程）。

### TUI 内启动（管理员专有）

管理员按 F2 打开右侧面板，勾选「启用 Web 服务」即可。

### 手动启动

```bash
python -m core.web_api --port 4096
# 访问 http://localhost:4096
```

### 首次访问流程

1. 浏览器打开 `http://localhost:4096`
2. **无用户** → 自动跳转至设置页，创建管理员账号
3. **有用户** → 跳转至登录页
4. 登录后进入星图可视化页面

### Web 功能

| 页面 | 访问权限 | 功能 |
|------|----------|------|
| 🌟 星图 | 所有已登录用户 | 浏览知识图谱三元组 |
| ⚙ 设置 | 所有已登录用户 | 修改密码 |
| 🧑‍💼 用户管理 | **仅管理员** | 添加/删除用户 |

---

## 多用户系统

### 目录结构

```
~/.trulymem/
├── trulymem.db          # 全局用户数据库（web_users 表）
├── .migrated            # 旧版迁移标记
├── admin/
│   ├── config.json      # 管理员配置
│   └── admin_graph.db   # 管理员知识图谱
└── user2/
    ├── config.json      # user2 配置
    └── user2_graph.db   # user2 知识图谱
```

### 角色体系

| 功能 | 普通用户 | 管理员 |
|------|---------|--------|
| 修改自己密码 | ✅ | ✅ |
| 配置 API Key / 模型 | ✅ | ✅ |
| Web 服务开关（TUI） | ❌ | ✅ |
| Web 登录凭据 | ❌ | ✅ |
| 查看用户列表 | ❌ | ✅ |
| 添加/删除用户 | ❌ | ✅ |

> ⚠️ 首个注册用户自动成为管理员。Web 设置页可添加新用户。

---

## 快捷键

| 按键 | 功能 |
|------|------|
| F1 | 帮助 |
| F2 | 切换侧边栏（配置面板） |
| F3 | 工具详情 |
| F5 | 清屏 |
| F6 | 退出 |

---

## 打包构建

```bash
# 安装依赖
pip install -r requirements.txt

# 构建（Linux / macOS）
pyinstaller --clean build/trulymem.spec
```

构建产出：`dist/TrulyMEM`（单文件，TUI + Web 服务均内嵌于同一二进制）

> 📦 从 v2 开始，Web 服务作为线程嵌入主程序，不再需要独立打包 `trulymem-web`。
> 
> 💡 修改 `ui/static/` 或 `core/` 等源码后必须重新编译才能生效（静态文件在构建时打入二进制）。

---

## 架构说明

### 通信协议

UI 与后端通过 **Packet 协议** 通信：

```
TUI (Textual)  ←→  BackendClient  ←→  queue.Queue  ←→  BackendServer (独立线程)
```

### 配置管理

- **用户级存储**: `~/.trulymem/{username}/config.json`
- **Web 配置**: `~/.trulymem/trulymem.db`（web_users 表）
- **自动加载**: 启动时根据登录用户加载对应配置文件
- **动态更新**: 运行时修改配置立即生效，自动持久化

### Web 服务架构

```
┌──────────────────────┐
│    TrulyMEM 主进程    │
│  ┌──────┐ ┌────────┐ │
│  │ TUI  │ │ Flask  │ │  ← 同一进程，不同线程
│  │      │ │ Thread │ │
│  └──────┘ └────────┘ │
└──────────────────────┘
```

---

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

检查 API Key 格式，确保无多余空格。可在 TUI 右侧面板重新配置。

### 管理员账号丢失

数据库中第一个注册账号总是 admin。如果所有用户都丢失了 admin 权限，删除用户目录下的 `trulymem.db` 后重新注册即可。

### 旧版数据迁移

检测到旧版 `~/.trulymem/config.json` 和 `graph_memory.db` 时，TUI 启动时自动进入迁移引导。迁移后旧文件保留，不会删除。

---

## 开发命令

```bash
pip install -r requirements.txt
pytest tests/
bash build/build_linux.sh
```
