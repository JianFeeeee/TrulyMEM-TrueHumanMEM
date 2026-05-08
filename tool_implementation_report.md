# AIAgentService.ets 工具实现完整性审查报告

**审查文件**: `/home/program/TrulyMEM-TrueHumanMEM/common/src/main/ets/service/AIAgentService.ets`
**审查日期**: 2026-05-02

---

## 一、工具实现状态总览

| # | 工具名 | Handler 名 | executeTool case | GraphMemoryService 方法 | 状态 |
|---|--------|------------|------------------|------------------------|------|
| 1 | `memory_recall` | `memoryRecal` | ✅ (L794-808) | `memoryRecall()` L316 | ✅ 完整 |
| 2 | `memory_commit` | `memoryCommit` | ✅ (L811-825) | `memoryCommit()` L353 | ✅ 完整 |
| 3 | `memory_purge` | `memoryPurge` | ✅ (L827-840) | `memoryPurge()` L382 | ✅ 完整 |
| 4 | `memory_introspect` | `memoryIntrospect` | ✅ (L842-850) | `memoryIntrospect()` L436 | ✅ 完整 |
| 5 | `memory_archive` | `memoryArchive` | ✅ (L852-860) | `archive()` L469 | ✅ 完整 |
| 6 | `memory_cleanup` | `memoryCleanup` | ✅ (L862-870) | `cleanup()` L604 | ✅ 完整 |
| 7 | `memory_query_archived` | `memoryQueryArchived` | ✅ (L872-880) | `queryArchived()` L626 | ✅ 完整 |
| 8 | `context_rewrite` | `contextRewrite` | ✅ (L882-890) | 无（本地验证） | ⚠️ 可疑 |
| 9 | `persona_update` | `personaUpdate` | ✅ (L892-907) | `personaUpdate()` L643 | ✅ 完整 |
| 10 | `persona_remove` | `personaRemove` | ✅ (L909-917) | `personaRemove()` L732 | ✅ 完整 |
| 11 | `persona_clear` | `personaClear` | ✅ (L919-927) | `personaClear()` L714 | ✅ 完整 |
| 12 | `task_create` | `taskCreate` | ✅ (L929-942) | `taskCreate()` L774 | ✅ 完整 |
| 13 | `task_set_state` | `taskSetState` | ✅ (L944-956) | `taskSetState()` L812 | ⚠️ 可疑 |
| 14 | `task_delete` | `taskDelete` | ✅ (L958-970) | `taskDelete()` L835 | ✅ 完整 |
| 15 | `task_link_info` | `taskLinkInfo` | ✅ (L972-984) | `taskLinkInfo()` L857 | ✅ 完整 |
| 16 | `task_archive` | `taskArchive` | ✅ (L986-998) | `taskArchive()` L881 | ⚠️ 可疑 |
| 17 | `task_query` | `taskQuery` | ✅ (L1000-1011) | `taskQuery()` L904 | ✅ 完整 |

---

## 二、详细分析

### ✅ 完整实现的工具（14/17）

以下工具均有完整的 case 分支、参数映射、GraphMemoryService 方法调用和结果返回：

- **memory_recall** - 完整，参数映射正确，调用 `memoryRecall()`
- **memory_commit** - 完整，参数映射正确，调用 `memoryCommit()`
- **memory_purge** - 完整，参数映射正确，调用 `memoryPurge()`
- **memory_introspect** - 完整，参数映射正确，调用 `memoryIntrospect()`
- **memory_archive** - 完整，参数映射正确，调用 `archive()`
- **memory_cleanup** - 完整，参数映射正确，调用 `cleanup()`
- **memory_query_archived** - 完整，参数映射正确，调用 `queryArchived()`
- **persona_update** - 完整，参数映射正确，调用 `personaUpdate()`
- **persona_remove** - 完整，参数映射正确，调用 `personaRemove()`
- **persona_clear** - 完整，无参数，调用 `personaClear()`
- **task_create** - 完整，参数映射正确，调用 `taskCreate()`
- **task_delete** - 完整，参数映射正确，调用 `taskDelete()`
- **task_link_info** - 完整，参数映射正确，调用 `taskLinkInfo()`
- **task_query** - 完整，参数映射正确，调用 `taskQuery()`

### ⚠️ 可疑的工具（3/17）

#### 1. `context_rewrite` (L882-890) — ⚠️ 非真实实现

```typescript
case 'contextRewrite': {
    const summary = args.summary as string;
    const result: ToolCallResult = {
        name: 'context_rewrite',
        success: summary.includes('[工具调用总结'),
        message: summary.includes('[工具调用总结') ? '上下文已压缩' : '格式错误：必须包含[工具调用总结]标记'
    };
    return result;
}
```

**问题**:
- 没有调用任何 GraphMemoryService 方法，仅做本地字符串验证
- 只是检查 `summary` 参数是否包含 `[工具调用总结` 标记
- 实际上下文压缩完全依赖 AI 端的 LLM 处理，服务端不做任何存储或处理
- 这是一个**设计选择**而非 bug——上下文重写确实是 LLM 侧操作
- **风险**: 如果未来需要保存压缩结果或审计，这里需要补充实现

#### 2. `task_archive` (L986-998) — ⚠️ 语义 bug

Handler 调用 `this.memoryService.taskArchive()` 在 GraphMemoryService:881:

```typescript
async taskArchive(params: TaskArchiveParams): Promise<TaskActionResult> {
    await this.taskSetState({ taskId: params.taskId, state: '已暂停' });
    // ...
}
```

**问题**:
- `task_archive` 的内部实现将任务状态设为 `'已暂停'` 而非 `'archived'`
- 工具描述明确说"将任务状态设为 archived"，但实际设为 `已暂停`
- 与系统提示词中"步骤6归档规则"的语义不一致
- **建议**: 改为 `state: '已暂停'` 应改为 `state: '已完成'` 或直接支持 `'archived'` 状态

#### 3. `task_set_state` (L944-956) — ⚠️ 类型定义不一致

```typescript
// ToolStateArg 类型定义
type ToolStateArg = '进行中' | '已完成' | '已暂停' | '已取消';

// 工具描述中 stateFilter 允许的值
stateFilter: '进行中/已完成/已暂停/已取消/archived'
```

**问题**:
- `ToolStateArg` 类型不包含 `'archived'` 值
- 但工具描述和 query 的 stateFilter 都提到了 `archived` 状态
- `task_archive` 内部使用 `'已暂停'` 来模拟归档，而非真正的 `'archived'` 状态
- 这意味着 AI 无法通过 `task_set_state` 直接设置 `archived` 状态
- 虽然底层只是写入 `has_state` 关系字符串，类型限制不会阻断运行时，但**语义不一致**

---

## 三、TODO/FIXME/占位符检查

| 检查项 | 结果 |
|--------|------|
| `TODO` 注释 | ❌ 无 |
| `FIXME` 注释 | ❌ 无 |
| `placeholder` | ❌ 无 |
| `return { success: false }` 占位 | ❌ 无 |
| `not implemented` | ❌ 无 |
| `未实现的工具` | ✅ 仅在 default case 中（预期行为） |

**结论**: 文件中没有未完成的占位符代码。所有 case 分支都有实际实现。

---

## 四、TOOL_HANDLER_MAP 映射完整性

| TOOLS_DEFINITION (17个) | TOOL_HANDLER_MAP (17个) | executeTool case (17个) | 匹配状态 |
|-------------------------|-------------------------|-------------------------|----------|
| 17 个工具定义 | 17 个映射条目 | 17 个 case 分支 | ✅ 完全匹配 |

- `TOOLS_DEFINITION` 定义了 17 个工具
- `TOOL_HANDLER_MAP` 包含 17 个 snake_case → camelCase 映射
- `executeTool` switch 包含 17 个 case + 1 个 default
- 每个工具都有对应的 handler 映射和 case 实现

---

## 五、工具描述完整性

| 工具 | 描述完整性 | 备注 |
|------|-----------|------|
| `memory_recall` | ✅ | 包含强制执行顺序说明 |
| `memory_commit` | ✅ | 包含写入原则说明 |
| `memory_purge` | ✅ | 包含使用场景和模式说明 |
| `memory_introspect` | ⚠️ | 描述较短，缺少参数说明 |
| `memory_archive` | ⚠️ | 描述较短，缺少天数说明 |
| `memory_cleanup` | ⚠️ | 描述较短，缺少 dryRun 说明 |
| `memory_query_archived` | ✅ | 包含使用场景和注意事项 |
| `context_rewrite` | ✅ | 包含强制要求说明 |
| `persona_update` | ⚠️ | 描述非常简短 |
| `persona_remove` | ⚠️ | 描述非常简短 |
| `persona_clear` | ⚠️ | 描述非常简短 |
| `task_create` | ✅ | 包含 info_nodes 限制说明 |
| `task_set_state` | ⚠️ | 描述非常简短 |
| `task_delete` | ⚠️ | 描述非常简短 |
| `task_link_info` | ✅ | 包含全局实体限制说明 |
| `task_archive` | ✅ | 包含使用场景和注意事项 |
| `task_query` | ✅ | 包含使用说明 |

---

## 六、发现的其他问题

### 1. `memoryArchive` 工具属性定义混淆

存在两个 `archiveProps` 变量：
- `archiveProps` (L480): `{ taskId, summary }` — 用于 `task_archive`
- `archiveProps2` (L491): `{ days }` — 用于 `memory_archive`

命名容易混淆，建议重命名为 `taskArchiveProps` 和 `memoryArchiveProps`。

### 2. `taskSetState` 的 state 参数描述过于简短

L521: `makeToolDef('task_set_state', '设置任务状态。', ...)`

建议补充状态枚举值说明，帮助 AI 理解可用的状态选项。

### 3. `persona_update` 缺少 mode 参数

工具描述提到 `mode="replace"` 和 `mode="merge"`，但 `personaProps` 和 `PersonaUpdateParams` 中都没有 `mode` 字段。

---

## 七、总结

```
✅ 完整实现: 14/17 (82%)
⚠️ 有缺陷:  3/17 (18%)
❌ 占位符:   0/17 (0%)
```

**关键发现**:
1. **无占位符代码** — 所有工具都有实际实现，没有 TODO/FIXME/placeholder
2. **映射完全覆盖** — TOOLS_DEFINITION ↔ TOOL_HANDLER_MAP ↔ executeTool case 100% 匹配
3. **3个可疑项**:
   - `context_rewrite` 是纯本地验证，非真实服务实现（设计选择）
   - `task_archive` 内部使用 `'已暂停'` 替代 `'archived'` 状态（语义 bug）
   - `task_set_state` 类型定义不包含 `'archived'`（与文档不一致）

**建议优先级**:
- 🔴 高: 修复 `task_archive` 的语义不一致问题
- 🟡 中: 补充 `persona_update` 的 `mode` 参数支持
- 🟢 低: 重命名 `archiveProps`/`archiveProps2` 以提高可读性
