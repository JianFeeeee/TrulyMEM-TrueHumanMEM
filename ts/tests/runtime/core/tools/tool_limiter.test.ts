import { describe, it, expect, beforeEach } from 'vitest';
import { ToolLimiter } from '../../../../dist/runtime/core/tools/tool_limiter.js';

describe('ToolLimiter', () => {
  describe('Default limits', () => {
    it('should have correct default limits', () => {
      const limiter = new ToolLimiter();

      expect(limiter.limits.persona_query_max).toBe(1);
      expect(limiter.limits.persona_update_max).toBe(1);
      expect(limiter.limits.task_query_max).toBe(4);
      expect(limiter.limits.task_update_max).toBe(5);
      expect(limiter.limits.memory_query_max).toBe(20);
      expect(limiter.limits.memory_update_max).toBe(10);
    });

    it('should initialize counts to zero', () => {
      const limiter = new ToolLimiter();

      expect(limiter.counts.persona_query).toBe(0);
      expect(limiter.counts.persona_update).toBe(0);
      expect(limiter.counts.task_query).toBe(0);
      expect(limiter.counts.task_update).toBe(0);
      expect(limiter.counts.memory_query).toBe(0);
      expect(limiter.counts.memory_update).toBe(0);
    });
  });

  describe('canCall allows within limits', () => {
    let limiter: ToolLimiter;

    beforeEach(() => {
      limiter = new ToolLimiter();
    });

    it('should allow recall (memory query) initially', () => {
      const [allowed, reason] = limiter.canCall('recall');
      expect(allowed).toBe(true);
      expect(reason).toBe('允许调用');
    });

    it('should allow introspect (memory query) initially', () => {
      const [allowed, reason] = limiter.canCall('introspect');
      expect(allowed).toBe(true);
      expect(reason).toBe('允许调用');
    });

    it('should allow commit (memory update) initially', () => {
      const [allowed, reason] = limiter.canCall('commit');
      expect(allowed).toBe(true);
      expect(reason).toBe('允许调用');
    });

    it('should allow task operations initially', () => {
      expect(limiter.canCall('task_create')[0]).toBe(true);
      expect(limiter.canCall('task_set_state')[0]).toBe(true);
      expect(limiter.canCall('task_delete')[0]).toBe(true);
      expect(limiter.canCall('task_link_info')[0]).toBe(true);
    });

    it('should allow persona operations initially', () => {
      expect(limiter.canCall('persona_update')[0]).toBe(true);
      expect(limiter.canCall('persona_clear')[0]).toBe(true);
    });

    it('should allow purge initially', () => {
      const [allowed] = limiter.canCall('purge');
      expect(allowed).toBe(true);
    });

    it('should allow archive initially', () => {
      const [allowed] = limiter.canCall('archive');
      expect(allowed).toBe(true);
    });

    it('should allow cleanup initially', () => {
      const [allowed] = limiter.canCall('cleanup');
      expect(allowed).toBe(true);
    });
  });

  describe('canCall blocks when exceeded', () => {
    let limiter: ToolLimiter;

    beforeEach(() => {
      limiter = new ToolLimiter();
    });

    it('should block recall after 20 calls', () => {
      for (let i = 0; i < 20; i++) {
        limiter.recordCall('recall');
      }

      const [allowed, reason] = limiter.canCall('recall');
      expect(allowed).toBe(false);
      expect(reason).toContain('一般记忆查询次数已达上限');
      expect(reason).toContain('20');
    });

    it('should block commit after 10 calls', () => {
      for (let i = 0; i < 10; i++) {
        limiter.recordCall('commit');
      }

      const [allowed, reason] = limiter.canCall('commit');
      expect(allowed).toBe(false);
      expect(reason).toContain('一般记忆修改次数已达上限');
    });

    it('should block purge after 10 calls', () => {
      for (let i = 0; i < 10; i++) {
        limiter.recordCall('purge');
      }

      const [allowed] = limiter.canCall('purge');
      expect(allowed).toBe(false);
    });

    it('should block task operations after 5 updates', () => {
      for (let i = 0; i < 5; i++) {
        limiter.recordCall('task_create');
      }

      const [allowed] = limiter.canCall('task_create');
      expect(allowed).toBe(false);
    });

    it('should block task_set_state after 5 updates', () => {
      for (let i = 0; i < 5; i++) {
        limiter.recordCall('task_set_state');
      }

      const [allowed] = limiter.canCall('task_set_state');
      expect(allowed).toBe(false);
    });

    it('should block persona_update after 1 call', () => {
      limiter.recordCall('persona_update');

      const [allowed] = limiter.canCall('persona_update');
      expect(allowed).toBe(false);
    });

    it('should block persona_clear after 1 call', () => {
      limiter.recordCall('persona_clear');

      const [allowed] = limiter.canCall('persona_clear');
      expect(allowed).toBe(false);
    });

    it('should block unknown actions as memory update', () => {
      for (let i = 0; i < 10; i++) {
        limiter.recordCall('unknown_action');
      }

      const [allowed] = limiter.canCall('unknown_action');
      expect(allowed).toBe(false);
    });
  });

  describe('recordCall increments counters', () => {
    let limiter: ToolLimiter;

    beforeEach(() => {
      limiter = new ToolLimiter();
    });

    it('should increment memory_query for recall', () => {
      limiter.recordCall('recall');
      expect(limiter.counts.memory_query).toBe(1);

      limiter.recordCall('recall');
      expect(limiter.counts.memory_query).toBe(2);
    });

    it('should increment memory_query for introspect', () => {
      limiter.recordCall('introspect');
      expect(limiter.counts.memory_query).toBe(1);
    });

    it('should increment memory_update for commit', () => {
      limiter.recordCall('commit');
      expect(limiter.counts.memory_update).toBe(1);
    });

    it('should increment memory_update for purge', () => {
      limiter.recordCall('purge');
      expect(limiter.counts.memory_update).toBe(1);
    });

    it('should increment memory_update for archive', () => {
      limiter.recordCall('archive');
      expect(limiter.counts.memory_update).toBe(1);
    });

    it('should increment memory_update for cleanup', () => {
      limiter.recordCall('cleanup');
      expect(limiter.counts.memory_update).toBe(1);
    });

    it('should increment task_update for task operations', () => {
      limiter.recordCall('task_create');
      limiter.recordCall('task_set_state');
      limiter.recordCall('task_delete');
      limiter.recordCall('task_link_info');

      expect(limiter.counts.task_update).toBe(4);
    });

    it('should increment persona_update for persona operations', () => {
      limiter.recordCall('persona_update');
      limiter.recordCall('persona_clear');

      expect(limiter.counts.persona_update).toBe(2);
    });

    it('should handle unknown actions as memory update', () => {
      limiter.recordCall('some_unknown_action');

      expect(limiter.counts.memory_update).toBe(1);
    });
  });

  describe('reset clears counters', () => {
    it('should reset all counts to zero', () => {
      const limiter = new ToolLimiter();

      limiter.recordCall('recall');
      limiter.recordCall('recall');
      limiter.recordCall('commit');
      limiter.recordCall('task_create');
      limiter.recordCall('persona_update');

      limiter.reset();

      expect(limiter.counts.persona_query).toBe(0);
      expect(limiter.counts.persona_update).toBe(0);
      expect(limiter.counts.task_query).toBe(0);
      expect(limiter.counts.task_update).toBe(0);
      expect(limiter.counts.memory_query).toBe(0);
      expect(limiter.counts.memory_update).toBe(0);
    });

    it('should allow calls after reset', () => {
      const limiter = new ToolLimiter();

      for (let i = 0; i < 20; i++) {
        limiter.recordCall('recall');
      }

      limiter.reset();

      const [allowed] = limiter.canCall('recall');
      expect(allowed).toBe(true);
    });
  });

  describe('getSummary returns formatted string', () => {
    it('should return summary with correct format', () => {
      const limiter = new ToolLimiter();
      const summary = limiter.getSummary();

      expect(summary).toContain('人设图');
      expect(summary).toContain('工作记忆链');
      expect(summary).toContain('一般记忆');
      expect(summary).toContain('查询');
      expect(summary).toContain('修改');
      expect(summary).toContain('/');
    });

    it('should show updated counts in summary', () => {
      const limiter = new ToolLimiter();

      limiter.recordCall('recall');
      limiter.recordCall('recall');
      limiter.recordCall('commit');

      const summary = limiter.getSummary();
      expect(summary).toContain('2/20');
      expect(summary).toContain('1/10');
    });
  });

  describe('classifyTool for all action types', () => {
    let limiter: ToolLimiter;

    beforeEach(() => {
      limiter = new ToolLimiter();
    });

    it('should classify recall as memory query', () => {
      for (let i = 0; i < 20; i++) limiter.recordCall('recall');
      const [, reason] = limiter.canCall('recall');
      expect(reason).toContain('一般记忆查询');
    });

    it('should classify introspect as memory query', () => {
      for (let i = 0; i < 20; i++) limiter.recordCall('introspect');
      const [, reason] = limiter.canCall('introspect');
      expect(reason).toContain('一般记忆查询');
    });

    it('should classify commit as memory update', () => {
      for (let i = 0; i < 10; i++) limiter.recordCall('commit');
      const [, reason] = limiter.canCall('commit');
      expect(reason).toContain('一般记忆修改');
    });

    it('should classify purge as memory update', () => {
      for (let i = 0; i < 10; i++) limiter.recordCall('purge');
      const [, reason] = limiter.canCall('purge');
      expect(reason).toContain('一般记忆修改');
    });

    it('should classify archive as memory update', () => {
      for (let i = 0; i < 10; i++) limiter.recordCall('archive');
      const [, reason] = limiter.canCall('archive');
      expect(reason).toContain('一般记忆修改');
    });

    it('should classify cleanup as memory update', () => {
      for (let i = 0; i < 10; i++) limiter.recordCall('cleanup');
      const [, reason] = limiter.canCall('cleanup');
      expect(reason).toContain('一般记忆修改');
    });

    it('should classify task_create as task update', () => {
      for (let i = 0; i < 5; i++) limiter.recordCall('task_create');
      const [, reason] = limiter.canCall('task_create');
      expect(reason).toContain('工作记忆链修改');
    });

    it('should classify task_set_state as task update', () => {
      for (let i = 0; i < 5; i++) limiter.recordCall('task_set_state');
      const [, reason] = limiter.canCall('task_set_state');
      expect(reason).toContain('工作记忆链修改');
    });

    it('should classify task_delete as task update', () => {
      for (let i = 0; i < 5; i++) limiter.recordCall('task_delete');
      const [, reason] = limiter.canCall('task_delete');
      expect(reason).toContain('工作记忆链修改');
    });

    it('should classify task_link_info as task update', () => {
      for (let i = 0; i < 5; i++) limiter.recordCall('task_link_info');
      const [, reason] = limiter.canCall('task_link_info');
      expect(reason).toContain('工作记忆链修改');
    });

    it('should classify persona_update as persona update', () => {
      limiter.recordCall('persona_update');
      const [, reason] = limiter.canCall('persona_update');
      expect(reason).toContain('人设图修改');
    });

    it('should classify persona_clear as persona update', () => {
      limiter.recordCall('persona_clear');
      const [, reason] = limiter.canCall('persona_clear');
      expect(reason).toContain('人设图修改');
    });

    it('should classify unknown action as memory update', () => {
      for (let i = 0; i < 10; i++) limiter.recordCall('totally_unknown');
      const [, reason] = limiter.canCall('totally_unknown');
      expect(reason).toContain('一般记忆修改');
    });
  });

  describe('Custom limits override', () => {
    it('should accept custom limits', () => {
      const limiter = new ToolLimiter({
        memory_query_max: 100,
        memory_update_max: 50
      });

      expect(limiter.limits.memory_query_max).toBe(100);
      expect(limiter.limits.memory_update_max).toBe(50);
      expect(limiter.limits.task_query_max).toBe(4);
    });

    it('should merge custom limits with defaults', () => {
      const limiter = new ToolLimiter({
        persona_update_max: 5
      });

      expect(limiter.limits.persona_update_max).toBe(5);
      expect(limiter.limits.persona_query_max).toBe(1);
    });

    it('should allow unlimited calls with high custom limits', () => {
      const limiter = new ToolLimiter({
        memory_query_max: 10000,
        memory_update_max: 10000
      });

      for (let i = 0; i < 100; i++) {
        limiter.recordCall('recall');
        limiter.recordCall('commit');
      }

      expect(limiter.canCall('recall')[0]).toBe(true);
      expect(limiter.canCall('commit')[0]).toBe(true);
    });

    it('should allow zero limits to block immediately', () => {
      const limiter = new ToolLimiter({
        task_update_max: 0
      });

      const [allowed] = limiter.canCall('task_create');
      expect(allowed).toBe(false);
    });

    it('should preserve custom limits after reset', () => {
      const limiter = new ToolLimiter({
        memory_query_max: 500
      });

      for (let i = 0; i < 100; i++) {
        limiter.recordCall('recall');
      }

      limiter.reset();

      expect(limiter.limits.memory_query_max).toBe(500);
      expect(limiter.counts.memory_query).toBe(0);

      const [allowed] = limiter.canCall('recall');
      expect(allowed).toBe(true);
    });
  });
});
