export interface ToolLimits {
  persona_query_max: number;
  persona_update_max: number;
  task_query_max: number;
  task_update_max: number;
  memory_query_max: number;
  memory_update_max: number;
}

export interface ToolCallCount {
  persona_query: number;
  persona_update: number;
  task_query: number;
  task_update: number;
  memory_query: number;
  memory_update: number;
}

const DEFAULT_LIMITS: ToolLimits = {
  persona_query_max: 1,
  persona_update_max: 1,
  task_query_max: 4,
  task_update_max: 5,
  memory_query_max: 20,
  memory_update_max: 10,
};

export class ToolLimiter {
  limits: ToolLimits;
  counts: ToolCallCount;

  constructor(limits?: Partial<ToolLimits>) {
    this.limits = { ...DEFAULT_LIMITS, ...limits };
    this.counts = {
      persona_query: 0,
      persona_update: 0,
      task_query: 0,
      task_update: 0,
      memory_query: 0,
      memory_update: 0,
    };
  }

  private classifyTool(action: string): [string, string] {
    switch (action) {
      case 'persona_update':
      case 'persona_clear':
        return ['persona', 'update'];
      case 'task_create':
      case 'task_set_state':
      case 'task_delete':
      case 'task_link_info':
        return ['task', 'update'];
      case 'recall':
      case 'introspect':
        return ['memory', 'query'];
      case 'commit':
      case 'purge':
      case 'archive':
      case 'cleanup':
        return ['memory', 'update'];
      default:
        return ['memory', 'update'];
    }
  }

  canCall(action: string): [boolean, string] {
    const [category, operation] = this.classifyTool(action);

    if (category === 'persona') {
      if (operation === 'query') {
        if (this.counts.persona_query >= this.limits.persona_query_max) {
          return [false, `人设图查询次数已达上限(${this.limits.persona_query_max}次)`];
        }
      } else {
        if (this.counts.persona_update >= this.limits.persona_update_max) {
          return [false, `人设图修改次数已达上限(${this.limits.persona_update_max}次)`];
        }
      }
    } else if (category === 'task') {
      if (operation === 'query') {
        if (this.counts.task_query >= this.limits.task_query_max) {
          return [false, `工作记忆链查询次数已达上限(${this.limits.task_query_max}次)`];
        }
      } else {
        if (this.counts.task_update >= this.limits.task_update_max) {
          return [false, `工作记忆链修改次数已达上限(${this.limits.task_update_max}次)`];
        }
      }
    } else if (category === 'memory') {
      if (operation === 'query') {
        if (this.counts.memory_query >= this.limits.memory_query_max) {
          return [false, `一般记忆查询次数已达上限(${this.limits.memory_query_max}次)`];
        }
      } else {
        if (this.counts.memory_update >= this.limits.memory_update_max) {
          return [false, `一般记忆修改次数已达上限(${this.limits.memory_update_max}次)`];
        }
      }
    }

    return [true, '允许调用'];
  }

  recordCall(action: string): void {
    const [category, operation] = this.classifyTool(action);

    if (category === 'persona') {
      if (operation === 'query') this.counts.persona_query++;
      else this.counts.persona_update++;
    } else if (category === 'task') {
      if (operation === 'query') this.counts.task_query++;
      else this.counts.task_update++;
    } else if (category === 'memory') {
      if (operation === 'query') this.counts.memory_query++;
      else this.counts.memory_update++;
    }
  }

  getSummary(): string {
    const lines = [
      `人设图: 查询${this.counts.persona_query}/${this.limits.persona_query_max}次, 修改${this.counts.persona_update}/${this.limits.persona_update_max}次`,
      `工作记忆链: 查询${this.counts.task_query}/${this.limits.task_query_max}次, 修改${this.counts.task_update}/${this.limits.task_update_max}次`,
      `一般记忆: 查询${this.counts.memory_query}/${this.limits.memory_query_max}次, 修改${this.counts.memory_update}/${this.limits.memory_update_max}次`,
    ];
    return lines.join('\n');
  }

  reset(): void {
    this.counts = {
      persona_query: 0,
      persona_update: 0,
      task_query: 0,
      task_update: 0,
      memory_query: 0,
      memory_update: 0,
    };
  }
}
