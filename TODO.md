# TrulyMEM OpenClaw分支 TODO

## 设计决策：作为增强工具而非主记忆核心

### 背景分析

TrulyMEM main分支的设计理念：
- **图数据库作为唯一持久化记忆载体**
- **摒弃传统messages数组上下文**
- **工作记忆链(TaskNode链)代替对话历史**
- **每轮强制执行流程**：查询人设图 → 查询工作记忆链 → 处理对话 → 更新工作记忆链

### 与OpenClaw memory-core对比

| 方面 | TrulyMEM (main分支) | OpenClaw memory-core |
|------|---------------------|---------------------|
| 核心理念 | 图数据库作为唯一持久化记忆载体 | session transcripts + memory search |
| 对话历史 | 工作记忆链(TaskNode链)代替传统messages | messages数组持久化存储 |
| 上下文管理 | 每轮从图数据库重建 + context_rewrite压缩 | compaction机制压缩历史 |
| 记忆写入 | 通过memory_commit工具写入三元组 | 自动记录对话历史 |
| 记忆检索 | memory_recall工具主动查询 | memory search索引检索 |
| 人设管理 | PersonaNode + 强制查询机制 | 无内置人设系统 |

### 作为主记忆核心的挑战

1. **架构差异**：
   - OpenClaw memory-core是完整基础设施，管理session transcripts、health monitor等
   - TrulyMEM是独立应用设计，需要重新适配OpenClaw架构

2. **强制执行流程**：
   - TrulyMEM要求每轮必须：查询人设图 → 查询工作记忆链 → 处理对话 → 更新工作记忆链
   - OpenClaw没有这种强制流程，需要修改核心逻辑

3. **依赖问题**：
   - main分支是Python实现（TUI应用）
   - openclaw分支是TypeScript插件（不完整移植）
   - 需要完整移植Python版本的核心逻辑

4. **功能缺失**：
   - openclaw分支缺少：context_rewrite压缩工具、强制执行流程、人设强制查询
   - 当前只是普通tool，不是完整记忆系统

### 设计决策

**短期目标**：作为增强工具
- 提供图记忆能力作为额外工具
- 不替换memory-core
- LLM可选调用
- 移除 `"kind": "memory"` 配置，避免独占memory插槽

**长期目标**：如果要替代memory-core
- 需要深度架构重构
- 需要完整移植main分支的核心逻辑（Python → TypeScript）
- 需要实现强制执行流程（修改OpenClaw核心）
- 需要实现context_rewrite工具
- 需要实现工作记忆链机制
- 需要先在独立项目中验证可行性

---

## 当前状态

### 已完成
- [x] plugin-entry.ts 改为OpenClaw SDK规范格式
- [x] 移除 `"kind": "memory"` 配置
- [x] README.md 更新安装文档
- [x] 插件成功加载到OpenClaw
- [x] 基本recall/commit功能测试通过

### 待完成（增强工具设计）

#### 优先级 P0 - 核心功能修复
- [ ] 确认移除memory插槽后的插件加载状态
- [ ] 测试与memory-core并存运行
- [ ] 验证工具schema正确传递给Kimi

#### 优先级 P1 - 功能完善
- [ ] 实现完整的工具参数验证
- [ ] 添加错误处理和日志
- [ ] 完善skill文档（说明增强而非替换）

#### 优先级 P2 - 可选高级功能
- [ ] 实现context_rewrite工具（压缩上下文）
- [ ] 实现工作记忆链机制
- [ ] 实现人设强制查询（作为skill而非核心）
- [ ] 添加时间过滤和多跳遍历优化

---

## 技术细节

### 当前实现状态

**工具列表**：
- `graph_memory` - 综合工具，支持多种action
  - recall: 检索记忆
  - commit: 写入记忆
  - purge: 删除记忆
  - introspect: 查看状态
  - archive: 归档记忆
  - cleanup: 清理数据
  - persona_update/clear: 人设管理
  - task_create/set_state/delete/link_info: 任务管理

**数据存储**：
- SQLite数据库：`~/.trulymem/graph_memory.db`
- 表结构：entities, relations

**与main分支差异**：
- 无context_rewrite工具
- 无强制执行流程
- 无Python TUI界面
- 纯TypeScript插件实现

---

## 参考

- main分支文档：`docs/zh/memory.md`, `docs/zh/working_memory.md`
- OpenClaw文档：https://docs.openclaw.ai/zh-CN/tools/plugin
- kimi-proxy：`/home/program/kimi-proxy/server.js`