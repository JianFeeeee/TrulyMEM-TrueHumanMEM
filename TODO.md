# TrulyMEM 待完成事项

## 项目概述
TrulyMEM - 真正的长期记忆系统 (True Human MEMory)
为 OpenClaw 提供图数据库形式的结构化长期记忆能力。

## 已完成功能

### P0 - 核心功能修复 ✅
- [x] 确认移除 memory 插槽后的插件加载状态
- [x] 测试与 memory-core 并存运行
- [x] 验证工具 schema 正确传递给 Kimi

### P1 - 功能完善 ✅
- [x] 4. 实现完整的工具参数验证
  - 为所有 action（recall/commit/purge/persona_update/persona_clear/task_create/task_set_state/task_delete/task_link_info）实现独立验证函数
  - 验证规则：recall 必需 queryIntent 或 seedEntities；depth 1-5；commit triplets 非空且字段有效；persona_clear 需 confirm；task 需 task_id 和 description 等
- [x] 5. 添加错误处理和日志
  - 新增 GraphMemoryLogger 日志系统（info/warn/error/action 级别）
  - 敏感数据脱敏：attributes 只记录属性名，triplets 只记录数量
  - 参数验证错误返回 validation_error 类型
  - 执行错误返回 execution_error 类型
- [x] 6. 完善 skill 文档（说明增强而非替换）
  - 更新 3 个 skill 文档（graph-memory、graph-memory-persona、graph-memory-task）
  - 明确说明是 OpenClaw memory-core 的增强补充，不替代核心功能
  - 添加与 memory-core 的关系对比表

## 进行中 / 待完成

### P2 - 可选高级功能
- [ ] 7. 实现 context_rewrite 工具（压缩上下文）
- [ ] 8. 实现工作记忆链机制
- [ ] 9. 实现人设强制查询（作为 skill 而非核心）

## 技术规格

### 测试覆盖
- 测试文件：`ts/tests/runtime/core/tools/builtin/graph_memory_tool.test.ts`
- 当前测试数：**118 个全部通过**
- 参数验证测试：11 个（覆盖所有 action 的必填参数、范围校验等）

### 提交记录
- 最新提交：`P1: 完整参数验证 + 错误处理/日志 + 测试覆盖`

## 注意事项
- 所有功能均作为 OpenClaw 插件实现，不修改 OpenClaw 核心代码
- 插件入口：`ts/src/plugin-entry.ts`
- 技能目录：`skills/`（源文件）和 `ts/bundled-skills/`（编译后）
