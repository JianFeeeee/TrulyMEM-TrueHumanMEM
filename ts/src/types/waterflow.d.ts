declare module 'waterflow/platform' {
  import type { Platform } from 'waterflow/platform/types';
  export function getPlatform(): Platform;
  export function hasCapability(capability: string): boolean;
  export function initPlatform(options?: any): Platform;
  export function resetPlatform(): void;
}

declare module 'waterflow/platform/types' {
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

  export interface PathOperations {
    join(...paths: string[]): string;
    dirname(p: string): string;
    basename(p: string, ext?: string): string;
    extname(p: string): string;
    normalize(p: string): string;
    isAbsolute(p: string): boolean;
    resolve(...paths: string[]): string;
    relative(from: string, to: string): string;
  }

  export interface FileReadOptions {
    encoding?: 'utf-8' | 'binary';
    start?: number;
    end?: number;
  }

  export interface FileWriteOptions {
    encoding?: 'utf-8' | 'binary';
    append?: boolean;
  }

  export interface FileInfo {
    path: string;
    name: string;
    isFile: boolean;
    isDirectory: boolean;
    size: number;
    modifiedTime: number;
    createdTime: number;
  }

  export interface FileSystemOperations {
    readFile(filePath: string, options?: FileReadOptions): Promise<string | ArrayBuffer>;
    writeFile(filePath: string, data: string | ArrayBuffer, options?: FileWriteOptions): Promise<void>;
    appendFile(filePath: string, data: string, options?: FileWriteOptions): Promise<void>;
    deleteFile(filePath: string): Promise<void>;
    exists(filePath: string): Promise<boolean>;
    stat(filePath: string): Promise<FileInfo>;
    readdir(dirPath: string): Promise<FileInfo[]>;
    mkdir(dirPath: string, recursive?: boolean): Promise<void>;
    rmdir(dirPath: string, recursive?: boolean): Promise<void>;
    copy(src: string, dest: string): Promise<void>;
    move(src: string, dest: string): Promise<void>;
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
    maxBuffer?: number;
  }

  export interface ProcessOperations {
    exec(command: string, options?: ProcessOptions): Promise<ProcessResult>;
    execFile(file: string, args: string[], options?: ProcessOptions): Promise<ProcessResult>;
  }

  export interface StorageOperations {
    get(key: string): Promise<string | null>;
    set(key: string, value: string, ttl?: number): Promise<void>;
    delete(key: string): Promise<void>;
    clear(): Promise<void>;
    keys(): Promise<string[]>;
  }

  export interface PlatformGlobals {
    TextEncoder: typeof TextEncoder;
    TextDecoder: typeof TextDecoder;
    URL: typeof URL;
    randomUUID(): string;
    now(): number;
    btoa(data: string): string;
    atob(data: string): string;
  }

  export interface Logger {
    info(msg: string, ...args: unknown[]): void;
    warn(msg: string, ...args: unknown[]): void;
    error(msg: string, ...args: unknown[]): void;
    debug(msg: string, ...args: unknown[]): void;
  }

  export interface Platform {
    readonly path: PathOperations;
    readonly fs: FileSystemOperations;
    readonly process: ProcessOperations;
    readonly storage: StorageOperations;
    readonly globals: PlatformGlobals;
    getInfo(): { runtime: string; os: string; version: string; arch: string; hostname: string };
    createAbortController(): PlatformAbortController;
    getEnv(key: string): string | undefined;
    getAllEnv(): Record<string, string>;
    setEnv(key: string, value: string): void;
    getCwd(): string;
    setCwd(p: string): void;
    exit(code: number): void;
    getLogger(): Logger;
  }
}

declare module 'waterflow/runtime/core/tools/tool_interface' {
  import type { PlatformAbortController, Logger } from 'waterflow/platform/types';

  export type ToolCategory = 'file' | 'code' | 'search' | 'execute' | 'network' | 'analysis' | 'generation' | 'communication' | 'mcp' | 'custom';
  export type PermissionLevel = 'safe' | 'moderate' | 'dangerous' | 'restricted';
  export type ToolInput = Record<string, unknown>;
  export type ToolOutput = string | Record<string, unknown> | void;

  export interface SchemaProperty {
    type: string;
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

  export interface ToolExecutionContext {
    toolCallId: string;
    workingDirectory: string;
    abortController: PlatformAbortController;
    config: { timeout?: number };
    logger: Logger;
  }

  export interface Tool {
    readonly id: string;
    readonly name: string;
    readonly description: string;
    readonly category: ToolCategory;
    readonly inputSchema: ToolInputSchema;
    readonly outputSchema?: ToolOutputSchema;
    readonly handler: (params: ToolInput, context: ToolExecutionContext) => Promise<ToolOutput>;
    readonly permissionLevel: PermissionLevel;
    readonly alwaysLoad?: boolean;
    readonly shouldDefer?: boolean;
    readonly isMcp?: boolean;
    readonly prompt?: (options: any) => Promise<string>;
    readonly features?: string[];
    readonly metadata?: Record<string, unknown>;
    readonly searchHint?: string;
  }
}
