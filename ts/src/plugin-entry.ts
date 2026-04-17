import { GraphMemoryToolSchema, createGraphMemoryTool } from './runtime/core/tools/builtin/graph_memory_tool.js';

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
  const tool = createGraphMemoryTool();
  api.registerTool(tool);
}