import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { createGraphMemoryTool, ToolLimiter } from '../../../../../dist/runtime/core/tools/builtin/graph_memory_tool.js';
import * as fs from 'fs';

const TEST_DB_PATH = '/tmp/test_graph_memory_tool.db';

describe('GraphMemoryTool', () => {
  let tool: ReturnType<typeof createGraphMemoryTool>;

  beforeEach(() => {
    if (fs.existsSync(TEST_DB_PATH)) {
      fs.unlinkSync(TEST_DB_PATH);
    }
    tool = createGraphMemoryTool(TEST_DB_PATH, 'test-session');
  });

  afterEach(() => {
    if (fs.existsSync(TEST_DB_PATH)) {
      fs.unlinkSync(TEST_DB_PATH);
    }
  });

  describe('Tool metadata', () => {
    it('should have correct name', () => {
      expect(tool.name).toBe('graph_memory');
    });

    it('should have description', () => {
      expect(tool.description).toBeTruthy();
      expect(tool.description).toContain('图记忆');
    });

    it('should have input schema with all actions', () => {
      const actions = tool.parameters.properties?.action?.enum as string[];
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

  describe('execute wrapper', () => {
    it('should execute recall action', async () => {
      await tool.execute('call-1', {
        action: 'commit',
        params: {
          triplets: [
            { subject: '用户', relation: '喜欢', object: '编程' }
          ]
        }
      });

      const result = await tool.execute('call-2', {
        action: 'recall',
        params: {
          queryIntent: '用户 编程'
        }
      });

      expect(result).toHaveProperty('content');
      expect(Array.isArray(result.content)).toBe(true);
      expect(result.content[0]).toHaveProperty('type', 'text');

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.entities).toBeDefined();
      expect(parsed.data.relations).toBeDefined();
    });

    it('should return empty results for non-matching query', async () => {
      const result = await tool.execute('call-3', {
        action: 'recall',
        params: {
          queryIntent: '不存在的关键词xyz123'
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.entities).toEqual([]);
      expect(parsed.data.relations).toEqual([]);
    });

    it('should commit triplets successfully', async () => {
      const result = await tool.execute('call-4', {
        action: 'commit',
        params: {
          triplets: [
            { subject: '测试', relation: '是', object: '示例' }
          ]
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.createdEntities).toBeGreaterThan(0);
      expect(parsed.data.createdRelations).toBeGreaterThan(0);
    });

    it('should handle multiple triplets', async () => {
      const result = await tool.execute('call-5', {
        action: 'commit',
        params: {
          triplets: [
            { subject: '实体A', relation: '关联', object: '实体B' },
            { subject: '实体B', relation: '关联', object: '实体C' },
            { subject: '实体C', relation: '关联', object: '实体A' }
          ]
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.createdEntities).toBe(6);
      expect(parsed.data.createdRelations).toBe(3);
    });

    it('should purge relations by criteria', async () => {
      await tool.execute('call-6', {
        action: 'commit',
        params: {
          triplets: [
            { subject: '待删除', relation: '是', object: '测试' }
          ]
        }
      });

      const result = await tool.execute('call-7', {
        action: 'purge',
        params: {
          criteria: { subject: '待删除' },
          mode: 'soft'
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.deleted).toBeGreaterThanOrEqual(1);
      expect(parsed.data.mode).toBe('soft');
    });

    it('should return 0 when no criteria provided', async () => {
      const result = await tool.execute('call-8', {
        action: 'purge',
        params: {}
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.deleted).toBe(0);
    });

    it('should return memory statistics', async () => {
      await tool.execute('call-9', {
        action: 'commit',
        params: {
          triplets: [
            { subject: '实体1', relation: '关系', object: '实体2' }
          ]
        }
      });

      const result = await tool.execute('call-10', {
        action: 'introspect',
        params: {}
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.entityCount).toBeGreaterThan(0);
      expect(parsed.data.relationCount).toBeGreaterThan(0);
      expect(parsed.data.sessionId).toBeDefined();
    });

    it('should update persona attributes', async () => {
      const result = await tool.execute('call-11', {
        action: 'persona_update',
        params: {
          attributes: [
            { attribute: 'name', value: 'AI助手' },
            { attribute: '性格', value: '友善' }
          ],
          mode: 'merge'
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('success');
      expect(parsed.data.updatedAttributes).toBe(2);
    });

    it('should clear persona when confirm is true', async () => {
      const result = await tool.execute('call-12', {
        action: 'persona_clear',
        params: {
          confirm: true
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('success');
      expect(parsed.data.deletedCount).toBeGreaterThanOrEqual(0);
    });

    it('should cancel when confirm is false', async () => {
      const result = await tool.execute('call-13', {
        action: 'persona_clear',
        params: {
          confirm: false
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('cancelled');
      expect(parsed.data.deletedCount).toBe(0);
    });

    it('should create task successfully', async () => {
      const result = await tool.execute('call-14', {
        action: 'task_create',
        params: {
          task_id: 'Task_Test123',
          description: '测试任务描述'
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('success');
      expect(parsed.data.taskId).toBe('Task_Test123');
    });

    it('should create task with info_nodes', async () => {
      const result = await tool.execute('call-15', {
        action: 'task_create',
        params: {
          task_id: 'Task_WithInfo',
          description: '带信息的任务',
          info_nodes: ['信息节点1', '信息节点2']
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.taskId).toBe('Task_WithInfo');
    });

    it('should set task state', async () => {
      await tool.execute('call-16', {
        action: 'task_create',
        params: {
          task_id: 'Task_StateTest',
          description: '状态测试任务'
        }
      });

      const result = await tool.execute('call-17', {
        action: 'task_set_state',
        params: {
          task_id: 'Task_StateTest',
          state: '已完成'
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('success');
      expect(parsed.data.newState).toBe('已完成');
    });

    it('should delete task', async () => {
      await tool.execute('call-18', {
        action: 'task_create',
        params: {
          task_id: 'Task_DeleteMe',
          description: '待删除任务'
        }
      });

      const result = await tool.execute('call-19', {
        action: 'task_delete',
        params: {
          task_id: 'Task_DeleteMe'
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('success');
      expect(parsed.data.taskId).toBe('Task_DeleteMe');
    });

    it('should link info node to task', async () => {
      await tool.execute('call-20', {
        action: 'task_create',
        params: {
          task_id: 'Task_Link',
          description: '链接测试任务'
        }
      });

      const result = await tool.execute('call-21', {
        action: 'task_link_info',
        params: {
          task_id: 'Task_Link',
          info_node: '新的信息节点'
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('success');
    });

    it('should archive old relations', async () => {
      const result = await tool.execute('call-22', {
        action: 'archive',
        params: {
          days: 30
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
    });

    it('should cleanup in dry_run mode', async () => {
      const result = await tool.execute('call-23', {
        action: 'cleanup',
        params: {
          dry_run: true
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
    });

    it('should cleanup without dry_run', async () => {
      const result = await tool.execute('call-24', {
        action: 'cleanup',
        params: {}
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
    });

    it('should return error for unknown action', async () => {
      const result = await tool.execute('call-25', {
        action: 'invalid_action',
        params: {}
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
      expect(parsed.error).toBeDefined();
    });

    it('should handle errors in execute format', async () => {
      const result = await tool.execute('call-26', {
        action: '',
        params: {}
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
    });

    it('should handle limiter blocking', async () => {
      const newTool = createGraphMemoryTool(TEST_DB_PATH + '.limiter', 'limiter-session');

      // Fill up memory_query limit
      for (let i = 0; i < 20; i++) {
        await newTool.execute(`limiter-call-${i}`, {
          action: 'introspect',
          params: {}
        });
      }

      // Next recall should be blocked
      const result = await newTool.execute('limiter-blocked', {
        action: 'recall',
        params: { queryIntent: '测试' }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
      expect(parsed.error.message).toContain('已达上限');
    });
  });

  describe('ToolLimiter standalone', () => {
    it('should limit memory query calls', () => {
      const limiter = new ToolLimiter();

      for (let i = 0; i < 20; i++) {
        const [allowed] = limiter.canCall('recall');
        if (allowed) limiter.recordCall('recall');
      }

      const [allowed] = limiter.canCall('recall');
      expect(allowed).toBe(false);
    });

    it('should limit memory update calls', () => {
      const limiter = new ToolLimiter();

      for (let i = 0; i < 10; i++) {
        const [allowed] = limiter.canCall('commit');
        if (allowed) limiter.recordCall('commit');
      }

      const [allowed] = limiter.canCall('commit');
      expect(allowed).toBe(false);
    });

    it('should get summary', () => {
      const limiter = new ToolLimiter();
      const summary = limiter.getSummary();
      expect(summary).toContain('人设图');
      expect(summary).toContain('工作记忆链');
      expect(summary).toContain('一般记忆');
    });

    it('should reset and allow calls again', () => {
      const limiter = new ToolLimiter();

      for (let i = 0; i < 20; i++) {
        const [allowed] = limiter.canCall('recall');
        if (allowed) limiter.recordCall('recall');
      }

      expect(limiter.canCall('recall')[0]).toBe(false);
      limiter.reset();
      expect(limiter.canCall('recall')[0]).toBe(true);
    });
  });

  describe('Parameter validation', () => {
    it('should reject commit without triplets', async () => {
      const result = await tool.execute('call-val-1', {
        action: 'commit',
        params: {}
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
      expect(parsed.error.message).toContain('triplets');
    });

    it('should reject commit with empty triplet fields', async () => {
      const result = await tool.execute('call-val-2', {
        action: 'commit',
        params: {
          triplets: [{ subject: '', relation: '是', object: '测试' }]
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
      expect(parsed.error.message).toContain('subject');
    });

    it('should reject persona_update without attributes', async () => {
      const result = await tool.execute('call-val-3', {
        action: 'persona_update',
        params: {}
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
      expect(parsed.error.message).toContain('attributes');
    });

    it('should reject persona_clear without confirm', async () => {
      const result = await tool.execute('call-val-4', {
        action: 'persona_clear',
        params: {}
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
      expect(parsed.error.message).toContain('confirm');
    });

    it('should allow persona_clear with confirm=false and return cancelled', async () => {
      const result = await tool.execute('call-val-4b', {
        action: 'persona_clear',
        params: { confirm: false }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(true);
      expect(parsed.data.status).toBe('cancelled');
      expect(parsed.data.deletedCount).toBe(0);
    });

    it('should reject task_create without task_id', async () => {
      const result = await tool.execute('call-val-5', {
        action: 'task_create',
        params: { description: '测试' }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
      expect(parsed.error.message).toContain('task_id');
    });

    it('should reject task_set_state without state', async () => {
      const result = await tool.execute('call-val-6', {
        action: 'task_set_state',
        params: { task_id: 'T1' }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
      expect(parsed.error.message).toContain('state');
    });

    it('should reject recall without queryIntent and seedEntities', async () => {
      const result = await tool.execute('call-val-7', {
        action: 'recall',
        params: {}
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
      expect(parsed.error.message).toContain('queryIntent');
    });

    it('should reject depth out of range', async () => {
      const result = await tool.execute('call-val-8', {
        action: 'recall',
        params: { queryIntent: '测试', depth: 10 }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
      expect(parsed.error.message).toContain('depth');
    });

    it('should reject commit with invalid confidence', async () => {
      const result = await tool.execute('call-val-9', {
        action: 'commit',
        params: {
          triplets: [{ subject: 'A', relation: '是', object: 'B', confidence: 2 }]
        }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
      expect(parsed.error.message).toContain('置信度');
    });

    it('should reject purge supersede without newRelation', async () => {
      const result = await tool.execute('call-val-10', {
        action: 'purge',
        params: { mode: 'supersede' }
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
      expect(parsed.error.message).toContain('newRelation');
    });

    it('should reject missing action', async () => {
      const result = await tool.execute('call-val-11', {
        action: '',
        params: {}
      });

      const parsed = JSON.parse(result.content[0].text);
      expect(parsed.success).toBe(false);
      expect(parsed.error.message).toContain('action');
    });
  });
});
