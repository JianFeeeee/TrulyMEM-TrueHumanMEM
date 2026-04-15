export type ToolCategory = 'file' | 'code' | 'search' | 'execute' | 'network' | 'analysis' | 'generation' | 'communication' | 'mcp' | 'custom';

export type PermissionLevel = 'safe' | 'moderate' | 'dangerous' | 'restricted';

export type SchemaType = 'string' | 'number' | 'integer' | 'boolean' | 'array' | 'object';

export interface SchemaProperty {
  type: SchemaType;
  description: string;
  enum?: string[];
  minimum?: number;
  maximum?: number;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  default?: unknown;
  examples?: unknown[];
  items?: SchemaProperty;
  properties?: Record<string, SchemaProperty>;
}

export interface ToolInputSchema {
  type: 'object';
  properties: Record<string, SchemaProperty>;
  required?: string[];
  additionalProperties?: boolean;
}

export interface ToolOutputSchema {
  type: 'object';
  properties: Record<string, SchemaProperty>;
  format?: 'json' | 'text' | 'markdown' | 'binary';
  maxSize?: number;
  maxLines?: number;
}

export type ToolInput = Record<string, unknown>;
export type ToolOutput = string | Record<string, unknown> | void;

export interface ToolExecutionContext {
  toolCallId: string;
  workingDirectory: string;
  abortController: { signal: AbortSignal };
  config: { timeout?: number };
  logger: { info: (...args: unknown[]) => void; warn: (...args: unknown[]) => void; error: (...args: unknown[]) => void; debug: (...args: unknown[]) => void };
}

export type ToolHandler = (params: ToolInput, context: ToolExecutionContext) => Promise<ToolOutput>;

export interface Tool {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly category: ToolCategory;
  readonly inputSchema: ToolInputSchema;
  readonly outputSchema?: ToolOutputSchema;
  readonly handler: ToolHandler;
  readonly permissionLevel: PermissionLevel;
}
