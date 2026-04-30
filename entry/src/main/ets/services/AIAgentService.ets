/**
 * AIAgentService - AI Agent 服务层
 * 管理上下文感知的 AI 对话，注入图数据作为上下文，
 * 解析 AI 返回中的记忆操作，调用 GraphMemoryService 执行
 * 参考：main 分支 core/graph_client.py
 */
import http from '@ohos.net.http';
import dataPreferences from '@ohos.data.preferences';
import { Context } from '@ohos.app.ability.UIAbility';
import { GraphMemoryService, EntityInfo, RelationInfo, TaskInfo, MemoryRecallParams, MemoryCommitParams, MemoryPurgeParams, TimeRangeParams, PurgeCriteriaParams, NewRelationParams, PersonaUpdateParams, TaskCreateParams, TaskSetStateParams, TaskDeleteParams, TaskLinkInfoParams, TaskArchiveParams, TaskQueryParams, TripletInput, PersonaQueryResult, TaskQueryResult, MemoryRecallResult } from './GraphMemoryService';

export interface ChatMessage {
    role: string;
    content: string;
}

export interface AgentResponse {
    content: string;
    toolCalls: ToolCallResult[];
}

export interface ToolCallResult {
    name: string;
    success: boolean;
    message: string;
}

// ========= 工具定义类型 =========

// Concrete interface for tool property definitions (replaces Record<string, T>)
interface ToolPropertiesDefinition {
    days?: ToolParamProperty;
    queryIntent?: ToolParamProperty;
    seedEntities?: ToolParamProperty;
    depth?: ToolParamProperty;
    timeRange?: ToolParamProperty;
    sessionFilter?: ToolParamProperty;
    triplets?: ToolParamProperty;
    entityTypes?: ToolParamProperty;
    sessionId?: ToolParamProperty;
    turnId?: ToolParamProperty;
    criteria?: ToolParamProperty;
    mode?: ToolParamProperty;
    newRelation?: ToolParamProperty;
    tone?: ToolParamProperty;
    style?: ToolParamProperty;
    personality?: ToolParamProperty;
    catchphrase?: ToolParamProperty;
    background?: ToolParamProperty;
    taskId?: ToolParamProperty;
    description?: ToolParamProperty;
    infoNodes?: ToolParamProperty;
    state?: ToolParamProperty;
    deleteInfoNodes?: ToolParamProperty;
    infoNodeNames?: ToolParamProperty;
    summary?: ToolParamProperty;
    limit?: ToolParamProperty;
    stateFilter?: ToolParamProperty;
    subject?: ToolParamProperty;
    relation?: ToolParamProperty;
    object?: ToolParamProperty;
    confidence?: ToolParamProperty;
    subjectContains?: ToolParamProperty;
    relationType?: ToolParamProperty;
    targetContains?: ToolParamProperty;
    target?: ToolParamProperty;
}

interface ToolParamProperty {
    type: string;
    description: string;
    items?: ToolParamProperty;
    properties?: ToolPropertiesDefinition;
    required?: string[];
    enum?: string[];
}

interface ToolParamDecl {
    type: string;
    properties: ToolPropertiesDefinition;
    required?: string[];
}

interface ToolFunctionDecl {
    name: string;
    description: string;
    parameters: ToolParamDecl;
}

interface ToolFunctionDef {
    type: string;
    function: ToolFunctionDecl;
}

// ========= API 请求/响应结构 =========

interface ApiRequestMessage {
    role: string;
    content: string;
}

interface ApiRequest {
    model: string;
    messages: ApiRequestMessage[];
    tools?: ToolFunctionDef[];
    tool_choice?: string;
}

interface ApiToolCall {
    id: string;
    type: string;
    function: ToolFunctionCall;
}

interface ToolFunctionCall {
    name: string;
    arguments: string;
}

interface ApiChoiceMessage {
    content?: string;
    tool_calls?: ApiToolCall[];
}

interface ApiChoice {
    message: ApiChoiceMessage;
}

interface ApiResponse {
    choices: ApiChoice[];
}

// ========= 内部结果类型 =========

interface ExecuteToolResult {
    name: string;
    success: boolean;
    message: string;
}





interface BuildContextBlockParams {
    persona: Record<string, string>;
    found: boolean;
    entities: EntityInfo[];
    relations: RelationInfo[];
    message: string;
}

// ========= 服务方法参数类型 =========



// ========= 工具定义辅助函数 =========

function makeStringProp(description: string): ToolParamProperty {
    const result: ToolParamProperty = { type: 'string', description: description };
    return result;
}

function makeIntegerProp(description: string): ToolParamProperty {
    const result: ToolParamProperty = { type: 'integer', description: description };
    return result;
}

function makeObjectProp(description: string, props: ToolPropertiesDefinition, required?: string[]): ToolParamProperty {
    const param: ToolParamProperty = { type: 'object', description: description };
    param.properties = props;
    if (required && required.length > 0) {
        param.required = required;
    }
    return param;
}

function makeArrayProp(description: string, item: ToolParamProperty): ToolParamProperty {
    const result: ToolParamProperty = { type: 'array', description: description, items: item };
    return result;
}

function makeBoolProp(description: string): ToolParamProperty {
    const result: ToolParamProperty = { type: 'boolean', description: description };
    return result;
}

function makeNumberProp(description: string): ToolParamProperty {
    const result: ToolParamProperty = { type: 'number', description: description };
    return result;
}

function makeEnumProp(description: string, enumValues: string[]): ToolParamProperty {
    const result: ToolParamProperty = { type: 'string', description: description, enum: enumValues };
    return result;
}

function makeToolDef(name: string, description: string, properties: ToolPropertiesDefinition, required?: string[]): ToolFunctionDef {
    const params: ToolParamDecl = { type: 'object', properties: properties };
    const func: ToolFunctionDecl = { name: name, description: description, parameters: params };
    const tool: ToolFunctionDef = { type: 'function', function: func };
    if (required && required.length > 0) {
        tool.function.parameters.required = required;
    }
    return tool;
}

/**
 * 系统提示词 — AI 人设 + 图记忆使用说明
 */
function buildSystemPrompt(personaContext: string): string {
    return `你是 TrulyMEM（True Memory）——一个拥有真实记忆的 AI 助手。

## 核心身份
${personaContext || '你是一个帮助用户记录和回忆信息的助手。你的核心能力是基于图数据库的记忆系统。'}

## 记忆系统
你的记忆存储在图数据库中，每个记忆都是「实体 - 关系 - 实体」的三元组形式。
每轮对话开始，你都会按以下顺序操作：

### 步骤1：查询人设
使用 memory_recall 查询当前人设，确保回复风格一致。

### 步骤2：查询工作记忆链
使用 memory_recall 查询任务链，了解会话上下文和进展中的任务。

### 步骤3：处理用户请求

### 步骤4：更新工作记忆链

## 可用工具
- memory_recall(queryIntent, seedEntities?, depth?, timeRange?, sessionFilter?): 检索记忆
- memory_commit(triplets, entityTypes?, sessionId?, turnId?): 写入记忆
- memory_purge(criteria, mode, newRelation?): 删除/修正记忆
- memory_introspect(sessionId?): 查看记忆状态统计
- memory_archive(days?): 归档旧记忆
- memory_cleanup(dryRun?): 清理已删除数据
- memory_query_archived(days?, keyword?): 查询已归档记忆
- context_rewrite(summary): 压缩工具调用上下文
- persona_update(tone?, style?, personality?, catchphrase?, background?): 更新人设
- persona_remove(attribute): 删除单条人设属性
- persona_clear(): 清除人设
- task_create(taskId, description, infoNodes?): 创建任务
- task_set_state(taskId, state): 设置任务状态
- task_delete(taskId, deleteInfoNodes?): 删除任务
- task_link_info(taskId, infoNodeNames): 关联信息节点
- task_archive(taskId, summary?): 归档任务
- task_query(limit?, stateFilter?): 查询任务列表

## 工具调用规则
1. 每轮对话必须按顺序执行：步骤1查询人设 → 步骤2查询工作记忆链 → 步骤3处理请求
2. context_rewrite 必须单独调用，不能和其他工具在同一轮一起调！
3. 工具调用 ≥5 次后应使用 context_rewrite 压缩上下文

## 写入规则
用户明确表达以下信息时必须写入记忆：
- 偏好、兴趣
- 个人信息（工作、项目、学习）
- 计划安排
- 当前状态
- 结论性事实

推理得到的信息可以写入但需标注 [推测]。`;
}

// ========= 工具定义 =========

// Pre-typed property dictionaries for tool definitions
const recallTimeRangeDict: ToolPropertiesDefinition = { days: makeIntegerProp('最近N天') };
const tripletPropsDict: ToolPropertiesDefinition = {
    subject: makeStringProp('主体'),
    relation: makeStringProp('关系'),
    object: makeStringProp('客体'),
    confidence: makeNumberProp('置信度')
};
const purgeCriteriaDict: ToolPropertiesDefinition = {
    subjectContains: makeStringProp(''),
    relationType: makeStringProp(''),
    targetContains: makeStringProp(''),
    sessionId: makeStringProp('')
};
const newRelDict: ToolPropertiesDefinition = {
    relation: makeStringProp(''),
    target: makeStringProp('')
};
const EMPTY_PROPS: ToolPropertiesDefinition = {};

const recallProps: ToolPropertiesDefinition = {
    queryIntent: makeStringProp('查询意图，支持逗号分隔多个关键词'),
    seedEntities: makeArrayProp('种子实体（可选）', makeStringProp('')),
    depth: makeIntegerProp('搜索深度，默认2'),
    timeRange: makeObjectProp('时间范围（可选）', recallTimeRangeDict),
    sessionFilter: makeStringProp('会话ID过滤（可选）')
};
const commitProps: ToolPropertiesDefinition = {
    triplets: makeArrayProp('三元组列表', makeObjectProp('', tripletPropsDict, ['subject', 'relation', 'object'])),
    entityTypes: makeObjectProp('实体类型映射（可选）', EMPTY_PROPS),
    sessionId: makeStringProp('会话ID（可选）'),
    turnId: makeIntegerProp('轮次ID（可选）')
};
const purgeProps: ToolPropertiesDefinition = {
    criteria: makeObjectProp('删除条件', purgeCriteriaDict),
    mode: makeEnumProp('删除模式：soft逻辑删除, hard物理删除, supersede纠错替代', ['soft', 'hard', 'supersede']),
    newRelation: makeObjectProp('替代关系（supersede模式用）', newRelDict)
};
const personaProps: ToolPropertiesDefinition = {
    tone: makeStringProp('语气'),
    style: makeStringProp('风格'),
    personality: makeStringProp('性格'),
    catchphrase: makeStringProp('口头禅'),
    background: makeStringProp('背景')
};
const createProps: ToolPropertiesDefinition = {
    taskId: makeStringProp('任务ID'),
    description: makeStringProp('任务描述'),
    infoNodes: makeArrayProp('关联的信息节点名称列表', makeStringProp(''))
};
const setStateProps: ToolPropertiesDefinition = {
    taskId: makeStringProp('任务ID'),
    state: makeEnumProp('任务状态', ['进行中', '已完成', '已暂停', '已取消'])
};
const deleteProps: ToolPropertiesDefinition = {
    taskId: makeStringProp('任务ID'),
    deleteInfoNodes: makeBoolProp('是否删除关联的信息节点')
};
const linkInfoProps: ToolPropertiesDefinition = {
    taskId: makeStringProp('任务ID'),
    infoNodeNames: makeArrayProp('信息节点名称列表', makeStringProp(''))
};
const archiveProps: ToolPropertiesDefinition = {
    taskId: makeStringProp('任务ID'),
    summary: makeStringProp('归档摘要')
};
const queryProps: ToolPropertiesDefinition = {
    limit: makeIntegerProp('返回数量，默认10'),
    stateFilter: makeStringProp('状态过滤: 进行中/已完成/已暂停/已取消/archived')
};
const introspectProps: ToolPropertiesDefinition = {
    sessionId: makeStringProp('会话ID（可选）')
};
const archiveProps2: ToolPropertiesDefinition = {
    days: makeIntegerProp('归档天数，默认30')
};
const cleanupProps: ToolPropertiesDefinition = {
    dryRun: makeBoolProp('仅预览不删除')
};
const queryArchivedProps: ToolPropertiesDefinition = {
    days: makeIntegerProp('最近N天内的归档记录'),
    keyword: makeStringProp('关键词过滤')
};
const contextRewriteProps: ToolPropertiesDefinition = {
    summary: makeStringProp('压缩后的摘要文本，必须包含工具调用元信息')
};
const personaRemoveProps: ToolPropertiesDefinition = {
    attribute: makeStringProp('要删除的属性名（如：扮演角色、说话风格）')
};

const TOOLS_DEFINITION: ToolFunctionDef[] = [
    makeToolDef('memory_recall', '检索记忆。支持关键词、种子实体、深度扩展。返回相关实体和关系。', recallProps, ['queryIntent']),
    makeToolDef('memory_commit', '写入记忆。将三元组写入图数据库。', commitProps, ['triplets']),
    makeToolDef('memory_purge', '删除或修正记忆。支持条件删除和纠错替代。', purgeProps, ['criteria', 'mode']),
    makeToolDef('memory_introspect', '查看记忆状态。返回实体数量、关系数量、热点实体。', introspectProps),
    makeToolDef('memory_archive', '归档旧记忆。将N天前的非活跃关系标记为归档状态。', archiveProps2, ['days']),
    makeToolDef('memory_cleanup', '清理无效数据。物理删除已删除状态超过90天的关系和孤立节点。', cleanupProps),
    makeToolDef('memory_query_archived', '查询已归档的记忆。返回所有 status=archived 的关系记录。', queryArchivedProps),
    makeToolDef('context_rewrite', '压缩本轮对话的工具调用上下文。将冗长的JSON工具结果提炼为简洁摘要。', contextRewriteProps, ['summary']),
    makeToolDef('persona_update', '更新AI人设属性（语气、风格、性格等）。', personaProps),
    makeToolDef('persona_remove', '删除单条人设属性。保留其他人设不变。', personaRemoveProps, ['attribute']),
    makeToolDef('persona_clear', '清除所有人设信息。', EMPTY_PROPS),
    makeToolDef('task_create', '创建新的工作记忆任务节点。', createProps, ['taskId', 'description']),
    makeToolDef('task_set_state', '设置任务状态。', setStateProps, ['taskId', 'state']),
    makeToolDef('task_delete', '删除任务节点。', deleteProps, ['taskId']),
    makeToolDef('task_link_info', '关联信息节点到任务。', linkInfoProps, ['taskId', 'infoNodeNames']),
    makeToolDef('task_archive', '归档任务。将任务设为已暂停，写入归档摘要。', archiveProps, ['taskId']),
    makeToolDef('task_query', '查询最近的任务列表。', queryProps)
];

// ========= 工具名称映射 =========

// Types for executeTool generic args





type ToolStateArg = '进行中' | '已完成' | '已暂停' | '已取消';

type ToolHandlerName =
    | 'memoryRecal'
    | 'memoryCommit'
    | 'memoryPurge'
    | 'memoryIntrospect'
    | 'memoryArchive'
    | 'memoryCleanup'
    | 'memoryQueryArchived'
    | 'contextRewrite'
    | 'personaUpdate'
    | 'personaRemove'
    | 'personaClear'
    | 'taskCreate'
    | 'taskSetState'
    | 'taskDelete'
    | 'taskLinkInfo'
    | 'taskArchive'
    | 'taskQuery';

const TOOL_HANDLER_MAP: Record<string, ToolHandlerName> = {
    'memory_recall': 'memoryRecal',
    'memory_commit': 'memoryCommit',
    'memory_purge': 'memoryPurge',
    'memory_introspect': 'memoryIntrospect',
    'memory_archive': 'memoryArchive',
    'memory_cleanup': 'memoryCleanup',
    'memory_query_archived': 'memoryQueryArchived',
    'context_rewrite': 'contextRewrite',
    'persona_update': 'personaUpdate',
    'persona_remove': 'personaRemove',
    'persona_clear': 'personaClear',
    'task_create': 'taskCreate',
    'task_set_state': 'taskSetState',
    'task_delete': 'taskDelete',
    'task_link_info': 'taskLinkInfo',
    'task_archive': 'taskArchive',
    'task_query': 'taskQuery',
};

// ========= AIAgentService =========

export class AIAgentService {
    private memoryService: GraphMemoryService;
    private currentSessionId: string;
    private turnCounter: number = 0;

    private appContext: Context;

    constructor(memoryService: GraphMemoryService, appContext: Context, sessionId?: string) {
        this.memoryService = memoryService;
        this.appContext = appContext;
        this.currentSessionId = sessionId || `session-hm-${Date.now()}`;
    }

    getSessionId(): string {
        return this.currentSessionId;
    }

    /**
     * 发送消息 — 完整的 Agent 流程
     * 1. 查询人设
     * 2. 查询工作记忆链
     * 3. 注入上下文后请求 AI
     * 4. 处理 tool_calls
     * 5. 返回最终回复
     */
    async sendMessage(userInput: string): Promise<AgentResponse> {
        this.turnCounter++;

        // === 步骤1+2: 获取上下文 ===
        const personaResult = await this.memoryService.personaQuery();
        const personaContext: string = personaResult.found ? this.formatPersona(personaResult.persona) : '';

        const recallParams: MemoryRecallParams = {
            queryIntent: 'TaskNode,工作记忆,任务链',
            depth: 2
        };
        const taskResult = await this.memoryService.memoryRecall(recallParams);

        // === 读取 API 配置 ===
        const context = this.appContext;
        const pref = await dataPreferences.getPreferences(context, 'trulymem_config');
        const baseUrl: string = String(await pref.get('base_url', 'https://api.deepseek.com'));
        const model: string = String(await pref.get('model', 'deepseek-chat'));
        const apiKey: string = String(await pref.get('api_key', ''));
        if (!apiKey) {
            const noKeyResponse: AgentResponse = {
                content: '⚠️ API Key 未配置，请先在设置页填写 API Key。',
                toolCalls: []
            };
            return noKeyResponse;
        }

        // === 构建上下文丰富的消息 ===
        const systemPrompt: string = buildSystemPrompt(personaContext);
        const contextBlock: string = this.buildContextBlock(personaResult, taskResult);
        const sysMsg: ApiRequestMessage = { role: 'system' as string, content: systemPrompt };
        const userMsg: ApiRequestMessage = { role: 'user' as string, content: contextBlock + '\n\n---\n\n用户消息: ' + userInput };
        const messages: ApiRequestMessage[] = [sysMsg, userMsg];

        // === 步骤3: 请求 AI ===
        const response: ApiResponse = await this.callApi(messages, baseUrl, model, apiKey);

        const toolCalls: ToolCallResult[] = [];

        // === 步骤4: 处理 tool_calls ===
        if (response.choices && response.choices.length > 0) {
            const choice: ApiChoice = response.choices[0];
            const aiMessage: ApiChoiceMessage = choice.message;

            // 处理函数调用
            if (aiMessage.tool_calls && aiMessage.tool_calls.length > 0) {
                for (const tc of aiMessage.tool_calls) {
                    const handlerName: ToolHandlerName | undefined = TOOL_HANDLER_MAP[tc.function.name];
                    if (handlerName) {
                        const args: Record<string, Object> = JSON.parse(tc.function.arguments);
                        const result: ToolCallResult = await this.executeTool(handlerName, args);
                        toolCalls.push(result);
                    } else {
                        const unknownToolResult: ToolCallResult = {
                            name: tc.function.name,
                            success: false,
                            message: '未知工具'
                        };
                        toolCalls.push(unknownToolResult);
                    }
                }

                // 有 tool_calls 时需要再次请求 AI，带上工具执行结果
                const followUpSystemMsg: ApiRequestMessage = { role: 'system', content: systemPrompt };
                const followUpUserMsg: ApiRequestMessage = { role: 'user', content: contextBlock + '\n\n---\n\n用户消息: ' + userInput };
                const followUpAssistantMsg: ApiRequestMessage = {
                    role: 'assistant',
                    content: aiMessage.content || '（已执行记忆操作）',
                };
                const toolResultsMessages: ApiRequestMessage[] = [
                    followUpSystemMsg,
                    followUpUserMsg,
                    followUpAssistantMsg,
                ];

                for (const tc of aiMessage.tool_calls) {
                    const callResult: ToolCallResult | undefined = toolCalls.find(r => r.name === tc.function.name);
                    const toolResultMsg: string = callResult ? callResult.message : '完成';
                    const toolResultMessage: ApiRequestMessage = {
                        role: 'tool',
                        content: `工具 ${tc.function.name} 执行结果: ${toolResultMsg}`
                    };
                    toolResultsMessages.push(toolResultMessage);
                }

                const finalResponse: ApiResponse = await this.callApi(toolResultsMessages, baseUrl, model, apiKey);
                if (finalResponse.choices && finalResponse.choices.length > 0) {
                    const content: string = finalResponse.choices[0].message.content || '';
                    const finalResult: AgentResponse = { content, toolCalls };
                    return finalResult;
                }
            }

            // 普通回复（无 tool_calls）
            const content: string = aiMessage.content || '';
            const noToolResponse: AgentResponse = { content, toolCalls };
            return noToolResponse;
        }

        const noResponse: AgentResponse = {
            content: 'AI 无响应',
            toolCalls
        };
        return noResponse;
    }

    /**
     * 请求 DeepSeek API
     */
    private async callApi(
        messages: ApiRequestMessage[],
        baseUrl: string,
        model: string,
        apiKey: string
    ): Promise<ApiResponse> {
        const httpRequest = http.createHttp();
        try {
            const resp = await httpRequest.request(baseUrl + '/chat/completions', {
                method: http.RequestMethod.POST,
                header: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + apiKey
                },
                extraData: {
                    model: model,
                    messages: messages,
                    tools: TOOLS_DEFINITION,
                    tool_choice: 'auto'
                },
                expectDataType: http.HttpDataType.OBJECT,
                readTimeout: 60000
            });
            if (resp.responseCode === 200) {
                return resp.result as ApiResponse;
            }
            const errorMsg: string = `API 请求失败: HTTP ${resp.responseCode}`;
            throw new Error(errorMsg);
        } finally {
            httpRequest.destroy();
        }
    }

    /**
     * 执行工具调用
     */
    private async executeTool(name: ToolHandlerName, args: Record<string, Object>): Promise<ToolCallResult> {
        try {
            switch (name) {
                case 'memoryRecal': {
                    const recallArgs: MemoryRecallParams = {
                        queryIntent: args.queryIntent as string,
                        seedEntities: args.seedEntities as string[],
                        depth: (args.depth as number) ?? 2,
                        timeRange: args.timeRange as TimeRangeParams,
                        sessionFilter: args.sessionFilter as string
                    };
                    const recallResult = await this.memoryService.memoryRecall(recallArgs);
                    const result: ToolCallResult = {
                        name: 'memory_recall',
                        success: true,
                        message: `找到 ${recallResult.entities.length} 个实体, ${recallResult.relations.length} 条关系`
                    };
                    return result;
                }

                case 'memoryCommit': {
                    const commitParams: MemoryCommitParams = {
                        triplets: args.triplets as TripletInput[],
                        entityTypes: args.entityTypes as Record<string, string>,
                        sessionId: (args.sessionId as string) || this.currentSessionId,
                        turnId: (args.turnId as number) || this.turnCounter
                    };
                    const commitResult = await this.memoryService.memoryCommit(commitParams);
                    const result: ToolCallResult = {
                        name: 'memory_commit',
                        success: true,
                        message: `已写入 ${commitResult.committedCount} 条记忆`
                    };
                    return result;
                }

                case 'memoryPurge': {
                    const purgeArgs: MemoryPurgeParams = {
                        criteria: args.criteria as PurgeCriteriaParams,
                        mode: args.mode as 'soft' | 'hard' | 'supersede',
                        newRelation: args.newRelation as NewRelationParams
                    };
                    const purgeResult = await this.memoryService.memoryPurge(purgeArgs);
                    const result: ToolCallResult = {
                        name: 'memory_purge',
                        success: true,
                        message: purgeResult.message
                    };
                    return result;
                }

                case 'memoryIntrospect': {
                    const introspectResult = await this.memoryService.memoryIntrospect(args.sessionId as string);
                    const result: ToolCallResult = {
                        name: 'memory_introspect',
                        success: true,
                        message: `实体: ${introspectResult.entityCount}, 关系: ${introspectResult.relationCount}, 热点: ${introspectResult.hotNodes.length}`
                    };
                    return result;
                }

                case 'memoryArchive': {
                    const archiveResult = await this.memoryService.archive(args.days as number);
                    const result: ToolCallResult = {
                        name: 'memory_archive',
                        success: true,
                        message: `已归档 ${archiveResult.archived} 条关系`
                    };
                    return result;
                }

                case 'memoryCleanup': {
                    const cleanupResult = await this.memoryService.cleanup((args.dryRun as boolean) !== false);
                    const result: ToolCallResult = {
                        name: 'memory_cleanup',
                        success: true,
                        message: `清理: ${cleanupResult.cleaned} 条关系, ${cleanupResult.deletedOrphans} 个孤儿节点` + (cleanupResult.dryRun ? ' (预览模式)' : '')
                    };
                    return result;
                }

                case 'memoryQueryArchived': {
                    const qaResult = await this.memoryService.queryArchived(args.days as number, args.keyword as string);
                    const result: ToolCallResult = {
                        name: 'memory_query_archived',
                        success: true,
                        message: `找到 ${qaResult.length} 条归档记录`
                    };
                    return result;
                }

                case 'contextRewrite': {
                    const summary = args.summary as string;
                    const result: ToolCallResult = {
                        name: 'context_rewrite',
                        success: summary.includes('[工具调用总结'),
                        message: summary.includes('[工具调用总结') ? '上下文已压缩' : '格式错误：必须包含[工具调用总结]标记'
                    };
                    return result;
                }

                case 'personaUpdate': {
                    const personaParams: PersonaUpdateParams = {
                        tone: args.tone as string,
                        style: args.style as string,
                        personality: args.personality as string,
                        catchphrase: args.catchphrase as string,
                        background: args.background as string
                    };
                    const puResult = await this.memoryService.personaUpdate(personaParams);
                    const result: ToolCallResult = {
                        name: 'persona_update',
                        success: puResult.success,
                        message: puResult.message
                    };
                    return result;
                }

                case 'personaRemove': {
                    const prResult = await this.memoryService.personaRemove(args.attribute as string);
                    const result: ToolCallResult = {
                        name: 'persona_remove',
                        success: prResult.success,
                        message: prResult.message
                    };
                    return result;
                }

                case 'personaClear': {
                    const pcResult = await this.memoryService.personaClear();
                    const result: ToolCallResult = {
                        name: 'persona_clear',
                        success: pcResult.success,
                        message: pcResult.message
                    };
                    return result;
                }

                case 'taskCreate': {
                    const createParams: TaskCreateParams = {
                        taskId: args.taskId as string,
                        description: args.description as string,
                        infoNodes: args.infoNodes as string[]
                    };
                    const tcResult = await this.memoryService.taskCreate(createParams);
                    const result: ToolCallResult = {
                        name: 'task_create',
                        success: tcResult.success,
                        message: tcResult.message
                    };
                    return result;
                }

                case 'taskSetState': {
                    const setStateParams: TaskSetStateParams = {
                        taskId: args.taskId as string,
                        state: args.state as ToolStateArg
                    };
                    const tsResult = await this.memoryService.taskSetState(setStateParams);
                    const result: ToolCallResult = {
                        name: 'task_set_state',
                        success: tsResult.success,
                        message: tsResult.message
                    };
                    return result;
                }

                case 'taskDelete': {
                    const deleteParams: TaskDeleteParams = {
                        taskId: args.taskId as string,
                        deleteInfoNodes: (args.deleteInfoNodes as boolean) !== false
                    };
                    const tdResult = await this.memoryService.taskDelete(deleteParams);
                    const result: ToolCallResult = {
                        name: 'task_delete',
                        success: tdResult.success,
                        message: tdResult.message
                    };
                    return result;
                }

                case 'taskLinkInfo': {
                    const linkInfoParams: TaskLinkInfoParams = {
                        taskId: args.taskId as string,
                        infoNodeNames: args.infoNodeNames as string[]
                    };
                    const tliResult = await this.memoryService.taskLinkInfo(linkInfoParams);
                    const result: ToolCallResult = {
                        name: 'task_link_info',
                        success: tliResult.success,
                        message: tliResult.message
                    };
                    return result;
                }

                case 'taskArchive': {
                    const archiveParams: TaskArchiveParams = {
                        taskId: args.taskId as string,
                        summary: args.summary as string
                    };
                    const taResult = await this.memoryService.taskArchive(archiveParams);
                    const result: ToolCallResult = {
                        name: 'task_archive',
                        success: taResult.success,
                        message: taResult.message
                    };
                    return result;
                }

                case 'taskQuery': {
                    const tqResult = await this.memoryService.taskQuery({
                        limit: args.limit as number,
                        stateFilter: args.stateFilter as string
                    });
                    const result: ToolCallResult = {
                        name: 'task_query',
                        success: true,
                        message: `找到 ${tqResult.tasks.length} 个任务`
                    };
                    return result;
                }

                default: {
                    const defaultResult: ToolCallResult = {
                        name: name as string,
                        success: false,
                        message: '未实现的工具'
                    };
                    return defaultResult;
                }
            }
        } catch (e) {
            const errorMessage: string = (e as Error).message || '';
            const errorResult: ToolCallResult = {
                name: name as string,
                success: false,
                message: `执行失败: ${errorMessage}`
            };
            return errorResult;
        }
    }

    /**
     * 格式化人设数据为文本
     */
    private formatPersona(persona: Record<string, string>): string {
        const parts: string[] = [];
        const keys: string[] = Object.keys(persona);
        for (let i = 0; i < keys.length; i++) {
            const key: string = keys[i];
            const val: string = persona[key];
            parts.push(`${key}: ${val}`);
        }
        return parts.length > 0 ? parts.join('；') : '';
    }

    /**
     * 构建上下文注入块
     */
    private buildContextBlock(
        personaResult: PersonaQueryResult,
        taskResult: MemoryRecallResult
    ): string {
        const blocks: string[] = [];

        if (personaResult.found) {
            blocks.push(`【当前人设】\n${this.formatPersona(personaResult.persona)}`);
        }

        if (taskResult.entities.length > 0) {
            const entitySample: EntityInfo[] = taskResult.entities.slice(0, 5);
            const entitiesStr: string = JSON.stringify(entitySample);
            blocks.push(`【工作记忆】\n${taskResult.message}\n${entitiesStr}`);
        }

        return blocks.length > 0 ? blocks.join('\n\n') : '【新对话】';
    }
}
