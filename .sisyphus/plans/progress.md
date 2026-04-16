# 重构执行进度追踪

> 最后更新: 2026-04-16 15:00
> 当前分支: openclaw

## Phase 1: 项目结构改造为 OpenClaw Plugin（🔴 P0）

### 1.1 添加 OpenClaw Plugin SDK 依赖
- [x] 1.1.1 `npm install @sinclair/typebox better-sqlite3`
- [x] 1.1.2 更新 `ts/package.json` 添加 `openclaw` 字段
- [x] 1.1.3 创建 `ts/openclaw.plugin.json` manifest 文件

### 1.2 创建 Plugin Entry Point
- [x] 1.2.1 创建 `ts/src/plugin-entry.ts`
- [x] 1.2.2 确保 entry point 导出为 ESM 格式
- [x] 1.2.3 更新 `ts/tsconfig.json` 确保编译输出路径正确

### 1.3 迁移 Tool Schema 到 TypeBox
- [x] 1.3.1 添加 TypeBox schema 到 plugin-entry.ts
- [x] 1.3.2 更新 `graph_memory_tool.ts` 的 `inputSchema` 字段（添加 newRelation, days, dry_run）
- [x] 1.3.3 添加 `execute(_id, params)` 方法匹配 OpenClaw 签名
- [x] 1.3.4 返回值格式为 `{ content: [{ type: "text", text }] }`

### 1.4 更新 Tool Interface
- [x] 1.4.1 添加 `OpenClawToolResult` 类型到 graph_memory_tool.ts

## Phase 2: SKILL.md 格式修复（🔴 P0）

### 2.1 修复 skills/graph-memory/SKILL.md
- [x] 2.1.1 移除多行嵌套结构
- [x] 2.1.2 name 改为 kebab-case
- [x] 2.1.3 description 改为单行
- [x] 2.1.4 添加 metadata 单行 JSON

### 2.2 修复 skills/graph-memory/persona/SKILL.md
- [x] 2.2.1 同上

### 2.3 修复 skills/graph-memory/task/SKILL.md
- [x] 2.3.1 同上

### 2.4 同步修复 bundled-skills
- [x] 2.4.1 ts/bundled-skills/graph-memory/SKILL.md
- [x] 2.4.2 ts/bundled-skills/graph-memory/persona/SKILL.md
- [x] 2.4.3 ts/bundled-skills/graph-memory/task/SKILL.md

### 2.5 重命名目录
- [x] 2.5.1 skills/graph_memory/ → skills/graph-memory/
- [x] 2.5.2 ts/bundled-skills/graph_memory/ → ts/bundled-skills/graph-memory/

## Phase 3: GraphDatabase 持久化（🔴 P0）

### 3.1 添加 SQLite 依赖
- [ ] 3.1.1 npm install better-sqlite3
- [ ] 3.1.2 npm install @types/better-sqlite3

### 3.2 重写 GraphDatabase
- [x] 3.2.1 修改构造函数接受 dbPath
- [x] 3.2.2 使用 better-sqlite3 创建/连接数据库
- [x] 3.2.3 创建实体表
- [x] 3.2.4 创建关系表
- [x] 3.2.5 创建索引

### 3.3-3.7 功能补全
- [x] 3.3 depth 多跳遍历 (BFS)
- [x] 3.4 timeRange 过滤
- [x] 3.5 supersede 模式
- [x] 3.6 archive 归档
- [x] 3.7 cleanup 清理

### 3.8 修复逻辑
- [x] 3.8.1 修复 isEntityDeleted 逻辑 (已移除，用 SQL 替代)

## Phase 4: ToolLimiter（🟡 P2）

- [ ] 4.1 创建 ToolLimiter
- [ ] 4.2 集成到 GraphMemoryTool

## Phase 5: 测试重建（🔴 P1）

- [ ] 5.1 GraphDatabase 测试 (15+)
- [ ] 5.2 MemoryService 测试 (12+)
- [ ] 5.3 GraphMemoryTool 测试 (15+)
- [ ] 5.4 Plugin Entry 集成测试

## Phase 6: 文档更新（🟢 P3）

- [ ] 6.1 更新 README.md
- [ ] 6.2 更新 README_EN.md
- [ ] 6.3 更新迁移设计文档

## 最终验收

- [ ] npm run build 编译通过
- [ ] npm test 全部通过
- [ ] 推送到远程 openclaw 分支
