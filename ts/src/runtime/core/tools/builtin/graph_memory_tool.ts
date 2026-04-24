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

const GRAPH_MEMORY_TOOL_DESCRIPTION = `图记忆工具 - 让 AI 拥有真正的长期记忆能力。作为 OpenClaw memory-core 的增强补充，不替代其核心功能。

操作:
- recall: 检索记忆（可选参数: queryIntent, seedEntities, depth, sessionFilter）
- commit: 写入记忆（必需参数: triplets）
- purge: 删除记忆（可选参数: criteria, mode, newRelation）
- introspect: 查看状态（无参数）
- archive: 归档旧记忆（可选参数: days, 默认30天）
- cleanup: 清理无效数据（可选参数: dry_run, 默认true预览模式）
- persona_update: 更新人设（必需参数: attributes; 可选: mode=merge/replace）
- persona_clear: 清除人设（必需参数: confirm=true）
- task_create: 创建任务（必需参数: task_id, description; 可选: info_nodes）
- task_set_state: 设置任务状态（必需参数: task_id, state）
- task_delete: 删除任务（必需参数: task_id）
- task_link_info: 关联信息（必需参数: task_id, info_node）`;

// ==================== 参数验证 ====================

interface ValidationError {
  field: string;
  message: string;
}

function validateRecallParams(params: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];
  const queryIntent = params.queryIntent;
  const seedEntities = params.seedEntities;

  if ((!queryIntent || (typeof queryIntent === 'string' && queryIntent.trim() === '')) &&
      (!seedEntities || !Array.isArray(seedEntities) || seedEntities.length === 0)) {
    errors.push({ field: 'queryIntent/seedEntities', message: 'recall 操作需要提供 queryIntent 或 seedEntities 之一' });
  }

  if (params.depth !== undefined) {
    const depth = Number(params.depth);
    if (isNaN(depth) || depth < 1 || depth > 5) {
      errors.push({ field: 'depth', message: 'depth 必须在 1-5 之间' });
    }
  }

  return errors;
}

function validateCommitParams(params: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];
  const triplets = params.triplets;

  if (!triplets || !Array.isArray(triplets) || triplets.length === 0) {
    errors.push({ field: 'triplets', message: 'commit 操作必需提供 triplets 数组' });
    return errors;
  }

  for (let i = 0; i < triplets.length; i++) {
    const t = triplets[i] as Record<string, unknown>;
    if (!t.subject || typeof t.subject !== 'string' || t.subject.trim() === '') {
      errors.push({ field: `triplets[${i}].subject`, message: '三元组主体不能为空字符串' });
    }
    if (!t.relation || typeof t.relation !== 'string' || t.relation.trim() === '') {
      errors.push({ field: `triplets[${i}].relation`, message: '三元组关系不能为空字符串' });
    }
    if (!t.object || typeof t.object !== 'string' || t.object.trim() === '') {
      errors.push({ field: `triplets[${i}].object`, message: '三元组客体不能为空字符串' });
    }
    if (t.confidence !== undefined) {
      const c = Number(t.confidence);
      if (isNaN(c) || c < 0 || c > 1) {
        errors.push({ field: `triplets[${i}].confidence`, message: '置信度必须在 0-1 之间' });
      }
    }
  }

  return errors;
}

function validatePurgeParams(params: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];

  if (params.mode === 'supersede' && (!params.newRelation || typeof params.newRelation !== 'object')) {
    errors.push({ field: 'newRelation', message: 'supersede 模式必需提供 newRelation' });
  }

  if (params.newRelation) {
    const nr = params.newRelation as Record<string, unknown>;
    if (!nr.relation || typeof nr.relation !== 'string') {
      errors.push({ field: 'newRelation.relation', message: 'newRelation.relation 必须是字符串' });
    }
    if (!nr.target || typeof nr.target !== 'string') {
      errors.push({ field: 'newRelation.target', message: 'newRelation.target 必须是字符串' });
    }
  }

  return errors;
}

function validatePersonaUpdateParams(params: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];
  const attributes = params.attributes;

  if (!attributes || !Array.isArray(attributes) || attributes.length === 0) {
    errors.push({ field: 'attributes', message: 'persona_update 操作必需提供 attributes 数组' });
    return errors;
  }

  for (let i = 0; i < attributes.length; i++) {
    const attr = attributes[i] as Record<string, unknown>;
    if (!attr.attribute || typeof attr.attribute !== 'string' || attr.attribute.trim() === '') {
      errors.push({ field: `attributes[${i}].attribute`, message: '属性名不能为空字符串' });
    }
    if (attr.value === undefined || typeof attr.value !== 'string') {
      errors.push({ field: `attributes[${i}].value`, message: '属性值必须是字符串' });
    }
  }

  return errors;
}

function validateTaskCreateParams(params: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!params.task_id || typeof params.task_id !== 'string' || params.task_id.trim() === '') {
    errors.push({ field: 'task_id', message: 'task_create 操作必需提供 task_id 字符串' });
  }
  if (!params.description || typeof params.description !== 'string') {
    errors.push({ field: 'description', message: 'task_create 操作必需提供 description 字符串' });
  }

  return errors;
}

function validateTaskSetStateParams(params: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!params.task_id || typeof params.task_id !== 'string' || params.task_id.trim() === '') {
    errors.push({ field: 'task_id', message: 'task_set_state 操作必需提供 task_id 字符串' });
  }
  if (!params.state || typeof params.state !== 'string' || params.state.trim() === '') {
    errors.push({ field: 'state', message: 'task_set_state 操作必需提供 state 字符串' });
  }

  return errors;
}

function validateTaskDeleteParams(params: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!params.task_id || typeof params.task_id !== 'string' || params.task_id.trim() === '') {
    errors.push({ field: 'task_id', message: 'task_delete 操作必需提供 task_id 字符串' });
  }

  return errors;
}

function validateTaskLinkInfoParams(params: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!params.task_id || typeof params.task_id !== 'string' || params.task_id.trim() === '') {
    errors.push({ field: 'task_id', message: 'task_link_info 操作必需提供 task_id 字符串' });
  }
  if (!params.info_node || typeof params.info_node !== 'string' || params.info_node.trim() === '') {
    errors.push({ field: 'info_node', message: 'task_link_info 操作必需提供 info_node 字符串' });
  }

  return errors;
}

function validatePersonaClearParams(params: Record<string, unknown>): ValidationError[] {
  const errors: ValidationError[] = [];

  if (params.confirm === undefined) {
    errors.push({ field: 'confirm', message: 'persona_clear 操作必需设置 confirm: true 才能执行清除' });
  }

  return errors;
}

function validateParams(action: string, params: Record<string, unknown>): ValidationError[] {
  switch (action) {
    case 'recall': return validateRecallParams(params);
    case 'commit': return validateCommitParams(params);
    case 'purge': return validatePurgeParams(params);
    case 'persona_update': return validatePersonaUpdateParams(params);
    case 'persona_clear': return validatePersonaClearParams(params);
    case 'task_create': return validateTaskCreateParams(params);
    case 'task_set_state': return validateTaskSetStateParams(params);
    case 'task_delete': return validateTaskDeleteParams(params);
    case 'task_link_info': return validateTaskLinkInfoParams(params);
    default: return [];
  }
}

// ==================== 日志 ====================

class GraphMemoryLogger {
  private prefix = '[TrulyMEM]';

  info(message: string, meta?: Record<string, unknown>): void {
    console.log(`${this.prefix} [INFO] ${message}`, meta ? JSON.stringify(meta) : '');
  }

  warn(message: string, meta?: Record<string, unknown>): void {
    console.warn(`${this.prefix} [WARN] ${message}`, meta ? JSON.stringify(meta) : '');
  }

  error(message: string, meta?: Record<string, unknown>): void {
    console.error(`${this.prefix} [ERROR] ${message}`, meta ? JSON.stringify(meta) : '');
  }

  action(action: string, params: Record<string, unknown>, result?: unknown): void {
    const meta: Record<string, unknown> = { action };
    if (params && Object.keys(params).length > 0) {
      // 敏感信息脱敏：不记录具体属性值
      const sanitized = this.sanitizeParams(params);
      meta.params = sanitized;
    }
    if (result !== undefined) {
      meta.result = typeof result === 'object' && result !== null
        ? (result as Record<string, unknown>).success ?? 'ok'
        : 'ok';
    }
    this.info(`action=${action}`, meta);
  }

  private sanitizeParams(params: Record<string, unknown>): Record<string, unknown> {
    const sanitized: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(params)) {
      if (key === 'attributes') {
        sanitized[key] = Array.isArray(value)
          ? (value as Array<Record<string, unknown>>).map(a => a.attribute)
          : value;
      } else if (key === 'triplets') {
        sanitized[key] = Array.isArray(value)
          ? `${(value as unknown[]).length} triplets`
          : value;
      } else {
        sanitized[key] = value;
      }
    }
    return sanitized;
  }
}

// ==================== 主逻辑 ====================

export function createGraphMemoryTool(dbPath?: string, sessionId?: string) {
  const db = new GraphDatabase(dbPath, sessionId);
  const service = new MemoryService(db);
  const limiter = new ToolLimiter();
  const logger = new GraphMemoryLogger();

  async function executeAction(action: string, params: Record<string, unknown>): Promise<unknown> {
    // 1. 限流检查
    const [allowed, reason] = limiter.canCall(action);
    if (!allowed) {
      logger.warn(`Rate limit blocked: ${action}`, { reason });
      throw new Error(reason);
    }
    limiter.recordCall(action);

    // 2. 参数验证
    const validationErrors = validateParams(action, params);
    if (validationErrors.length > 0) {
      const errorMsg = validationErrors.map(e => `${e.field}: ${e.message}`).join('; ');
      logger.warn(`Validation failed for ${action}`, { errors: validationErrors });
      throw new Error(`参数验证失败: ${errorMsg}`);
    }

    logger.action(action, params);

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
        // confirm=false 时也要允许执行（返回 cancelled），验证只拦截 confirm 不是 boolean 的情况
        if (params.confirm === undefined) {
          throw new Error('persona_clear 操作必需设置 confirm: true 才能执行清除');
        }
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
      const actionParams = (params.params as Record<string, unknown>) || {};

      // 顶层参数验证
      if (!action || typeof action !== 'string') {
        logger.error('Missing or invalid action parameter', { params });
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: false,
              error: {
                type: 'validation_error',
                message: '必需提供 action 参数（字符串类型）'
              }
            })
          }]
        };
      }

      try {
        const result = await executeAction(action, actionParams);
        logger.action(action, actionParams, result);
        return {
          content: [{ type: 'text', text: JSON.stringify({ success: true, data: result }) }]
        };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        logger.error(`Execution failed: ${action}`, { error: errorMessage });
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: false,
              error: {
                type: 'execution_error',
                message: errorMessage
              }
            })
          }]
        };
      }
    },

    // 供测试使用的内部方法
    getLimiterSummary(): string {
      return limiter.getSummary();
    },

    resetLimiter(): void {
      limiter.reset();
      logger.info('Tool limiter reset');
    }
  };
}

export { ToolLimiter } from '../tool_limiter.js';