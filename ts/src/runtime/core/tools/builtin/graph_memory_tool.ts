import type { Tool, ToolCategory, PermissionLevel, ToolInputSchema, ToolExecutionContext, ToolOutput } from '../tool_interface';
import { GraphDatabase } from '../../graph_memory/graph_database';
import { MemoryService } from '../../graph_memory/memory_service';

const GRAPH_MEMORY_TOOL_ID = 'builtin:graph_memory';

const GRAPH_MEMORY_TOOL_DESCRIPTION = `图记忆工具 - 让 AI 拥有真正的长期记忆能力

操作:
- recall: 检索记忆
- commit: 写入记忆  
- purge: 删除记忆
- introspect: 查看状态
- persona_update/clear: 人设管理
- task_create/set_state/delete: 任务管理`;

export class GraphMemoryTool implements Tool {
  readonly id = GRAPH_MEMORY_TOOL_ID;
  readonly name = 'GraphMemory';
  readonly description = GRAPH_MEMORY_TOOL_DESCRIPTION;
  readonly category: ToolCategory = 'analysis';
  readonly permissionLevel: PermissionLevel = 'safe';

  readonly inputSchema: ToolInputSchema = {
    type: 'object',
    properties: {
      action: {
        type: 'string',
        enum: [
          'recall', 'commit', 'purge', 'introspect',
          'persona_update', 'persona_clear',
          'task_create', 'task_set_state', 'task_delete', 'task_link_info'
        ],
        description: '记忆操作类型'
      },
      params: {
        type: 'object',
        description: '操作参数',
        properties: {
          queryIntent: { type: 'string', description: '搜索意图' },
          seedEntities: { type: 'array', items: { type: 'string', description: '实体' }, description: '种子实体' },
          depth: { type: 'number', description: '检索深度' },
          sessionFilter: { type: 'string', description: '会话ID过滤' },
          triplets: {
            type: 'array',
            items: {
              type: 'object',
              description: '三元组',
              properties: {
                subject: { type: 'string', description: '主体' },
                relation: { type: 'string', description: '关系' },
                object: { type: 'string', description: '客体' },
                confidence: { type: 'number', description: '置信度' }
              }
            },
            description: '三元组数组'
          },
          sessionId: { type: 'string', description: '会话ID' },
          turnId: { type: 'number', description: '轮次ID' },
          criteria: {
            type: 'object',
            properties: {
              subject: { type: 'string', description: '主体' },
              target: { type: 'string', description: '客体' },
              relation: { type: 'string', description: '关系' },
              sessionId: { type: 'string', description: '会话ID' }
            },
            description: '删除条件'
          },
          mode: { type: 'string', enum: ['soft', 'hard', 'supersede'], description: '删除模式' },
          attributes: {
            type: 'array',
            items: {
              type: 'object',
              description: '属性',
              properties: {
                attribute: { type: 'string', description: '属性名' },
                value: { type: 'string', description: '属性值' }
              }
            },
            description: '属性数组'
          },
          confirm: { type: 'boolean', description: '确认清除' },
          task_id: { type: 'string', description: '任务ID' },
          description: { type: 'string', description: '任务描述' },
          state: { type: 'string', description: '任务状态' },
          info_nodes: { type: 'array', items: { type: 'string', description: '节点' }, description: '信息节点' },
          info_node: { type: 'string', description: '信息节点' }
        }
      }
    },
    required: ['action', 'params']
  };

  private db: GraphDatabase;
  private service: MemoryService;

  constructor(sessionId?: string) {
    this.db = new GraphDatabase(sessionId);
    this.service = new MemoryService(this.db);
  }

  async handler(params: Record<string, unknown>, _context: ToolExecutionContext): Promise<ToolOutput> {
    const action = params.action as string;
    const actionParams = params.params as Record<string, unknown>;

    try {
      const result = await this.executeAction(action, actionParams);
      return JSON.stringify({ success: true, data: result }, null, 2);
    } catch (error) {
      return JSON.stringify({
        success: false,
        error: {
          type: 'execution_error',
          message: error instanceof Error ? error.message : String(error)
        }
      }, null, 2);
    }
  }

  private async executeAction(action: string, params: Record<string, unknown>): Promise<unknown> {
    switch (action) {
      case 'recall':
        return this.service.recall({
          queryIntent: params.queryIntent as string || '',
          seedEntities: params.seedEntities as string[] | undefined,
          depth: params.depth as number | undefined,
          sessionFilter: params.sessionFilter as string | undefined
        });

      case 'commit':
        return this.service.commit({
          triplets: params.triplets as Array<{ subject: string; relation: string; object: string; confidence?: number }>,
          sessionId: params.sessionId as string | undefined,
          turnId: params.turnId as number | undefined
        });

      case 'purge':
        return this.service.purge({
          criteria: params.criteria as { subject?: string | undefined; target?: string | undefined; relation?: string | undefined; sessionId?: string | undefined } | undefined,
          mode: params.mode as 'soft' | 'hard' | 'supersede' | undefined
        });

      case 'introspect':
        return this.service.introspect();

      case 'persona_update':
        return this.service.updatePersona({
          attributes: params.attributes as Array<{ attribute: string; value: string }>,
          mode: params.mode as 'merge' | 'replace'
        });

      case 'persona_clear':
        return this.service.clearPersona({
          confirm: params.confirm as boolean
        });

      case 'task_create':
        return this.service.createTask({
          task_id: params.task_id as string,
          description: params.description as string,
          info_nodes: params.info_nodes as string[] | undefined
        });

      case 'task_set_state':
        return this.service.setTaskState({
          task_id: params.task_id as string,
          state: params.state as string
        });

      case 'task_delete':
        return this.service.deleteTask({
          task_id: params.task_id as string
        });

      case 'task_link_info':
        return this.service.linkInfoToTask({
          task_id: params.task_id as string,
          info_node: params.info_node as string
        });

      default:
        throw new Error(`Unknown action: ${action}`);
    }
  }
}

export function createGraphMemoryTool(sessionId?: string): GraphMemoryTool {
  return new GraphMemoryTool(sessionId);
}
