/**
 * OpenClaw Plugin Entry Point
 *
 * Registers the GraphMemory tool with OpenClaw's plugin system.
 * Uses @sinclair/typebox for parameter schema definition.
 */
import { Type } from '@sinclair/typebox';
import { GraphMemoryTool } from './runtime/core/tools/builtin/graph_memory_tool.js';

// OpenClaw Tool Schema using TypeBox
const GraphMemoryToolSchema = Type.Object({
  action: Type.String({
    description: '记忆操作类型',
    enum: [
      'recall', 'commit', 'purge', 'introspect',
      'persona_update', 'persona_clear',
      'task_create', 'task_set_state', 'task_delete', 'task_link_info'
    ]
  }),
  params: Type.Object({
    queryIntent: Type.Optional(Type.String({ description: '搜索意图' })),
    seedEntities: Type.Optional(Type.Array(Type.String({ description: '实体' }), { description: '种子实体' })),
    depth: Type.Optional(Type.Number({ description: '检索深度' })),
    sessionFilter: Type.Optional(Type.String({ description: '会话ID过滤' })),
    triplets: Type.Optional(Type.Array(
      Type.Object({
        subject: Type.String({ description: '主体' }),
        relation: Type.String({ description: '关系' }),
        object: Type.String({ description: '客体' }),
        confidence: Type.Optional(Type.Number({ description: '置信度' }))
      }, { description: '三元组' }),
      { description: '三元组数组' }
    )),
    sessionId: Type.Optional(Type.String({ description: '会话ID' })),
    turnId: Type.Optional(Type.Number({ description: '轮次ID' })),
    criteria: Type.Optional(Type.Object({
      subject: Type.Optional(Type.String({ description: '主体' })),
      target: Type.Optional(Type.String({ description: '客体' })),
      relation: Type.Optional(Type.String({ description: '关系' })),
      sessionId: Type.Optional(Type.String({ description: '会话ID' }))
    }, { description: '删除条件' })),
    mode: Type.Optional(Type.String({
      enum: ['soft', 'hard', 'supersede'],
      description: '删除模式'
    })),
    newRelation: Type.Optional(Type.Object({
      relation: Type.String({ description: '关系' }),
      target: Type.String({ description: '客体' })
    }, { description: '新关系（supersede模式）' })),
    attributes: Type.Optional(Type.Array(
      Type.Object({
        attribute: Type.String({ description: '属性名' }),
        value: Type.String({ description: '属性值' })
      }, { description: '属性' }),
      { description: '属性数组' }
    )),
    confirm: Type.Optional(Type.Boolean({ description: '确认清除' })),
    task_id: Type.Optional(Type.String({ description: '任务ID' })),
    description: Type.Optional(Type.String({ description: '任务描述' })),
    state: Type.Optional(Type.String({ description: '任务状态' })),
    info_nodes: Type.Optional(Type.Array(Type.String({ description: '节点' }), { description: '信息节点' })),
    info_node: Type.Optional(Type.String({ description: '信息节点' })),
    days: Type.Optional(Type.Number({ description: '归档天数' })),
    dry_run: Type.Optional(Type.Boolean({ description: '仅预览不删除' }))
  }, { description: '操作参数' })
});

/**
 * Plugin entry point for OpenClaw.
 *
 * When loaded as an OpenClaw plugin, this function registers the GraphMemory tool.
 * For standalone usage, import GraphMemoryTool directly.
 */
export default function registerGraphMemoryPlugin(api: {
  registerTool: (tool: {
    name: string;
    description: string;
    parameters: typeof GraphMemoryToolSchema;
    execute: (id: string, params: Record<string, unknown>) => Promise<{
      content: Array<{ type: 'text'; text: string }>;
    }>;
  }) => void;
}): void {
  const tool = new GraphMemoryTool();

  api.registerTool({
    name: 'graph_memory',
    description: '图记忆工具 - 让 AI 拥有真正的长期记忆能力。支持 recall(检索)、commit(写入)、purge(删除)、introspect(状态)、人设管理、任务管理',
    parameters: GraphMemoryToolSchema,
    async execute(_id: string, params: Record<string, unknown>): Promise<{
      content: Array<{ type: 'text'; text: string }>;
    }> {
      const result = await tool.handler(params, {
        toolCallId: _id,
        workingDirectory: process.cwd(),
        abortController: { signal: new AbortController().signal },
        config: {},
        logger: {
          info: () => {},
          warn: () => {},
          error: () => {},
          debug: () => {}
        }
      });

      return {
        content: [{
          type: 'text',
          text: typeof result === 'string' ? result : JSON.stringify(result)
        }]
      };
    }
  });
}
