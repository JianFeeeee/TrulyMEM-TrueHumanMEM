import { Type } from '@sinclair/typebox';
import type { Static } from '@sinclair/typebox';
import { GraphDatabase } from '../../graph_memory/graph_database.js';
import { MemoryService } from '../../graph_memory/memory_service.js';
import { ToolLimiter } from '../tool_limiter.js';

export const GraphMemoryToolSchema = Type.Object({
  action: Type.String({
    description: '记忆操作类型',
    enum: [
      'recall', 'commit', 'purge', 'introspect', 'archive', 'cleanup',
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

export type GraphMemoryToolParams = Static<typeof GraphMemoryToolSchema>;

const GRAPH_MEMORY_TOOL_DESCRIPTION = `图记忆工具 - 让 AI 拥有真正的长期记忆能力

操作:
- recall: 检索记忆
- commit: 写入记忆
- purge: 删除记忆
- introspect: 查看状态
- archive: 归档旧记忆
- cleanup: 清理无效数据
- persona_update/clear: 人设管理
- task_create/set_state/delete/link_info: 任务管理`;

export function createGraphMemoryTool(dbPath?: string, sessionId?: string) {
  const db = new GraphDatabase(dbPath, sessionId);
  const service = new MemoryService(db);
  const limiter = new ToolLimiter();

  async function executeAction(action: string, params: Record<string, unknown>): Promise<unknown> {
    const [allowed, reason] = limiter.canCall(action);
    if (!allowed) {
      throw new Error(reason);
    }
    limiter.recordCall(action);

    switch (action) {
      case 'recall':
        return service.recall({
          queryIntent: params.queryIntent as string || '',
          seedEntities: params.seedEntities as string[] | undefined,
          depth: params.depth as number | undefined,
          sessionFilter: params.sessionFilter as string | undefined
        });

      case 'commit':
        return service.commit({
          triplets: params.triplets as Array<{ subject: string; relation: string; object: string; confidence?: number }>,
          sessionId: params.sessionId as string | undefined,
          turnId: params.turnId as number | undefined
        });

      case 'purge':
        return service.purge({
          criteria: params.criteria as { subject?: string; target?: string; relation?: string; sessionId?: string } | undefined,
          mode: params.mode as 'soft' | 'hard' | 'supersede' | undefined,
          newRelation: params.newRelation as { relation: string; target: string } | undefined
        });

      case 'introspect':
        return service.introspect();

      case 'persona_update':
        return service.updatePersona({
          attributes: params.attributes as Array<{ attribute: string; value: string }>,
          mode: params.mode as 'merge' | 'replace'
        });

      case 'persona_clear':
        return service.clearPersona({
          confirm: params.confirm as boolean
        });

      case 'task_create':
        return service.createTask({
          task_id: params.task_id as string,
          description: params.description as string,
          info_nodes: params.info_nodes as string[] | undefined
        });

      case 'task_set_state':
        return service.setTaskState({
          task_id: params.task_id as string,
          state: params.state as string
        });

      case 'task_delete':
        return service.deleteTask({
          task_id: params.task_id as string
        });

      case 'task_link_info':
        return service.linkInfoToTask({
          task_id: params.task_id as string,
          info_node: params.info_node as string
        });

      case 'archive':
        return service.archive(params.days as number | undefined);

      case 'cleanup':
        return service.cleanup(params.dry_run as boolean | undefined);

      default:
        throw new Error(`Unknown action: ${action}`);
    }
  }

  return {
    name: 'graph_memory',
    description: GRAPH_MEMORY_TOOL_DESCRIPTION,
    parameters: GraphMemoryToolSchema,

    async execute(_toolCallId: string, params: Record<string, unknown>): Promise<{
      content: Array<{ type: 'text'; text: string }>;
    }> {
      const action = params.action as string;
      const actionParams = params.params as Record<string, unknown>;

      try {
        const result = await executeAction(action, actionParams);
        return {
          content: [{ type: 'text', text: JSON.stringify({ success: true, data: result }) }]
        };
      } catch (error) {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: false,
              error: {
                type: 'execution_error',
                message: error instanceof Error ? error.message : String(error)
              }
            })
          }]
        };
      }
    }
  };
}

export { ToolLimiter } from '../tool_limiter.js';