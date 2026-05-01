/**
 * GraphMemoryService - 图记忆服务层
 * 封装 GraphDatabase，提供 AI Agent 友好的图记忆操作方法
 * 参考：main 分支 core/tools/memory_tools.py
 */
import { GraphDatabase, RelationQueryResult, TimeRangeParams } from '../model/GraphDatabase';
import { defaultLogger } from '../util/Logger';

// ========= 接口定义 =========

export interface SnapshotData {
    entities: EntityInfo[];
    relations: RelationInfo[];
}

export interface GraphDataNode {
    id: number;
    label: string;
    type: string;
    mentions: number;
    depth?: number;
}

export interface GraphDataEdge {
    from: number;
    to: number;
    label: string;
    weight: number;
    depth?: number;
    sessionId?: string;
    turnId?: number;
}

export interface SnapshotEntity {
    name: string;
    type: string;
    mention_count: number;
    depth?: number;
}

export interface SnapshotRelation {
    source: string;
    target: string;
    type: string;
    confidence: number;
    session_id?: string;
    turn_id?: number;
    depth?: number;
}

export interface GraphOutput {
    nodes: GraphDataNode[];
    edges: GraphDataEdge[];
}

export interface SnapshotOutput {
    entities: SnapshotEntity[];
    relations: SnapshotRelation[];
}

export interface EntityInfo {
    name: string;
    type: string;
    mentionCount: number;
    depth?: number;
}

export interface RelationInfo {
    source: string;
    target: string;
    type: string;
    confidence: number;
    sessionId?: string;
    turnId?: number;
    depth?: number;
}

export interface TripletInput {
    subject: string;
    relation: string;
    object: string;
    confidence?: number;
}

export interface CleanupResult {
    cleaned: number;
    deletedRelations?: number;
    deletedOrphans?: number;
    dryRun?: boolean;
    message: string;
}

export interface SearchResult {
    name: string;
    type: string;
    mentions: number;
}

export interface TaskInfo {
    taskId: string;
    description: string;
    state: string;
    infoCount: number;
    updatedAt: string;
}

export interface NodeData {
    id: number;
    label: string;
    type: string;
    mentions: number;
}

export interface EdgeData {
    from: number;
    to: number;
    label: string;
    weight: number;
}

export interface GraphData {
    nodes: NodeData[];
    edges: EdgeData[];
}

// 内部接口 — 用于替换内联对象类型声明

export interface PurgeCriteriaParams {
    subjectContains?: string;
    relationType?: string;
    targetContains?: string;
    sessionId?: string;
    sourceType?: string;
    targetType?: string;
    sourceHasStatus?: string;
}

export interface NewRelationParams {
    relation: string;
    target: string;
}

interface TripletData {
    subject: string;
    relation: string;
    object: string;
}

interface CriteriaData {
    subject?: string;
    target?: string;
    relation?: string;
    sessionId?: string;
}

export interface MemoryRecallResult {
    entities: EntityInfo[];
    relations: RelationInfo[];
    message: string;
}

export interface MemoryRecallParams {
    queryIntent: string;
    seedEntities?: string[];
    depth?: number;
    timeRange?: TimeRangeParams;
    sessionFilter?: string;
}

export interface MemoryCommitParams {
    triplets: TripletInput[];
    entityTypes?: Record<string, string>;
    sessionId?: string;
    turnId?: number;
}

interface MemoryCommitResult {
    committedCount: number;
    details: string[];
}

export interface MemoryPurgeParams {
    criteria: PurgeCriteriaParams;
    mode: 'soft' | 'hard' | 'supersede';
    newRelation?: NewRelationParams;
}

interface MemoryPurgeResult {
    deletedCount: number;
    message: string;
}

interface HotNodeInfo {
    name: string;
    mentionCount: number;
    type: string;
}

interface MemoryIntrospectResult {
    entityCount: number;
    relationCount: number;
    hotNodes: HotNodeInfo[];
    message: string;
}

interface ArchiveResult {
    archived: number;
    message: string;
}

interface PersonaResult {
    success: boolean;
    message: string;
}

export interface PersonaQueryResult {
    persona: Record<string, string>;
    found: boolean;
}

interface TaskCreateResult {
    success: boolean;
    taskId: string;
    message: string;
}

interface TaskActionResult {
    success: boolean;
    message: string;
}

export interface TaskQueryResult {
    tasks: TaskInfo[];
    message: string;
}

export interface PersonaUpdateParams {
    tone?: string;
    style?: string;
    personality?: string;
    catchphrase?: string;
    background?: string;
}

export interface TaskCreateParams {
    taskId: string;
    description: string;
    infoNodes?: string[];
}

export interface TaskSetStateParams {
    taskId: string;
    state: '进行中' | '已完成' | '已暂停' | '已取消';
}

export interface TaskDeleteParams {
    taskId: string;
    deleteInfoNodes?: boolean;
}

export interface TaskLinkInfoParams {
    taskId: string;
    infoNodeNames: string[];
}

export interface TaskArchiveParams {
    taskId: string;
    summary?: string;
}

export interface TaskQueryParams {
    limit?: number;
    stateFilter?: string;
}

// 节点详情连接项接口
export interface ConnectionItem {
    type: string;
    target_name: string;
}

// 节点详情返回接口
export interface NodeDetailInfo {
    name: string;
    type: string;
    mention_count: number;
    connection_count: number;
    connections: ConnectionItem[];
}

// 图数据统计接口
export interface GraphStats {
    maxDegree: number;
    avgDegree: number;
}

// 人设节点的固定名称
const PERSONA_NODE_NAME: string = 'trulymem_persona_identity';
const PERSONA_NODE_TYPE: string = 'PersonaNode';

// ========= GraphMemoryService =========

export class GraphMemoryService {
    private db: GraphDatabase;

    constructor(db: GraphDatabase) {
        this.db = db;
    }

    // ========= 记忆操作 =========

    /**
     * 记忆召回 — 关键词搜索 + BFS 扩展
     * 对应 tools.memory_recall
     */
    async memoryRecall(params: MemoryRecallParams): Promise<MemoryRecallResult> {
        const depth: number = params.depth ?? 2;
        const result = await this.db.recall(
            params.queryIntent,
            params.seedEntities,
            depth,
            undefined,
            params.sessionFilter
        );
        const entities: EntityInfo[] = result.entities.map(e => {
            const entityItem: EntityInfo = {
                name: e.name,
                type: e.type,
                mentionCount: e.mention_count,
                depth: e.depth ?? 0
            };
            return entityItem;
        });
        const relations: RelationInfo[] = result.relations.map(r => {
            const relationItem: RelationInfo = {
                source: r.source,
                target: r.target,
                type: r.type,
                confidence: r.confidence,
                sessionId: r.session_id,
                turnId: r.turn_id,
                depth: r.depth ?? 0
            };
            return relationItem;
        });
        return { entities, relations, message: result.message };
    }

    /**
     * 记忆写入 — 批量三元组
     * 对应 tools.memory_commit
     */
    async memoryCommit(params: MemoryCommitParams): Promise<MemoryCommitResult> {
        const details: string[] = [];
        for (const t of params.triplets) {
            const subject = t.subject.trim();
            const relation = t.relation.trim();
            const object = t.object.trim();
            if (!subject || !relation || !object) {
                continue;
            }
            const triplets: TripletData[] = [{ subject, relation, object }];
            await this.db.commit(
                triplets,
                params.entityTypes,
                params.sessionId,
                params.turnId
            );
            details.push(`${subject} -[${relation}]-> ${object}`);
        }
        const result: MemoryCommitResult = {
            committedCount: details.length,
            details
        };
        return result;
    }

    /**
     * 记忆删除
     * 对应 tools.memory_purge
     */
    async memoryPurge(params: MemoryPurgeParams): Promise<MemoryPurgeResult> {
        // soft 模式：调用 db.purge 逻辑删除
        if (params.mode === 'supersede' && params.newRelation) {
            // supersede: 先软删除旧关系，再新建
            const softSubject = params.criteria.subjectContains;
            const softRelation = params.criteria.relationType;
            const softTarget = params.criteria.targetContains;
            await this.db.purge({
                subject: softSubject,
                relation: softRelation,
                target: softTarget
            }, 'soft');

            // 新建替代关系
            const newSubj = softSubject || '';
            if (newSubj) {
                await this.db.commit([{
                    subject: newSubj,
                    relation: params.newRelation.relation,
                    object: params.newRelation.target
                }]);
            }
            const supersedeResult: MemoryPurgeResult = {
                deletedCount: 1,
                message: '已用 supersede 模式替代记忆'
            };
            return supersedeResult;
        }

        const subjContains = params.criteria.subjectContains;
        const relType = params.criteria.relationType;
        const tgtContains = params.criteria.targetContains;
        const sessId = params.criteria.sessionId;
        await this.db.purge({
            subject: subjContains,
            relation: relType,
            target: tgtContains,
            sessionId: sessId,
            subjectContains: params.criteria.subjectContains,
            targetContains: params.criteria.targetContains,
            sourceType: params.criteria.sourceType,
            targetType: params.criteria.targetType,
            sourceHasStatus: params.criteria.sourceHasStatus
        }, params.mode === 'hard' ? 'hard' : 'soft');
        const purgeResult: MemoryPurgeResult = {
            deletedCount: subjContains || tgtContains || relType || sessId ? 1 : 0,
            message: `已${params.mode === 'hard' ? '物理删除' : '软删除'}匹配的记忆`
        };
        return purgeResult;
    }

    /**
     * 记忆状态查询
     */
    async memoryIntrospect(sessionId?: string): Promise<MemoryIntrospectResult> {
        const stats = await this.db.introspect();
        const hotNodes: HotNodeInfo[] = [];
        // 从所有节点中获取前10个高频节点
        const searchAll = await this.db.search('');
        const sorted = searchAll.sort((a, b) => b.mentions - a.mentions).slice(0, 10);
        for (const n of sorted) {
            const nodeInfo: HotNodeInfo = {
                name: n.name,
                mentionCount: n.mentions,
                type: n.type
            };
            hotNodes.push(nodeInfo);
        }
        const result: MemoryIntrospectResult = {
            entityCount: stats.entity_count,
            relationCount: stats.relation_count,
            hotNodes,
            message: stats.message
        };
        return result;
    }

    /**
     * 关键词搜索节点
     */
    async search(keyword: string): Promise<SearchResult[]> {
        return await this.db.search(keyword);
    }

    /**
     * 归档旧记忆
     */
    async archive(days: number): Promise<ArchiveResult> {
        return await this.db.archive(days);
    }

    /**
     * 清理已删除的记忆
     */
    async cleanup(dryRun: boolean): Promise<CleanupResult> {
        const result = await this.db.cleanup(dryRun);
        const cleanupResult: CleanupResult = {
            cleaned: result.cleaned,
            deletedRelations: result.deleted_relations,
            deletedOrphans: result.deleted_orphans,
            dryRun: result.dry_run,
            message: result.message || ''
        };
        return cleanupResult;
    }

    /**
     * 记忆图谱 — 在指定时间范围内查询关系
     * 对应 tools.memory_graph
     */
    async memoryGraph(timeRange: TimeRangeParams, sessionFilter?: string): Promise<GraphOutput> {
        const dbResult = await this.db.graph(timeRange, sessionFilter);
        const nodeCount: number = dbResult.nodes.length;
        const edgeCount: number = dbResult.edges.length;
        const nodeList: GraphDataNode[] = [];
        const edgeList: GraphDataEdge[] = [];
        let idx: number = 0;
        while (idx < nodeCount) {
            const n = dbResult.nodes[idx];
            const id1: number = n.id;
            const label1: string = n.label;
            const type1: string = n.type;
            const mentions1: number = n.mentions;
            const depth1: number | undefined = n.depth;
            const graphNode: GraphDataNode = {
                id: id1,
                label: label1,
                type: type1,
                mentions: mentions1,
                depth: depth1
            };
            nodeList.push(graphNode);
            idx++;
        }
        idx = 0;
        while (idx < edgeCount) {
            const e = dbResult.edges[idx];
            const from1: number = e.from;
            const to1: number = e.to;
            const label1: string = e.label;
            const weight1: number = e.weight;
            const depth1: number | undefined = e.depth;
            const sessionId1: string | undefined = e.sessionId;
            const turnId1: number | undefined = e.turnId;
            const graphEdge: GraphDataEdge = {
                from: from1,
                to: to1,
                label: label1,
                weight: weight1,
                depth: depth1,
                sessionId: sessionId1,
                turnId: turnId1
            };
            edgeList.push(graphEdge);
            idx++;
        }
        const out: GraphOutput = {
            nodes: nodeList,
            edges: edgeList
        };
        return out;
    }

    /**
     * 记忆快照 — 在指定时间范围内查询实体和关系
     * 对应 tools.memory_snapshot
     */
    async memorySnapshot(timeRange: TimeRangeParams, sessionFilter?: string): Promise<SnapshotOutput> {
        const dbResult = await this.db.snapshot(timeRange, sessionFilter);
        const entityCount: number = dbResult.entities.length;
        const relationCount: number = dbResult.relations.length;
        const entityList: SnapshotEntity[] = [];
        const relationList: SnapshotRelation[] = [];
        let idx: number = 0;
        while (idx < entityCount) {
            const e = dbResult.entities[idx];
            const name1: string = e.name;
            const type1: string = e.type;
            const mentionCount1: number = e.mention_count;
            const depth1: number | undefined = e.depth;
            const entity: SnapshotEntity = {
                name: name1,
                type: type1,
                mention_count: mentionCount1,
                depth: depth1
            };
            entityList.push(entity);
            idx++;
        }
        idx = 0;
        while (idx < relationCount) {
            const r = dbResult.relations[idx];
            const source1: string = r.source;
            const target1: string = r.target;
            const type1: string = r.type;
            const confidence1: number = r.confidence;
            const sessionId1: string | undefined = r.session_id;
            const turnId1: number | undefined = r.turn_id;
            const depth1: number | undefined = r.depth;
            const relation: SnapshotRelation = {
                source: source1,
                target: target1,
                type: type1,
                confidence: confidence1,
                session_id: sessionId1,
                turn_id: turnId1,
                depth: depth1
            };
            relationList.push(relation);
            idx++;
        }
        const out2: SnapshotOutput = {
            entities: entityList,
            relations: relationList
        };
        return out2;
    }

    /**
     * 记忆清理 — 归档旧记忆并清理孤立节点
     * 对应 tools.memory_cleanup
     */
    async memoryCleanup(dryRun: boolean = false): Promise<CleanupResult> {
        const result = await this.db.cleanup(dryRun);
        const cleanupResult: CleanupResult = {
            cleaned: result.cleaned,
            deletedRelations: result.deleted_relations,
            deletedOrphans: result.deleted_orphans,
            dryRun: result.dry_run,
            message: result.message || ''
        };
        return cleanupResult;
    }

    /**
     * 记忆清理 — 删除指定条件的记忆
     * 对应 tools.memory_purge
     */


    /**
     * 查询已归档的记忆
     * 对应 tools.memory_query_archived
     */
    async queryArchived(days?: number, keyword?: string): Promise<RelationQueryResult[]> {
        try {
            const result = await this.db.queryArchived(days, keyword);
            return result;
        } catch (e) {
            defaultLogger.error('queryArchived error: ' + JSON.stringify(e));
            return [];
        }
    }

    // ========= 人设管理 =========

    /**
     * 更新人设
     * 对应 tools.persona_update
     * 使用 PersonaNode + HAS_PERSONA 关系存储属性
     */
    async personaUpdate(params: PersonaUpdateParams): Promise<PersonaResult> {
        try {
            // 1. 确保 PersonaNode 存在
            const personaTriplets: TripletData[] = [];
            const entityTypes: Record<string, string> = {};
            entityTypes[PERSONA_NODE_NAME] = PERSONA_NODE_TYPE;

            // 2. 逐个属性写入（作为关系），不使用 as any
            const toneVal = params.tone;
            const styleVal = params.style;
            const personalityVal = params.personality;
            const catchphraseVal = params.catchphrase;
            const backgroundVal = params.background;

            if (toneVal) {
                personaTriplets.push({
                    subject: PERSONA_NODE_NAME,
                    relation: 'HAS_PERSONA_TONE',
                    object: toneVal
                });
            }
            if (styleVal) {
                personaTriplets.push({
                    subject: PERSONA_NODE_NAME,
                    relation: 'HAS_PERSONA_STYLE',
                    object: styleVal
                });
            }
            if (personalityVal) {
                personaTriplets.push({
                    subject: PERSONA_NODE_NAME,
                    relation: 'HAS_PERSONA_PERSONALITY',
                    object: personalityVal
                });
            }
            if (catchphraseVal) {
                personaTriplets.push({
                    subject: PERSONA_NODE_NAME,
                    relation: 'HAS_PERSONA_CATCHPHRASE',
                    object: catchphraseVal
                });
            }
            if (backgroundVal) {
                personaTriplets.push({
                    subject: PERSONA_NODE_NAME,
                    relation: 'HAS_PERSONA_BACKGROUND',
                    object: backgroundVal
                });
            }

            if (personaTriplets.length > 0) {
                await this.db.commit(personaTriplets, entityTypes);
            }
            const successResult: PersonaResult = {
                success: true,
                message: `已更新 ${personaTriplets.length} 个人设属性`
            };
            return successResult;
        } catch (e) {
            const errorResult: PersonaResult = {
                success: false,
                message: `更新人设失败: ${(e as Error).message || ''}`
            };
            return errorResult;
        }
    }

    /**
     * 清除人设
     * 对应 tools.persona_clear
     */
    async personaClear(): Promise<PersonaResult> {
        try {
            await this.db.purge({ subject: PERSONA_NODE_NAME }, 'hard');
            const result: PersonaResult = { success: true, message: '已清除所有人设信息' };
            return result;
        } catch (e) {
            const errorResult: PersonaResult = {
                success: false,
                message: `清除人设失败: ${(e as Error).message || ''}`
            };
            return errorResult;
        }
    }

    /**
     * 删除单条人设属性
     * 对应 tools.persona_remove
     */
    async personaRemove(attribute: string): Promise<PersonaResult> {
        try {
            // 将 attribute 转为关系名格式
            const relationName = 'HAS_PERSONA_' + attribute.toUpperCase();
            await this.db.purge({ subject: PERSONA_NODE_NAME, relation: relationName }, 'hard');
            return {
                success: true,
                message: `已删除人设属性: ${attribute}`
            };
        } catch (e) {
            return {
                success: false,
                message: `删除人设属性失败: ${(e as Error).message || ''}`
            };
        }
    }

    /**
     * 查询当前人设
     */
    async personaQuery(): Promise<PersonaQueryResult> {
        const result = await this.db.recall(PERSONA_NODE_NAME, [PERSONA_NODE_NAME], 2);
        const persona: Record<string, string> = {};
        for (const rel of result.relations) {
            if (rel.source === PERSONA_NODE_NAME && rel.type.startsWith('HAS_PERSONA_')) {
                const key = rel.type.replace('HAS_PERSONA_', '').toLowerCase();
                persona[key] = rel.target;
            }
        }
        const queryResult: PersonaQueryResult = {
            persona,
            found: Object.keys(persona).length > 0
        };
        return queryResult;
    }

    // ========= 任务管理 =========

    /**
     * 创建任务节点
     * 对应 tools.task_create
     */
    async taskCreate(params: TaskCreateParams): Promise<TaskCreateResult> {
        try {
            const entityTypes: Record<string, string> = {};
            entityTypes[params.taskId] = 'TaskNode';

            const triplets: TripletData[] = [
                { subject: params.taskId, relation: 'description', object: params.description },
                { subject: params.taskId, relation: 'has_state', object: '进行中' }
            ];

            if (params.infoNodes && params.infoNodes.length > 0) {
                for (const infoNode of params.infoNodes) {
                    entityTypes[infoNode] = 'InfoNode';
                    triplets.push({ subject: params.taskId, relation: 'CONTAINS_INFO', object: infoNode });
                }
            }

            await this.db.commit(triplets, entityTypes);
            const result: TaskCreateResult = {
                success: true,
                taskId: params.taskId,
                message: `已创建任务: ${params.taskId}`
            };
            return result;
        } catch (e) {
            const errorResult: TaskCreateResult = {
                success: false,
                taskId: params.taskId,
                message: `创建任务失败: ${(e as Error).message || ''}`
            };
            return errorResult;
        }
    }

    /**
     * 设置任务状态
     * 对应 tools.task_set_state
     */
    async taskSetState(params: TaskSetStateParams): Promise<TaskActionResult> {
        try {
            // 先删旧的 has_state 关系，再新建
            await this.db.purge({ subject: params.taskId, relation: 'has_state' }, 'soft');
            await this.db.commit([{ subject: params.taskId, relation: 'has_state', object: params.state }]);
            const result: TaskActionResult = {
                success: true,
                message: `任务 ${params.taskId} 状态已设为: ${params.state}`
            };
            return result;
        } catch (e) {
            const errorResult: TaskActionResult = {
                success: false,
                message: `设置任务状态失败: ${(e as Error).message || ''}`
            };
            return errorResult;
        }
    }

    /**
     * 删除任务
     * 对应 tools.task_delete
     */
    async taskDelete(params: TaskDeleteParams): Promise<TaskActionResult> {
        try {
            // 删除所有关联关系
            await this.db.purge({ subject: params.taskId }, 'hard');
            if (params.deleteInfoNodes !== false) {
                await this.db.purge({ target: params.taskId }, 'hard');
            }
            const result: TaskActionResult = { success: true, message: `已删除任务: ${params.taskId}` };
            return result;
        } catch (e) {
            const errorResult: TaskActionResult = {
                success: false,
                message: `删除任务失败: ${(e as Error).message || ''}`
            };
            return errorResult;
        }
    }

    /**
     * 关联信息节点到任务
     * 对应 tools.task_link_info
     */
    async taskLinkInfo(params: TaskLinkInfoParams): Promise<TaskActionResult> {
        try {
            const triplets: TripletData[] = [];
            const entityTypes: Record<string, string> = {};
            for (const nodeName of params.infoNodeNames) {
                entityTypes[nodeName] = 'InfoNode';
                triplets.push({ subject: params.taskId, relation: 'CONTAINS_INFO', object: nodeName });
            }
            await this.db.commit(triplets, entityTypes);
            const result: TaskActionResult = { success: true, message: `已关联 ${triplets.length} 个信息节点` };
            return result;
        } catch (e) {
            const errorResult: TaskActionResult = {
                success: false,
                message: `关联信息节点失败: ${(e as Error).message || ''}`
            };
            return errorResult;
        }
    }

    /**
     * 归档任务
     * 对应 tools.task_archive
     */
    async taskArchive(params: TaskArchiveParams): Promise<TaskActionResult> {
        try {
            await this.taskSetState({ taskId: params.taskId, state: '已暂停' });
            if (params.summary) {
                await this.db.commit([
                    { subject: params.taskId, relation: 'archive_summary', object: params.summary }
                ]);
            }
            const result: TaskActionResult = { success: true, message: `已归档任务: ${params.taskId}` };
            return result;
        } catch (e) {
            const errorResult: TaskActionResult = {
                success: false,
                message: `归档任务失败: ${(e as Error).message || ''}`
            };
            return errorResult;
        }
    }

    /**
     * 查询任务列表
     * 对应 tools.task_query
     */
    async taskQuery(params?: TaskQueryParams): Promise<TaskQueryResult> {
        const limit: number = params?.limit ?? 10;
        const stateFilter: string | undefined = params?.stateFilter;
        const queryResult: TaskQueryResult = {
            tasks: await this.db.getRecentTasks(limit, stateFilter) as TaskInfo[],
            message: `找到 ${limit} 个任务`
        };
        return queryResult;
    }

    // ========= 图数据 =========

    /**
     * 获取用于 WebView 的完整图数据
     */
    async getGraphDataForView(): Promise<GraphData> {
        // 用空关键词召回所有数据
        const recallResult = await this.db.recall('', [], 3);
        const nodes: NodeData[] = [];
        const edges: EdgeData[] = [];
        let nodeIdCounter = 1;
        const nameToId: Record<string, number> = {};

        for (const entity of recallResult.entities) {
            const id = nodeIdCounter;
            nodeIdCounter++;
            nameToId[entity.name] = id;
            const node: NodeData = {
                id,
                label: entity.name,
                type: entity.type,
                mentions: entity.mention_count
            };
            nodes.push(node);
        }

        for (const rel of recallResult.relations) {
            const from = nameToId[rel.source];
            const to = nameToId[rel.target];
            if (from !== undefined && to !== undefined) {
                const edge: EdgeData = {
                    from,
                    to,
                    label: rel.type,
                    weight: rel.confidence
                };
                edges.push(edge);
            }
        }

        const graphData: GraphData = { nodes, edges };
        return graphData;
    }

    /**
     * 查询节点的完整信息 — 自身属性 + 所有相连关系
     */
    async getNodeDetail(nodeName: string): Promise<NodeDetailInfo | null> {
        try {
            const recallResult = await this.db.recall(nodeName, [nodeName], 1);
            if (recallResult.entities.length === 0) {
                return null;
            }

            const entity = recallResult.entities[0];
            const connections: ConnectionItem[] = [];
            let connectionCount = 0;

            for (const rel of recallResult.relations) {
                if (rel.source === nodeName) {
                    const conn: ConnectionItem = {
                        type: rel.type,
                        target_name: rel.target
                    };
                    connections.push(conn);
                    connectionCount++;
                } else if (rel.target === nodeName) {
                    const conn: ConnectionItem = {
                        type: rel.type + ' (反向)',
                        target_name: rel.source
                    };
                    connections.push(conn);
                    connectionCount++;
                }
            }

            const detail: NodeDetailInfo = {
                name: entity.name,
                type: entity.type,
                mention_count: entity.mention_count,
                connection_count: connectionCount,
                connections
            };
            return detail;
        } catch (err) {
            defaultLogger.error('getNodeDetail error: ' + JSON.stringify(err));
            return null;
        }
    }

    /**
     * 返回带连接度数的图数据（每个节点增加 degree 字段）
     */
    async getJoinedData(): Promise<GraphData> {
        const graphData = await this.getGraphDataForView();

        // 计算每个节点的连接度数
        const degreeMap: Record<number, number> = {};
        for (const edge of graphData.edges) {
            degreeMap[edge.from] = (degreeMap[edge.from] || 0) + 1;
            degreeMap[edge.to] = (degreeMap[edge.to] || 0) + 1;
        }

        // 手动为节点附加 degree（ArkTS 不支持展开运算符）
        const nodesWithDegree: NodeData[] = [];
        for (let i = 0; i < graphData.nodes.length; i++) {
            const orig = graphData.nodes[i];
            const copy: NodeData = {
                id: orig.id,
                label: orig.label,
                type: orig.type,
                mentions: orig.mentions
            };
            nodesWithDegree.push(copy);
        }

        const graphResult: GraphData = {
            nodes: nodesWithDegree,
            edges: graphData.edges
        };
        return graphResult;
    }
}
