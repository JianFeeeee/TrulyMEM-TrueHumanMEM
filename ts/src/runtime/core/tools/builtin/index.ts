import type { Tool } from 'waterflow-ts/dist/runtime/core/tools/tool_interface.js';
import type { Platform } from 'waterflow-ts/dist/platform/types.js';
import type { ToolRegistry } from 'waterflow-ts/dist/runtime/core/tools/tool_registry.js';
import { GraphMemoryTool, createGraphMemoryTool, mapToolIdToApiName, mapApiNameToToolId } from './graph_memory_tool';

export { GraphMemoryTool, createGraphMemoryTool, mapToolIdToApiName, mapApiNameToToolId };

export function registerGraphMemoryTool(
  registry: { register: (tool: Tool) => void },
  sessionId?: string
): void {
  registry.register(createGraphMemoryTool(sessionId));
}

export async function installTrulyMEM(platform: Platform, sessionId?: string): Promise<ToolRegistry> {
  const { initializeToolRegistry } = await import('waterflow-ts/dist/runtime/core/tools/builtin/index.js');
  const registry = initializeToolRegistry(platform);
  registerGraphMemoryTool(registry, sessionId);
  return registry;
}
