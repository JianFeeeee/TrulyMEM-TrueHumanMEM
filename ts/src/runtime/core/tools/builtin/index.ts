import type { Tool } from 'waterflow/runtime/core/tools/tool_interface';
import type { Platform } from 'waterflow/platform/types';
import { GraphMemoryTool, createGraphMemoryTool } from './graph_memory_tool';

export { GraphMemoryTool, createGraphMemoryTool };

export function registerGraphMemoryTool(
  registry: { register: (tool: Tool) => void },
  sessionId?: string
): void {
  registry.register(createGraphMemoryTool(sessionId));
}

export async function installTrulyMEM(platform: Platform, sessionId?: string) {
  const { initializeToolRegistry } = await import('waterflow/runtime/core/tools/builtin');
  const registry = initializeToolRegistry(platform);
  registerGraphMemoryTool(registry, sessionId);
  return registry;
}
