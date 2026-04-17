import type { Tool, ToolCategory, PermissionLevel, ToolInputSchema, ToolOutput, ToolInput, ToolExecutionContext } from 'waterflow-ts/dist/runtime/core/tools/tool_interface.js';
import { GraphDatabase } from '../../graph_memory/graph_database';
import { MemoryService } from '../../graph_memory/memory_service';

const GRAPH_MEMORY_TOOL_ID = 'builtin:graph_memory';
const GRAPH_MEMORY_TOOL_API_NAME = 'graph_memory'; // API 兼容名称（不含冒号，符合 ^[a-zA-Z0-9_-]+$ 要求）

/**
 * 工具名称映射工具 - 用于处理 API 对工具名称格式的限制
 * OpenAI/DeepSeek API 要求工具名称符合 ^[a-zA-Z0-9_-]+$ 正则表达式
 * 而 TrulyMEM 的内部 ID 使用 "builtin:xxx" 格式（含冒号）
 */

/**
 * 将内部工具 ID 映射为 API 兼容名称
 * @param toolId 内部工具 ID，如 "builtin:graph_memory"
 * @returns API 兼容名称，如 "graph_memory"
 */
export function mapToolIdToApiName(toolId: string): string {
  // 移除 "builtin:" 前缀
  if (toolId.startsWith('builtin:')) {
    return toolId.slice(8);
  }
  // 其他前缀也移除（如 "mcp:", "plugin:"）
  const colonIndex = toolId.indexOf(':');
  if (colonIndex > 0) {
    return toolId.slice(colonIndex + 1);
  }
  return toolId;
}

/**
 * 将 API 返回的工具名称映射回内部 ID
 * @param apiName API 返回的工具名称，如 "graph_memory"
 * @param prefix 内部 ID 前缀，默认 "builtin:"
 * @returns 内部工具 ID，如 "builtin:graph_memory"
 */
export function mapApiNameToToolId(apiName: string, prefix = 'builtin:'): string {
  // 如果已经是完整 ID 格式，直接返回
  if (apiName.includes(':')) {
    return apiName;
  }
  return `${prefix}${apiName}`;
}

const GRAPH_MEMORY_TOOL_DESCRIPTION = `图记忆工具 - 让 AI 拥有真正的长期记忆能力

操作:
- recall: 检索记忆 - 提供 queryIntent (搜索意图) 和可选的 seedEntities
- commit: 写入记忆 - 必须使用 triplets 数组格式，每个三元组包含 subject, relation, object
- purge: 删除记忆 - 提供 criteria 指定删除条件
- introspect: 查看状态 - 无参数
- persona_update/clear: 人设管理
- task_create/set_state/delete: 任务管理

【commit 操作的三元组格式】
triplets 必须是数组，每个元素是 {subject, relation, object, confidence} 格式:
示例: {"action":"commit","params":{"triplets":[{"subject":"Alice","relation":"is a","object":"engineer","confidence":0.95}]}}
- subject: 实体名称 (如用户名、技术名称)
- relation: 关系描述 (如 "is a", "likes", "knows")
- object: 目标实体 (如职业、爱好、技术)
- confidence: 置信度 0-1 (可选，默认0.9)

【recall 操作】
示例: {"action":"recall","params":{"queryIntent":"用户的学习偏好","seedEntities":["Alice"]}}`;

export class GraphMemoryTool implements Tool {
  readonly id = GRAPH_MEMORY_TOOL_ID;
  readonly name = 'GraphMemory';
  readonly apiName = GRAPH_MEMORY_TOOL_API_NAME;
  readonly description = GRAPH_MEMORY_TOOL_DESCRIPTION;
  readonly category: ToolCategory = 'analysis';
  readonly permissionLevel: PermissionLevel = 'safe';
  readonly alwaysLoad = true;

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
            description: '知识三元组数组。每个三元组描述 subject-relation-object 关系，用于存储记忆知识。',
            items: {
              type: 'object',
              description: '三元组: {subject, relation, object, confidence} - subject/relation/object 必填',
              properties: {
                subject: { type: 'string', description: '主体实体，如人名、技术名称等' },
                relation: { type: 'string', description: '关系描述，如 "is a", "likes", "knows", "uses" 等' },
                object: { type: 'string', description: '客体实体，如职业、爱好、技术名称等' },
                confidence: { type: 'number', description: '置信度 (0-1)，默认 0.9', default: 0.9 }
              }
            }
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

  async handler(params: ToolInput, context: ToolExecutionContext): Promise<ToolOutput> {
    if (context.abortController?.signal?.aborted) {
      throw new Error('Operation aborted');
    }

    const action = params.action as string;
    const actionParams = params.params as Record<string, unknown>;
    const logger = context?.logger;

    try {
      logger?.info(`[GraphMemoryTool] Executing action: ${action}`);
      const result = await this.executeAction(action, actionParams);
      logger?.info(`[GraphMemoryTool] Action ${action} completed successfully`);
      return JSON.stringify({ success: true, data: result }, null, 2);
    } catch (error) {
      logger?.error(`[GraphMemoryTool] Action ${action} failed:`, error);
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
