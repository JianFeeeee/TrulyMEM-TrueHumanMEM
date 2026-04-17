declare module 'waterflow/platform' {
  import type { Platform, CreatePlatformOptions, PlatformCapabilities } from 'waterflow-ts/platform/types';
  export function getPlatform(): Platform;
  export function hasCapability(capability: keyof PlatformCapabilities): boolean;
  export function initPlatform(options?: CreatePlatformOptions): Platform;
  export function resetPlatform(): void;
}

declare module 'waterflow/platform/types' {
  export type BufferSource = ArrayBuffer | ArrayBufferView;
  export type RuntimeType = 'node' | 'web' | 'harmony' | 'unknown';
  export type OSType = 'windows' | 'macos' | 'linux' | 'android' | 'ios' | 'harmony' | 'unknown';

  export interface PlatformCapabilities {
    fileSystem: boolean;
    processExecution: boolean;
    network: boolean;
    storage: boolean;
    webSocket: boolean;
    workers: boolean;
  }

  export interface PlatformAbortSignal {
    readonly aborted: boolean;
    readonly reason?: unknown;
    addEventListener(type: 'abort', listener: () => void): void;
    removeEventListener(type: 'abort', listener: () => void): void;
  }

  export interface PlatformAbortController {
    readonly signal: PlatformAbortSignal;
    abort(reason?: unknown): void;
  }

  export interface PlatformTextEncoder {
    encode(input?: string): Uint8Array;
    encodeInto(src: string, dest: Uint8Array): { read: number; written: number };
  }

  export interface PlatformTextDecoder {
    decode(input?: BufferSource): string;
  }

  export interface PlatformURL {
    href: string;
    origin: string;
    protocol: string;
    host: string;
    hostname: string;
    port: string;
    pathname: string;
    search: string;
    hash: string;
    toString(): string;
    toJSON(): string;
  }

  export interface PlatformGlobals {
    TextEncoder: new (encoding?: string) => PlatformTextEncoder;
    TextDecoder: new (encoding?: string) => PlatformTextDecoder;
    URL: new (url: string) => { href: string; pathname: string; toString(): string };
    randomUUID(): string;
    now(): number;
    btoa(data: string): string;
    atob(data: string): string;
  }

  export interface GlobOptions {
    cwd?: string;
    ignore?: string[];
    absolute?: boolean;
    dot?: boolean;
    onlyFiles?: boolean;
    onlyDirectories?: boolean;
    deep?: number;
    ignoreCase?: boolean;
  }

  export interface GlobResult {
    path: string;
    isFile: boolean;
    isDirectory: boolean;
  }

  export interface GlobTool {
    glob(pattern: string, options?: GlobOptions): Promise<string[]>;
    globWithInfo(pattern: string, options?: GlobOptions): Promise<GlobResult[]>;
    isMatch(path: string, pattern: string): boolean;
    search(pattern: string, basePath?: string): Promise<string[]>;
  }

  export interface GrepOptions {
    cwd?: string;
    ignoreCase?: boolean;
    multiline?: boolean;
    glob?: string | string[];
    include?: string[];
    exclude?: string[];
    context?: number;
    beforeContext?: number;
    afterContext?: number;
    headLimit?: number;
  }

  export interface GrepMatch {
    path: string;
    line: number;
    column?: number;
    content: string;
  }

  export interface GrepSearchOptions {
    pattern: string;
    path?: string;
    glob?: string | string[];
    ignoreCase?: boolean;
    context?: number;
    outputMode?: 'content' | 'files_with_matches' | 'count';
    maxResults?: number;
  }

  export interface GrepSearchResult {
    lines: string[];
  }

  export interface GrepTool {
    grep(pattern: string | RegExp, options?: GrepOptions): Promise<GrepMatch[]>;
    grepFiles(pattern: string | RegExp, options?: GrepOptions): Promise<string[]>;
    grepCount(pattern: string | RegExp, options?: GrepOptions): Promise<number>;
    search(options: GrepSearchOptions): Promise<GrepSearchResult>;
  }

  export interface PlatformTools {
    glob: GlobTool | null;
    grep: GrepTool | null;
  }

  export interface FileInfo {
    path: string;
    name: string;
    isFile: boolean;
    isDirectory: boolean;
    size: number;
    modifiedTime?: number;
    createdTime?: number;
  }

  export interface FileReadOptions {
    encoding?: 'utf-8' | 'binary' | 'base64';
    start?: number;
    end?: number;
  }

  export interface FileWriteOptions {
    encoding?: 'utf-8' | 'binary' | 'base64';
    append?: boolean;
    createDir?: boolean;
  }

  export interface FileSystemOperations {
    readFile(path: string, options?: FileReadOptions): Promise<string | ArrayBuffer>;
    writeFile(path: string, data: string | ArrayBuffer, options?: FileWriteOptions): Promise<void>;
    appendFile(path: string, data: string, options?: FileWriteOptions): Promise<void>;
    deleteFile(path: string): Promise<void>;
    exists(path: string): Promise<boolean>;
    stat(path: string): Promise<FileInfo>;
    readdir(path: string): Promise<FileInfo[]>;
    mkdir(path: string, recursive?: boolean): Promise<void>;
    rmdir(path: string, recursive?: boolean): Promise<void>;
    copy(src: string, dest: string): Promise<void>;
    move(src: string, dest: string): Promise<void>;
    watch?(path: string, callback: (event: string, filename: string) => void): () => void;
  }

  export interface ProcessResult {
    exitCode: number;
    stdout: string;
    stderr: string;
    signal?: string;
  }

  export interface ProcessOptions {
    cwd?: string;
    env?: Record<string, string>;
    timeout?: number;
    input?: string;
    shell?: boolean;
    maxBuffer?: number;
  }

  export interface ProcessOperations {
    exec(command: string, options?: ProcessOptions): Promise<ProcessResult>;
    execFile(file: string, args: string[], options?: ProcessOptions): Promise<ProcessResult>;
    spawn?(command: string, args: string[], options?: ProcessOptions): AsyncIterable<string>;
    which?(command: string): Promise<string | null>;
    kill?(pid: number, signal?: string): Promise<boolean>;
  }

  export interface StorageOperations {
    get(key: string): Promise<string | null>;
    set(key: string, value: string, ttl?: number): Promise<void>;
    delete(key: string): Promise<void>;
    clear(): Promise<void>;
    keys(): Promise<string[]>;
  }

  export interface PathOperations {
    join(...paths: string[]): string;
    dirname(path: string): string;
    basename(path: string, ext?: string): string;
    extname(path: string): string;
    normalize(path: string): string;
    isAbsolute(path: string): boolean;
    resolve(...paths: string[]): string;
    relative(from: string, to: string): string;
  }

  export interface PlatformResponse {
    status: number;
    statusText: string;
    headers: Record<string, string>;
    ok: boolean;
    text(): Promise<string>;
    json(): Promise<any>;
    arrayBuffer(): Promise<ArrayBuffer>;
  }

  export interface PlatformFetchRequestInit {
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS';
    headers?: Record<string, string>;
    body?: string | ArrayBuffer | Record<string, string | ArrayBuffer>;
    timeout?: number;
  }

  export interface PlatformWebSocket {
    readonly readyState: number;
    readonly url: string;
    send(data: string | ArrayBuffer): void;
    close(code?: number, reason?: string): void;
    addEventListener(type: string, listener: (event: any) => void): void;
    removeEventListener(type: string, listener: (event: any) => void): void;
  }

  export interface NetworkOperations {
    fetch(url: string, options?: PlatformFetchRequestInit): Promise<PlatformResponse>;
    fetchStream?(url: string, options?: PlatformFetchRequestInit): AsyncGenerator<ArrayBuffer, PlatformResponse, unknown>;
    connectWebSocket?(url: string, protocols?: string[]): Promise<PlatformWebSocket>;
  }

  export interface PlatformInfo {
    runtime: RuntimeType;
    os: OSType;
    version?: string;
    arch?: string;
    hostname?: string;
    capabilities: PlatformCapabilities;
  }

  export interface Tool {
    readonly id: string;
    readonly name: string;
    readonly apiName?: string;
    readonly description: string;
    readonly category: ToolCategory;
    readonly inputSchema: ToolInputSchema;
    readonly outputSchema?: ToolOutputSchema;
    readonly handler: (params: ToolInput, context: ToolExecutionContext) => Promise<ToolOutput>;
    readonly permissionLevel: ToolPermissionLevel;
    readonly requiredPermissions?: string[];
    readonly features?: ToolFeatures;
    readonly metadata?: ToolMetadata;
    readonly isMcp?: boolean;
    readonly shouldDefer?: boolean;
    readonly alwaysLoad?: boolean;
    readonly searchHint?: string;
    prompt?(options: ToolPromptOptions): Promise<string>;
  }

  export interface Platform {
    getInfo(): PlatformInfo;
    createAbortController(): PlatformAbortController;
    readonly path: PathOperations;
    readonly fs: FileSystemOperations | null;
    readonly process: ProcessOperations | null;
    readonly storage: StorageOperations;
    readonly network: NetworkOperations;
    readonly globals: PlatformGlobals;
    readonly tools: PlatformTools;
    readonly builtinTools: Tool[];
    getEnv(key: string): string | undefined;
    getAllEnv?(): Record<string, string>;
    setEnv?(key: string, value: string): void;
    getCwd(): string;
    setCwd?(path: string): void;
    exit?(code: number): void;
  }

  export interface CreatePlatformOptions {
    storagePath?: string;
    storageType?: 'localStorage' | 'indexedDB';
    dbName?: string;
    context?: any;
    storageName?: string;
  }

  export type ToolInput = Record<string, unknown>;
  export type ToolOutput = string | Record<string, unknown> | void;

  export type ToolPermissionLevel = 'safe' | 'moderate' | 'dangerous' | 'restricted';
  export type ToolCategory = 'file' | 'code' | 'search' | 'execute' | 'network' | 'analysis' | 'generation' | 'communication' | 'custom';

  export interface ToolSchemaProperty {
    type: 'string' | 'number' | 'integer' | 'boolean' | 'array' | 'object';
    description: string;
    enum?: string[];
    default?: unknown;
    examples?: unknown[];
    items?: ToolSchemaProperty;
    properties?: Record<string, ToolSchemaProperty>;
  }

  export interface ToolInputSchema {
    type: 'object';
    properties: Record<string, ToolSchemaProperty>;
    required?: string[];
    additionalProperties?: boolean;
  }

  export interface ToolExecutionContext {
    toolCallId: string;
    workingDirectory: string;
    additionalWorkingDirectories?: string[];
    abortController: PlatformAbortController;
    config: {
      timeout?: number;
      maxOutputSize?: number;
      allowedDirectories?: string[];
    };
    logger: {
      info(message: string, ...args: unknown[]): void;
      warn(message: string, ...args: unknown[]): void;
      error(message: string, ...args: unknown[]): void;
      debug(message: string, ...args: unknown[]): void;
    };
  }

  export interface BuiltinTool {
    readonly id: string;
    readonly name: string;
    readonly apiName?: string;
    readonly description: string;
    readonly category: ToolCategory;
    readonly inputSchema: ToolInputSchema;
    readonly permissionLevel: ToolPermissionLevel;
    handler(params: ToolInput, context: ToolExecutionContext): Promise<ToolOutput>;
  }
}

declare module 'waterflow/runtime/core/tools/tool_interface' {
  import type { PlatformAbortController } from 'waterflow-ts/platform/types';
  import type { AgentId } from 'waterflow-ts/shared/types/agent';
  import type { WorkflowRunner } from 'waterflow-ts/runtime/core/workflow/types';
  import type { WorkflowRegistryImpl } from 'waterflow-ts/runtime/core/workflow/workflow_registry';
  import type { AgentRegistryImpl } from 'waterflow-ts/runtime/core/workflow/agent_registry';
  import type { AgentExecutor } from 'waterflow-ts/runtime/core/agent/agent_executor';
  import type { MCPClient } from 'waterflow-ts/runtime/core/tools/mcp/mcp_client';

  export type ToolCategory =
    | 'file'
    | 'code'
    | 'search'
    | 'execute'
    | 'network'
    | 'analysis'
    | 'generation'
    | 'communication'
    | 'mcp'
    | 'custom';

  export type PermissionLevel =
    | 'safe'
    | 'moderate'
    | 'dangerous'
    | 'restricted';

  export type SchemaType =
    | 'string'
    | 'number'
    | 'integer'
    | 'boolean'
    | 'array'
    | 'object';

  export interface SchemaProperty {
    type: SchemaType;
    description: string;
    enum?: string[];
    minimum?: number;
    maximum?: number;
    minLength?: number;
    maxLength?: number;
    pattern?: string;
    default?: any;
    examples?: any[];
    suggestedSource?: 'context' | 'literal' | 'file';
    items?: SchemaProperty;
    properties?: Record<string, SchemaProperty>;
    required?: string[];
    additionalProperties?: boolean | SchemaProperty;
  }

  export interface ToolInputSchema {
    type: 'object';
    properties: Record<string, SchemaProperty>;
    required?: string[];
    additionalProperties?: boolean;
    semanticHints?: Record<string, string>;
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

  export interface Logger {
    info(message: string, ...args: any[]): void;
    warn(message: string, ...args: any[]): void;
    error(message: string, ...args: any[]): void;
    debug(message: string, ...args: any[]): void;
  }

  export interface ToolConfig {
    timeout?: number;
    maxOutputSize?: number;
    allowedDirectories?: string[];
  }

  export interface ToolExecutionContext {
    toolCallId: string;
    agentId?: AgentId;
    workingDirectory: string;
    additionalWorkingDirectories?: string[] | undefined;
    abortController: PlatformAbortController;
    config: ToolConfig;
    logger: Logger;
    workflowRunner?: WorkflowRunner | undefined;
    workflowRegistry?: WorkflowRegistryImpl | undefined;
    agentExecutor?: AgentExecutor | undefined;
    agentRegistry?: AgentRegistryImpl | undefined;
    allowedAgentTypes?: string[] | undefined;
    mcpClients?: Map<string, MCPClient> | undefined;
    tools?: Tool[] | undefined;
  }

  export type ToolHandler = (
    params: ToolInput,
    context: ToolExecutionContext
  ) => Promise<ToolOutput>;

  export interface ToolFeatures {
    isAsync?: boolean;
    isStreamable?: boolean;
    isCacheable?: boolean;
    requiresConfirmation?: boolean;
    supportsProgress?: boolean;
    supportsCancellation?: boolean;
    producesFiles?: boolean;
    producesImages?: boolean;
    producesStructuredOutput?: boolean;
    requiresMcp?: boolean;
    requiresNetwork?: boolean;
  }

  export interface ToolExample {
    description: string;
    input: ToolInput;
    output: ToolOutput;
    explanation?: string;
  }

  export interface ToolMetadata {
    source: 'builtin' | 'mcp' | 'plugin' | 'external';
    version?: string;
    author?: string;
    documentationUrl?: string;
    examples?: ToolExample[];
    estimatedDuration?: number;
    estimatedTokens?: number;
    compatibleModels?: string[];
    incompatibleModels?: string[];
  }

  export interface ToolPromptOptions {
    tools: Tool[];
    agentRegistry?: AgentRegistryImpl | undefined;
    workflowRegistry?: WorkflowRegistryImpl | undefined;
    allowedAgentTypes?: string[] | undefined;
  }

  export interface Tool {
    readonly id: string;
    readonly name: string;
    readonly apiName?: string;
    readonly description: string;
    readonly category: ToolCategory;
    readonly inputSchema: ToolInputSchema;
    readonly outputSchema?: ToolOutputSchema;
    readonly handler: ToolHandler;
    readonly permissionLevel: PermissionLevel;
    readonly requiredPermissions?: string[];
    readonly features?: ToolFeatures;
    readonly metadata?: ToolMetadata;
    readonly isMcp?: boolean;
    readonly shouldDefer?: boolean;
    readonly alwaysLoad?: boolean;
    readonly searchHint?: string;
    prompt?(options: ToolPromptOptions): Promise<string>;
  }

  export interface ToolExecutionError {
    type: ToolErrorType;
    message: string;
    code?: string;
    details?: Record<string, unknown>;
  }

  export type ToolErrorType =
    | 'validation_error'
    | 'permission_denied'
    | 'timeout'
    | 'execution_error'
    | 'network_error'
    | 'mcp_error'
    | 'unknown_error';

  export interface ToolExecutionResult {
    success: boolean;
    toolId: string;
    toolCallId: string;
    output: ToolOutput;
    error?: ToolExecutionError;
    metadata: {
      duration: number;
      tokensUsed?: number;
      cached?: boolean;
      retryCount?: number;
    };
  }

  export interface ToolCall {
    id: string;
    toolId: string;
    toolName: string;
    input: ToolInput;
    callerId: AgentId | string;
    callerType: 'agent' | 'workflow' | 'main';
  }

  export function createTextOutput(text: string): ToolOutput;
  export function createJSONOutput(data: Record<string, unknown>): ToolOutput;
  export function createErrorOutput(message: string, code?: string, details?: Record<string, unknown>): ToolOutput;
}

declare module 'waterflow/runtime/core/tools/builtin' {
  import type { Platform } from 'waterflow-ts/platform/types';
  import type { Tool } from 'waterflow-ts/runtime/core/tools/tool_interface';
  import { ToolRegistry } from 'waterflow-ts/runtime/core/tools/tool_registry';

  export const FRAMEWORK_TOOLS: Tool[];
  export function initializeToolRegistry(platform: Platform): ToolRegistry;
  export function getFrameworkTools(): Tool[];
}

declare module 'waterflow/runtime/core/tools/tool_registry' {
  import type { Tool, ToolCategory, ToolInput } from 'waterflow-ts/runtime/core/tools/tool_interface';

  export interface ValidationResult {
    valid: boolean;
    errors?: string[];
  }

  export interface ToolSearchResult {
    tool: Tool;
    relevanceScore: number;
    matchReason: string;
  }

  export interface SearchOptions {
    category?: ToolCategory;
    permissionLevel?: string;
    limit?: number;
  }

  export interface RegistryStatistics {
    totalTools: number;
    byCategory: Record<string, number>;
    bySource: Record<string, number>;
    byPermissionLevel: Record<string, number>;
  }

  export interface ToolDefinitionExtended {
    id: string;
    name: string;
    description: string;
    parameters: {
      type: 'object';
      properties: Record<string, any>;
      required?: string[];
      additionalProperties?: boolean;
    };
    execute: (params: Record<string, any>) => Promise<any>;
  }

  export class ToolRegistry {
    register(tool: Tool | ToolDefinitionExtended): void;
    registerAll(tools: (Tool | ToolDefinitionExtended)[]): void;
    unregister(toolId: string): void;
    get(toolId: string): Tool | ToolDefinitionExtended | undefined;
    getByName(name: string): Tool | ToolDefinitionExtended | undefined;
    has(toolId: string): boolean;
    size(): number;
    listAll(): (Tool | ToolDefinitionExtended)[];
    listByCategory(category: ToolCategory): (Tool | ToolDefinitionExtended)[];
    listByPermissionLevel(level: string): (Tool | ToolDefinitionExtended)[];
    search(query: string, options?: SearchOptions): ToolSearchResult[];
    isAvailable(toolId: string, context?: any): boolean;
    validateInput(toolId: string, input: ToolInput): ValidationResult;
    clear(): void;
    getStatistics(): RegistryStatistics;
  }
}
