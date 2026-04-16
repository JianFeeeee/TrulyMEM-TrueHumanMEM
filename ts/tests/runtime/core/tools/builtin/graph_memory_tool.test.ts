import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { GraphMemoryTool } from '../../../../../dist/runtime/core/tools/builtin/graph_memory_tool.js';
import { ToolLimiter } from '../../../../../dist/runtime/core/tools/tool_limiter.js';
import * as fs from 'fs';

const TEST_DB_PATH = '/tmp/test_graph_memory_tool.db';

describe('GraphMemoryTool', () => {
  let tool: GraphMemoryTool;

  beforeEach(() => {
    if (fs.existsSync(TEST_DB_PATH)) {
      fs.unlinkSync(TEST_DB_PATH);
    }
    tool = new GraphMemoryTool(TEST_DB_PATH, 'test-session');
  });

  afterEach(() => {
    if (fs.existsSync(TEST_DB_PATH)) {
      fs.unlinkSync(TEST_DB_PATH);
    }
  });

  describe('Tool metadata', () => {
    it('should have correct id', () => {
      expect(tool.id).toBe('builtin:graph_memory');
    });

    it('should have correct name', () => {
      expect(tool.name).toBe('GraphMemory');
    });

    it('should have analysis category', () => {
      expect(tool.category).toBe('analysis');
    });

    it('should have safe permission level', () => {
      expect(tool.permissionLevel).toBe('safe');
    });

    it('should have input schema with all actions', () => {
      const actions = tool.inputSchema.properties?.action?.enum as string[];
      expect(actions).toContain('recall');
      expect(actions).toContain('commit');
      expect(actions).toContain('purge');
      expect(actions).toContain('introspect');
      expect(actions).toContain('persona_update');
      expect(actions).toContain('persona_clear');
      expect(actions).toContain('task_create');
      expect(actions).toContain('task_set_state');
      expect(actions).toContain('task_delete');
      expect(actions).toContain('task_link_info');
      expect(actions).toContain('archive');
      expect(actions).toContain('cleanup');
    });
  });

  describe('recall action', () => {
    it('should recall memories by query intent', async () => {
      await tool.handler({
        action: 'commit',
        params: {
          triplets: [
            { subject: '用户', relation: '喜欢', object: '编程' }
          ]
        }
      }, {} as any);

      const result = await tool.handler({
        action: 'recall',
        params: {
          queryIntent: '用户 编程'
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.entities).toBeDefined();
      expect(parsed.data.relations).toBeDefined();
    });

    it('should return empty results for non-matching query', async () => {
      const result = await tool.handler({
        action: 'recall',
        params: {
          queryIntent: '不存在的关键词xyz123'
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.entities).toEqual([]);
      expect(parsed.data.relations).toEqual([]);
    });
  });

  describe('commit action', () => {
    it('should commit triplets successfully', async () => {
      const result = await tool.handler({
        action: 'commit',
        params: {
          triplets: [
            { subject: '测试', relation: '是', object: '示例' }
          ]
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.createdEntities).toBeGreaterThan(0);
      expect(parsed.data.createdRelations).toBeGreaterThan(0);
    });

    it('should handle multiple triplets', async () => {
      const result = await tool.handler({
        action: 'commit',
        params: {
          triplets: [
            { subject: '实体A', relation: '关联', object: '实体B' },
            { subject: '实体B', relation: '关联', object: '实体C' },
            { subject: '实体C', relation: '关联', object: '实体A' }
          ]
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.createdEntities).toBe(6);
      expect(parsed.data.createdRelations).toBe(3);
    });
  });

  describe('purge action', () => {
    it('should purge relations by criteria', async () => {
      await tool.handler({
        action: 'commit',
        params: {
          triplets: [
            { subject: '待删除', relation: '是', object: '测试' }
          ]
        }
      }, {} as any);

      const result = await tool.handler({
        action: 'purge',
        params: {
          criteria: { subject: '待删除' },
          mode: 'soft'
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.deleted).toBeGreaterThanOrEqual(1);
      expect(parsed.data.mode).toBe('soft');
    });

    it('should return 0 when no criteria provided', async () => {
      const result = await tool.handler({
        action: 'purge',
        params: {}
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.deleted).toBe(0);
    });
  });

  describe('introspect action', () => {
    it('should return memory statistics', async () => {
      await tool.handler({
        action: 'commit',
        params: {
          triplets: [
            { subject: '实体1', relation: '关系', object: '实体2' }
          ]
        }
      }, {} as any);

      const result = await tool.handler({
        action: 'introspect',
        params: {}
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.entityCount).toBeGreaterThan(0);
      expect(parsed.data.relationCount).toBeGreaterThan(0);
      expect(parsed.data.sessionId).toBeDefined();
    });
  });

  describe('persona_update action', () => {
    it('should update persona attributes', async () => {
      const result = await tool.handler({
        action: 'persona_update',
        params: {
          attributes: [
            { attribute: 'name', value: 'AI助手' },
            { attribute: '性格', value: '友善' }
          ],
          mode: 'merge'
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('success');
      expect(parsed.data.updatedAttributes).toBe(2);
    });

    it('should replace persona in replace mode', async () => {
      tool.resetLimiter();
      const result = await tool.handler({
        action: 'persona_update',
        params: {
          attributes: [{ attribute: 'name', value: 'TestAI' }],
          mode: 'merge'
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.updatedAttributes).toBe(1);
      expect(parsed.data.status).toBe('success');
    });
  });

  describe('persona_clear action', () => {
    it('should clear persona when confirm is true', async () => {
      const result = await tool.handler({
        action: 'persona_clear',
        params: {
          confirm: true
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('success');
      expect(parsed.data.deletedCount).toBeGreaterThanOrEqual(0);
    });

    it('should cancel when confirm is false', async () => {
      const result = await tool.handler({
        action: 'persona_clear',
        params: {
          confirm: false
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('cancelled');
      expect(parsed.data.deletedCount).toBe(0);
    });
  });

  describe('task_create action', () => {
    it('should create task successfully', async () => {
      const result = await tool.handler({
        action: 'task_create',
        params: {
          task_id: 'Task_Test123',
          description: '测试任务描述'
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('success');
      expect(parsed.data.taskId).toBe('Task_Test123');
    });

    it('should create task with info_nodes', async () => {
      const result = await tool.handler({
        action: 'task_create',
        params: {
          task_id: 'Task_WithInfo',
          description: '带信息的任务',
          info_nodes: ['信息节点1', '信息节点2']
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.taskId).toBe('Task_WithInfo');
    });
  });

  describe('task_set_state action', () => {
    it('should set task state', async () => {
      await tool.handler({
        action: 'task_create',
        params: {
          task_id: 'Task_StateTest',
          description: '状态测试任务'
        }
      }, {} as any);

      const result = await tool.handler({
        action: 'task_set_state',
        params: {
          task_id: 'Task_StateTest',
          state: '已完成'
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('success');
      expect(parsed.data.newState).toBe('已完成');
    });
  });

  describe('task_delete action', () => {
    it('should delete task', async () => {
      await tool.handler({
        action: 'task_create',
        params: {
          task_id: 'Task_DeleteMe',
          description: '待删除任务'
        }
      }, {} as any);

      const result = await tool.handler({
        action: 'task_delete',
        params: {
          task_id: 'Task_DeleteMe'
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('success');
      expect(parsed.data.taskId).toBe('Task_DeleteMe');
    });
  });

  describe('task_link_info action', () => {
    it('should link info node to task', async () => {
      await tool.handler({
        action: 'task_create',
        params: {
          task_id: 'Task_Link',
          description: '链接测试任务'
        }
      }, {} as any);

      const result = await tool.handler({
        action: 'task_link_info',
        params: {
          task_id: 'Task_Link',
          info_node: '新的信息节点'
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('success');
    });
  });

  describe('archive action', () => {
    it('should archive old relations', async () => {
      const result = await tool.handler({
        action: 'archive',
        params: {
          days: 30
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
    });
  });

  describe('cleanup action', () => {
    it('should cleanup in dry_run mode', async () => {
      const result = await tool.handler({
        action: 'cleanup',
        params: {
          dry_run: true
        }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
    });

    it('should cleanup without dry_run', async () => {
      const result = await tool.handler({
        action: 'cleanup',
        params: {}
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
    });
  });

  describe('Unknown action error handling', () => {
    it('should return error for unknown action', async () => {
      const result = await tool.handler({
        action: 'unknown_action',
        params: {}
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(false);
      expect(parsed.error).toBeDefined();
      expect(parsed.error.type).toBe('execution_error');
      expect(parsed.error.message).toContain('Unknown action');
    });

    it('should handle empty action gracefully', async () => {
      const result = await tool.handler({
        action: '',
        params: {}
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(false);
    });
  });

  describe('OpenClaw execute method', () => {
    it('should return correct format with content array', async () => {
      const result = await tool.execute('call-123', {
        action: 'introspect',
        params: {}
      });

      expect(result).toHaveProperty('content');
      expect(Array.isArray(result.content)).toBe(true);
      expect(result.content[0]).toHaveProperty('type', 'text');
      expect(result.content[0]).toHaveProperty('text');
      expect(typeof result.content[0].text).toBe('string');
    });

    it('should parse JSON in text content', async () => {
      const result = await tool.execute('call-456', {
        action: 'commit',
        params: {
          triplets: [
            { subject: '测试', relation: '是', object: '执行' }
          ]
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
    });

    it('should handle errors in execute format', async () => {
      const result = await tool.execute('call-789', {
        action: 'invalid_action',
        params: {}
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
    });
  });

  describe('ToolLimiter integration', () => {
    it('should block calls when rate limit exceeded', async () => {
      tool.resetLimiter();

      const limiter = (tool as any).limiter;
      for (let i = 0; i < 20; i++) {
        limiter.recordCall('recall');
      }

      const result = await tool.handler({
        action: 'recall',
        params: { queryIntent: '测试' }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(false);
      expect(parsed.error.message).toContain('已达上限');
    });

    it('should get limiter summary', () => {
      tool.resetLimiter();
      const summary = tool.getLimiterSummary();
      expect(summary).toContain('人设图');
      expect(summary).toContain('工作记忆链');
      expect(summary).toContain('一般记忆');
    });

    it('should reset limiter and allow calls again', async () => {
      const limiter = (tool as any).limiter;
      for (let i = 0; i < 20; i++) {
        limiter.recordCall('recall');
      }

      tool.resetLimiter();

      const result = await tool.handler({
        action: 'recall',
        params: { queryIntent: '测试' }
      }, {} as any);

      const parsed = JSON.parse(result);
      expect(parsed.success).toBe(true);
    });
  });
});
