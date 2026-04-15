# TrulyMEM → WaterFlow 迁移计划

> ⚠️ **修改只在 TrulyMEM 的 waterflow 分支执行** ⚠️
> 
> 所有代码修改仅应用于 TrulyMEM 仓库的 `waterflow` 分支，作为 WaterFlow 框架的适配版本。

---

## 迁移目标

将 TrulyMEM 的图记忆能力从 Python 迁移到 TypeScript，适配 WaterFlow 框架。

**代码位置**: `/home/program/TrulyMEM-TrueHumanMEM/` (waterflow 分支)

---

## 迁移策略

将图记忆能力作为 TypeScript 模块添加到 waterflow 分支：

| TrulyMEM (Python) | WaterFlow (TypeScript) |
|-------------------|------------------------|
| `EmbeddedGraphDB` | `GraphDatabase` |
| `GraphMemoryClient` | `MemoryService` |
| 12 个记忆工具 | `GraphMemoryTool` + Skills |

---

## 实施步骤

### Phase 1: 项目结构

- [x] 1.1 创建 `ts/` 目录 - TypeScript 项目
- [x] 1.2 创建 `package.json` - 项目配置
- [x] 1.3 创建 `tsconfig.json` - TypeScript 配置

### Phase 2: 核心库

- [x] 2.1 创建 `ts/src/runtime/core/graph_memory/types.ts` - 类型定义
- [x] 2.2 创建 `ts/src/runtime/core/graph_memory/graph_database.ts` - 图数据库
- [x] 2.3 创建 `ts/src/runtime/core/graph_memory/memory_service.ts` - 记忆服务
- [x] 2.4 创建 `ts/src/runtime/core/graph_memory/index.ts` - 模块导出

### Phase 3: Tool 接口

- [x] 3.1 创建 `ts/src/runtime/core/tools/builtin/graph_memory_tool.ts` - Tool 实现
- [x] 3.2 注册 Tool (作为独立模块导出)

### Phase 4: Skill 定义

- [x] 4.1 创建 `ts/bundled-skills/graph_memory/SKILL.md` - 主 Skill
- [x] 4.2 创建 `ts/bundled-skills/graph_memory/persona/SKILL.md` - Persona
- [x] 4.3 创建 `ts/bundled-skills/graph_memory/task/SKILL.md` - 任务管理

### Phase 5: 验证

- [x] 5.1 编译 TypeScript - 无错误
- [ ] 5.2 运行测试

---

## 目录结构 (在 TrulyMEM waterflow 分支)

```
TrulyMEM-TrueHumanMEM/
├── ts/                                    # TypeScript 项目 (保留)
│   ├── src/
│   │   └── runtime/core/
│   │       ├── graph_memory/              # 图记忆模块
│   │       │   ├── index.ts
│   │       │   ├── types.ts
│   │       │   ├── graph_database.ts
│   │       │   └── memory_service.ts
│   │       └── tools/
│   │           └── builtin/
│   │               └── graph_memory_tool.ts
│   ├── bundled-skills/
│   │   └── graph_memory/
│   │       ├── SKILL.md
│   │       ├── persona/SKILL.md
│   │       └── task/SKILL.md
│   ├── package.json
│   └── tsconfig.json
│
├── docs/integration/waterflow-design.md   # 迁移设计文档 (保留)
│
└── (其他文件迁移后删除)
```

---

## 迁移后清理

迁移完成后，waterflow 分支将删除以下文件：

- `core/` - Python 核心代码
- `ui/` - Python UI 代码
- `tests/` - Python 测试
- `tools/` - Python 工具
- `trulymem_entry.py` - Python 入口
- `build/` - 构建脚本
- `pic/` - 图片资源 (除图标外)
- `requirements.txt` - Python 依赖
- `TrulyMEM.spec` - Python 打包配置

只保留：
- `ts/` - TypeScript 源码
- `docs/integration/waterflow-design.md` - 迁移文档
- `.gitignore`, `LICENSE`

---

## 工作追踪

工作进度记录在: `todo_progress.md`

每次修改文件前后请查看此文件并更新进度。
