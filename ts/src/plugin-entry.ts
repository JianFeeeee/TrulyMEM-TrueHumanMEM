import { GraphMemoryToolSchema, createGraphMemoryTool } from './runtime/core/tools/builtin/graph_memory_tool.js';

export default {
  id: 'graph-memory',
  name: 'Graph Memory',
  description: '让 AI 拥有真正的长期记忆能力 - 基于图数据库的记忆系统',
  register(api: {
    registerTool: (tool: {
      name: string;
      description: string;
      parameters: typeof GraphMemoryToolSchema;
      execute: (id: string, params: Record<string, unknown>) => Promise<{
        content: Array<{ type: 'text'; text: string }>;
      }>;
    }) => void;
  }): void {
    const tool = createGraphMemoryTool();
    api.registerTool(tool);
  }
};