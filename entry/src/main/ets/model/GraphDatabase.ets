import relationalStore from '@ohos.data.relationalStore';
import { Context } from '@ohos.abilityAccessCtrl';

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

interface NodeData {
    id: number;
    label: string;
    type: string;
    mentions: number;
    depth?: number;
}

interface EdgeData {
    from: number;
    to: number;
    label: string;
    weight: number;
    depth?: number;
    sessionId?: string;
    turnId?: number;
}

interface GraphData {
    nodes: NodeData[];
    edges: EdgeData[];
}

export interface RecallEntity {
    name: string;
    type: string;
    mention_count: number;
    depth?: number;
}

interface RecallRelation {
    source: string;
    target: string;
    type: string;
    confidence: number;
    session_id?: string;
    turn_id?: number;
    depth?: number;
}

interface RecallResult {
    entities: RecallEntity[];
    relations: RecallRelation[];
    message: string;
}

interface BfsEntity {
    id: number;
    name: string;
    type: string;
    mentions: number;
    depth: number;
}

interface RelationQueryResult {
    sourceId: number;
    targetId: number;
    sourceName: string;
    targetName: string;
    type: string;
    confidence: number;
    sessionId?: string;
    turnId?: number;
    depth: number;
}

interface NodeQueryResult {
    id: number;
    name: string;
    type: string;
    mentions: number;
    depth: number;
}

interface CleanupResult {
    cleaned: number;
    deleted_relations?: number;
    deleted_orphans?: number;
    dry_run?: boolean;
    message?: string;
}

interface IntrospectResult {
    entity_count: number;
    relation_count: number;
    message: string;
}

interface ArchiveResult {
    archived: number;
    message: string;
}

interface SearchResultItem {
    name: string;
    type: string;
    mentions: number;
}

interface ChatMessage {
    role: string;
    content: string;
    session_id?: string;
}

const STORE_CONFIG: relationalStore.StoreConfig = {
    name: 'trulymem.db',
    securityLevel: relationalStore.SecurityLevel.S1
};

export class GraphDatabase {
    private store?: relationalStore.RdbStore;
    private context?: Context;

    async init(context: Context): Promise<void> {
        this.context = context;
        this.store = await relationalStore.getRdbStore(context, STORE_CONFIG);
        await this.createTables();
    }

    private async createTables(): Promise<void> {
        if (!this.store) return;
        await this.store.executeSql(`
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT DEFAULT 'concept',
                mentions INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT
            )
        `);
        await this.store.executeSql(`
            CREATE TABLE IF NOT EXISTS relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                relation TEXT NOT NULL,
                object_id INTEGER NOT NULL,
                weight REAL DEFAULT 1.0,
                session_id TEXT,
                turn_id INTEGER,
                created_at TEXT,
                updated_at TEXT,
                status TEXT DEFAULT 'active',
                date_bucket TEXT
            )
        `);
        await this.store.executeSql(`
            CREATE TABLE IF NOT EXISTS chat_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tools TEXT,
                created_at TEXT
            )
        `);
        await this.store.executeSql(`CREATE INDEX IF NOT EXISTS idx_node_name ON nodes(name)`);
        await this.store.executeSql(`CREATE INDEX IF NOT EXISTS idx_node_type ON nodes(type)`);
        await this.store.executeSql(`CREATE INDEX IF NOT EXISTS idx_rel_source ON relations(subject_id)`);
        await this.store.executeSql(`CREATE INDEX IF NOT EXISTS idx_rel_target ON relations(object_id)`);
        await this.store.executeSql(`CREATE INDEX IF NOT EXISTS idx_rel_type ON relations(relation)`);
        await this.store.executeSql(`CREATE INDEX IF NOT EXISTS idx_rel_status ON relations(status)`);
    }

    async commit(triplets: TripletData[], entityTypes?: Record<string, string>, sessionId?: string, turnId?: number): Promise<void> {
        if (!this.store) return;
        for (const triplet of triplets) {
            const subjectId: number = await this.upsertNode(triplet.subject, entityTypes?.[triplet.subject]);
            const objectId: number = await this.upsertNode(triplet.object, entityTypes?.[triplet.object]);
            const existingId: number = await this.checkDuplicateRelation(subjectId, triplet.relation, objectId);
            if (existingId > 0) {
                continue;
            }
            const now = new Date().toISOString();
            const dateBucket = now.split('T')[0];
            const bucket: relationalStore.ValuesBucket = {
                'subject_id': subjectId,
                'relation': triplet.relation,
                'object_id': objectId,
                'session_id': sessionId || null,
                'turn_id': turnId || null,
                'created_at': now,
                'updated_at': now,
                'status': 'active',
                'date_bucket': dateBucket
            };
            await this.store.insert('relations', bucket);
        }
    }

    private async checkDuplicateRelation(subjectId: number, relation: string, objectId: number): Promise<number> {
        if (!this.store) return -1;
        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('relations');
        predicates.equalTo('subject_id', subjectId).and().equalTo('relation', relation).and().equalTo('object_id', objectId).and().equalTo('status', 'active');
        const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['id']);
        if (resultSet.goToFirstRow()) {
            const id: number = resultSet.getLong(resultSet.getColumnIndex('id'));
            resultSet.close();
            return id;
        }
        resultSet.close();
        return -1;
    }

    private async upsertNode(name: string, entityType?: string): Promise<number> {
        if (!this.store) return -1;
        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
        predicates.equalTo('name', name);
        const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['id', 'mentions']);
        const now = new Date().toISOString();
        if (resultSet.goToNextRow()) {
            const id: number = resultSet.getLong(resultSet.getColumnIndex('id'));
            const mentions: number = resultSet.getLong(resultSet.getColumnIndex('mentions'));
            resultSet.close();
            const updatePredicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
            updatePredicates.equalTo('id', id);
            const bucket: relationalStore.ValuesBucket = {
                'mentions': mentions + 1,
                'updated_at': now
            };
            await this.store.update(bucket, updatePredicates);
            return id;
        }
        resultSet.close();
        const bucket: relationalStore.ValuesBucket = {
            'name': name,
            'type': entityType || 'concept',
            'mentions': 1,
            'created_at': now,
            'updated_at': now
        };
        return await this.store.insert('nodes', bucket);
    }

    async recall(queryIntent: string, seedEntities?: string[], depth: number = 2, timeRange?: TimeRangeParams, sessionFilter?: string): Promise<RecallResult> {
        if (!this.store) {
            return { entities: [], relations: [], message: 'Database not initialized' };
        }
        // 计算时间范围过滤
        let minDateBucket: string | undefined;
        if (timeRange && timeRange.days && timeRange.days > 0) {
            const cutoff = new Date();
            cutoff.setDate(cutoff.getDate() - timeRange.days);
            minDateBucket = cutoff.toISOString().slice(0, 10).replace(/-/g, '');
        }
        const keywords = queryIntent.toLowerCase().replace(/,/g, ' ').split(/\s+/).filter(w => w.trim());
        const allEntities: BfsEntity[] = [];
        const entityIds = new Set<number>();
        let seedEntityIds = new Set<number>();

        if (keywords.length === 0 && (!seedEntities || seedEntities.length === 0)) {
            const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
            predicates.orderByDesc('mentions');
            const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['id', 'name', 'type', 'mentions']);
            while (resultSet.goToNextRow() && allEntities.length < 50) {
                const id = resultSet.getLong(resultSet.getColumnIndex('id'));
                const name = resultSet.getString(resultSet.getColumnIndex('name'));
                const type = resultSet.getString(resultSet.getColumnIndex('type'));
                const mentions = resultSet.getLong(resultSet.getColumnIndex('mentions'));
                entityIds.add(id);
                allEntities.push({ id, name, type, mentions, depth: 0 });
            }
            resultSet.close();
        } else {
            if (seedEntities && seedEntities.length > 0) {
                for (const seedName of seedEntities) {
                    const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
                    predicates.equalTo('name', seedName);
                    const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['id', 'name', 'type', 'mentions']);
                    while (resultSet.goToNextRow()) {
                        const id = resultSet.getLong(resultSet.getColumnIndex('id'));
                        if (!entityIds.has(id)) {
                            entityIds.add(id);
                            seedEntityIds.add(id);
                            allEntities.push({
                                id,
                                name: resultSet.getString(resultSet.getColumnIndex('name')),
                                type: resultSet.getString(resultSet.getColumnIndex('type')),
                                mentions: resultSet.getLong(resultSet.getColumnIndex('mentions')),
                                depth: 0
                            });
                        }
                    }
                    resultSet.close();
                }
            }
            for (const keyword of keywords) {
                const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
                predicates.like('name', `%${keyword}%`);
                const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['id', 'name', 'type', 'mentions']);
                while (resultSet.goToNextRow()) {
                    const id = resultSet.getLong(resultSet.getColumnIndex('id'));
                    if (!entityIds.has(id)) {
                        entityIds.add(id);
                        allEntities.push({
                            id,
                            name: resultSet.getString(resultSet.getColumnIndex('name')),
                            type: resultSet.getString(resultSet.getColumnIndex('type')),
                            mentions: resultSet.getLong(resultSet.getColumnIndex('mentions')),
                            depth: 0
                        });
                    }
                }
                resultSet.close();
            }
        }

        const allRelations: RelationQueryResult[] = [];
        let currentLayerIds = new Set<number>(entityIds);
        const visitedEntityIds = new Set<number>(entityIds);
        // 批量预加载所有相关节点名称，减少 N+1 查询
        const nodeNameCache = new Map<number, {name: string, type: string, mentions: number}>();
        // 批量预加载所有相关节点名称，减少 N+1 查询
        const nodeNameCache = new Map<number, {name: string, type: string, mentions: number}>();

        for (let layer = 0; layer < depth && currentLayerIds.size > 0; layer++) {
            const currentIds = Array.from(currentLayerIds);
            const relations = await this.getRelationsForNodes(currentIds, sessionFilter, minDateBucket);
            const nextLayerIds = new Set<number>();

            for (const rel of relations) {
                allRelations.push(rel);
                if (!visitedEntityIds.has(rel.targetId)) {
                    nextLayerIds.add(rel.targetId);
                }
                if (rel.targetId !== rel.sourceId && !visitedEntityIds.has(rel.sourceId)) {
                    nextLayerIds.add(rel.sourceId);
                }
            }

            for (const newId of nextLayerIds) {
                if (!visitedEntityIds.has(newId)) {
                    visitedEntityIds.add(newId);
                    // 优先从缓存获取，避免 N+1 查询
                    const cached = nodeNameCache.get(newId);
                    if (cached) {
                        const addedEntity: BfsEntity = {
                            id: newId,
                            name: cached.name,
                            type: cached.type,
                            mentions: cached.mentions,
                            depth: layer + 1
                        };
                        allEntities.push(addedEntity);
                    } else {
                        const nodeData = await this.getNodeById(newId);
                        if (nodeData) {
                            nodeNameCache.set(newId, {name: nodeData.name, type: nodeData.type, mentions: nodeData.mentions});
                            const addedEntity: BfsEntity = {
                                id: nodeData.id,
                                name: nodeData.name,
                                type: nodeData.type,
                                mentions: nodeData.mentions,
                                depth: layer + 1
                            };
                            allEntities.push(addedEntity);
                        }
                    }
                }
            }
            currentLayerIds = nextLayerIds;
        }

        const entities: RecallEntity[] = allEntities.map(e => {
            const entity: RecallEntity = {
                name: e.name,
                type: e.type,
                mention_count: e.mentions,
                depth: e.depth
            };
            return entity;
        });
        const relations: RecallRelation[] = allRelations.map(r => {
            const rel: RecallRelation = {
                source: r.sourceName,
                target: r.targetName,
                type: r.type,
                confidence: r.confidence,
                session_id: r.sessionId,
                turn_id: r.turnId,
                depth: r.depth
            };
            return rel;
        });

        return {
            entities,
            relations,
            message: `找到 ${entities.length} 个实体, ${relations.length} 条关系`
        };
    }

    private async getNodeById(id: number): Promise<NodeQueryResult | null> {
        if (!this.store) return null;
        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
        predicates.equalTo('id', id);
        const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['id', 'name', 'type', 'mentions']);
        if (resultSet.goToNextRow()) {
            const node: NodeQueryResult = {
                id: resultSet.getLong(resultSet.getColumnIndex('id')),
                name: resultSet.getString(resultSet.getColumnIndex('name')),
                type: resultSet.getString(resultSet.getColumnIndex('type')),
                mentions: resultSet.getLong(resultSet.getColumnIndex('mentions')),
                depth: 0
            };
            resultSet.close();
            return node;
        }
        resultSet.close();
        return null;
    }

    private async getRelationsForNodes(nodeIds: number[], sessionFilter?: string, minDateBucket?: string): Promise<RelationQueryResult[]> {
        if (!this.store || nodeIds.length === 0) return [];
        const relations: RelationQueryResult[] = [];
        // 批量预加载所有节点名称到缓存，避免 N+1 查询
        const nodeNameCache = new Map<number, {name: string, type: string, mentions: number}>();
        for (const id of nodeIds) {
            const node = await this.getNodeById(id);
            if (node) {
                nodeNameCache.set(id, {name: node.name, type: node.type, mentions: node.mentions});
            }
        }
        for (const nodeId of nodeIds) {
            const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('relations');
            predicates.equalTo('status', 'active').and().equalTo('subject_id', nodeId);
            if (sessionFilter) {
                predicates.and().equalTo('session_id', sessionFilter);
            }
            if (minDateBucket) {
                predicates.and().greaterThanOrEqualTo('date_bucket', minDateBucket);
            }
            const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['subject_id', 'object_id', 'relation', 'weight', 'session_id', 'turn_id']);
            while (resultSet.goToNextRow()) {
                const sourceId = resultSet.getLong(resultSet.getColumnIndex('subject_id'));
                const targetId = resultSet.getLong(resultSet.getColumnIndex('object_id'));
                const sourceNode = nodeNameCache.get(sourceId) || await this.getNodeById(sourceId);
                const targetNode = nodeNameCache.get(targetId) || await this.getNodeById(targetId);
                if (sourceNode && targetNode) {
                    relations.push({
                        sourceId,
                        targetId,
                        sourceName: sourceNode.name,
                        targetName: targetNode.name,
                        type: resultSet.getString(resultSet.getColumnIndex('relation')),
                        confidence: resultSet.getDouble(resultSet.getColumnIndex('weight')),
                        sessionId: resultSet.getString(resultSet.getColumnIndex('session_id')),
                        turnId: resultSet.getLong(resultSet.getColumnIndex('turn_id')),
                        depth: 1
                    });
                }
            }
            resultSet.close();

            const predicates2: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('relations');
            predicates2.equalTo('status', 'active').and().equalTo('object_id', nodeId);
            if (sessionFilter) {
                predicates2.and().equalTo('session_id', sessionFilter);
            }
            if (minDateBucket) {
                predicates2.and().greaterThanOrEqualTo('date_bucket', minDateBucket);
            }
            const resultSet2: relationalStore.ResultSet = await this.store.query(predicates2, ['subject_id', 'object_id', 'relation', 'weight', 'session_id', 'turn_id']);
            while (resultSet2.goToNextRow()) {
                const sourceId = resultSet2.getLong(resultSet2.getColumnIndex('subject_id'));
                const targetId = resultSet2.getLong(resultSet2.getColumnIndex('object_id'));
                const sourceNode = nodeNameCache.get(sourceId) || await this.getNodeById(sourceId);
                const targetNode = nodeNameCache.get(targetId) || await this.getNodeById(targetId);
                if (sourceNode && targetNode) {
                    relations.push({
                        sourceId,
                        targetId,
                        sourceName: sourceNode.name,
                        targetName: targetNode.name,
                        type: resultSet2.getString(resultSet2.getColumnIndex('relation')),
                        confidence: resultSet2.getDouble(resultSet2.getColumnIndex('weight')),
                        sessionId: resultSet2.getString(resultSet2.getColumnIndex('session_id')),
                        turnId: resultSet2.getLong(resultSet2.getColumnIndex('turn_id')),
                        depth: 1
                    });
                }
            }
            resultSet2.close();
        }
        return relations;
    }

    async search(keyword: string): Promise<SearchResultItem[]> {
        if (!this.store) return [];
        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
        predicates.like('name', `%${keyword}%`);
        const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['name', 'type', 'mentions']);
        const results: SearchResultItem[] = [];
        while (resultSet.goToNextRow()) {
            results.push({
                name: resultSet.getString(resultSet.getColumnIndex('name')),
                type: resultSet.getString(resultSet.getColumnIndex('type')),
                mentions: resultSet.getLong(resultSet.getColumnIndex('mentions'))
            });
        }
        resultSet.close();
        return results;
    }

    async purge(criteria: CriteriaData, mode: string = 'soft'): Promise<void> {
        if (!this.store) return;
        if (!criteria.subject && !criteria.target && !criteria.relation && !criteria.sessionId) {
            return;
        }
        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('relations');
        let hasCondition = false;

        if (criteria.subject) {
            const subjectId = await this.getNodeIdByName(criteria.subject);
            if (subjectId > 0) {
                predicates.equalTo('subject_id', subjectId);
                hasCondition = true;
            }
        }
        if (criteria.target) {
            const targetId = await this.getNodeIdByName(criteria.target);
            if (targetId > 0) {
                if (hasCondition) {
                    predicates.and();
                }
                predicates.equalTo('object_id', targetId);
                hasCondition = true;
            }
        }
        if (criteria.relation) {
            if (hasCondition) {
                predicates.and();
            }
            predicates.equalTo('relation', criteria.relation);
            hasCondition = true;
        }
        if (criteria.sessionId) {
            if (hasCondition) {
                predicates.and();
            }
            predicates.equalTo('session_id', criteria.sessionId);
            hasCondition = true;
        }

        if (hasCondition) {
            if (mode === 'soft') {
                const bucket: relationalStore.ValuesBucket = {
                    'status': 'deleted',
                    'updated_at': new Date().toISOString()
                };
                await this.store.update(bucket, predicates);
            } else {
                await this.store.delete(predicates);
            }
        }
        await this.removeOrphanNodes();
    }

    private async removeOrphanNodes(): Promise<number> {
        if (!this.store) return 0;
        let deleted = 0;
        // 优化：批量查询所有有关系的节点 ID，避免 O(N²) 逐节点检查
        const activeRelPred: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('relations');
        activeRelPred.equalTo('status', 'active');
        const relResultSet: relationalStore.ResultSet = await this.store.query(activeRelPred, ['subject_id', 'object_id']);
        const relatedIds = new Set<number>();
        while (relResultSet.goToNextRow()) {
            relatedIds.add(relResultSet.getLong(relResultSet.getColumnIndex('subject_id')));
            relatedIds.add(relResultSet.getLong(relResultSet.getColumnIndex('object_id')));
        }
        relResultSet.close();

        // 查询所有节点，筛选出不在关系中的孤儿节点
        const nodePred: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
        const nodeResultSet: relationalStore.ResultSet = await this.store.query(nodePred, ['id']);
        const orphanIds: number[] = [];
        while (nodeResultSet.goToNextRow()) {
            const nodeId = nodeResultSet.getLong(nodeResultSet.getColumnIndex('id'));
            if (!relatedIds.has(nodeId)) {
                orphanIds.push(nodeId);
            }
        }
        nodeResultSet.close();

        // 批量删除孤儿节点
        for (const orphanId of orphanIds) {
            const deletePred: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
            deletePred.equalTo('id', orphanId);
            await this.store.delete(deletePred);
            deleted++;
        }
        return deleted;
    }

    private async getNodeIdByName(name: string): Promise<number> {
        if (!this.store) return -1;
        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
        predicates.equalTo('name', name);
        const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['id']);
        if (resultSet.goToNextRow()) {
            const id = resultSet.getLong(resultSet.getColumnIndex('id'));
            resultSet.close();
            return id;
        }
        resultSet.close();
        return -1;
    }

    async introspect(): Promise<IntrospectResult> {
        if (!this.store) return { entity_count: 0, relation_count: 0, message: 'Database not initialized' };
        const nodePredicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
        const nodeResultSet = await this.store.query(nodePredicates, ['id']);
        let entityCount = 0;
        while (nodeResultSet.goToNextRow()) {
            entityCount++;
        }
        nodeResultSet.close();

        const relPredicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('relations');
        relPredicates.equalTo('status', 'active');
        const relResultSet = await this.store.query(relPredicates, ['id']);
        let relationCount = 0;
        while (relResultSet.goToNextRow()) {
            relationCount++;
        }
        relResultSet.close();

        return {
            entity_count: entityCount,
            relation_count: relationCount,
            message: `数据库包含 ${entityCount} 个实体, ${relationCount} 条关系`
        };
    }

    async archive(days: number): Promise<ArchiveResult> {
        if (!this.store) return { archived: 0, message: 'Database not initialized' };
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - days);
        const cutoffStr = cutoffDate.toISOString();

        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('relations');
        predicates.equalTo('status', 'active').and().lessThan('created_at', cutoffStr);
        const bucket: relationalStore.ValuesBucket = {
            'status': 'archived',
            'updated_at': new Date().toISOString()
        };
        const count = await this.store.update(bucket, predicates);

        return {
            archived: count,
            message: `归档了 ${count} 条关系`
        };
    }

    async cleanup(dryRun: boolean): Promise<CleanupResult> {
        if (!this.store) return { cleaned: 0, message: 'Database not initialized' };
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - 90);
        const cutoffStr = cutoffDate.toISOString();

        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('relations');
        predicates.equalTo('status', 'deleted').and().lessThan('updated_at', cutoffStr);

        let deleted = 0;
        if (dryRun) {
            const resultSet = await this.store.query(predicates, ['id']);
            while (resultSet.goToNextRow()) {
                deleted++;
            }
            resultSet.close();
        } else {
            deleted = await this.store.delete(predicates);
            const orphanCount = await this.removeOrphanNodes();
            return {
                cleaned: deleted + orphanCount,
                deleted_relations: deleted,
                deleted_orphans: orphanCount,
                dry_run: false,
                message: `删除了 ${deleted} 条关系, ${orphanCount} 个孤立实体`
            } as CleanupResult;
        }

        return {
            cleaned: deleted,
            deleted_relations: deleted,
            dry_run: true,
            message: `将删除 ${deleted} 条关系`
        } as CleanupResult;
    }

    async saveChatMessage(role: string, content: string, tools?: string, sessionId?: string): Promise<void> {
        if (!this.store) return;
        const bucket: relationalStore.ValuesBucket = {
            'session_id': sessionId || null,
            'role': role,
            'content': content,
            'tools': tools || null,
            'created_at': new Date().toISOString()
        };
        await this.store.insert('chat_records', bucket);
    }

    async getChatHistory(limit?: number, sessionId?: string): Promise<ChatMessage[]> {
        if (!this.store) return [];
        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('chat_records');
        if (sessionId) {
            predicates.equalTo('session_id', sessionId);
        }
        predicates.orderByDesc('created_at');
        if (limit) {
            predicates.limitAs(limit);
        }
        const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['role', 'content', 'session_id']);
        const messages: ChatMessage[] = [];
        while (resultSet.goToNextRow()) {
            const msg: ChatMessage = {
                role: resultSet.getString(resultSet.getColumnIndex('role')),
                content: resultSet.getString(resultSet.getColumnIndex('content')),
                session_id: resultSet.getString(resultSet.getColumnIndex('session_id'))
            };
            messages.push(msg);
        }
        resultSet.close();
        return messages.reverse();
    }

    async clearChatHistory(): Promise<void> {
        if (!this.store) return;
        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('chat_records');
        await this.store.delete(predicates);
    }

    private async getAllNodes(): Promise<NodeData[]> {
        if (!this.store) return [];
        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
        const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['id', 'name', 'type', 'mentions']);
        const nodes: NodeData[] = [];
        while (resultSet.goToNextRow()) {
            const node: NodeData = {
                id: resultSet.getLong(resultSet.getColumnIndex('id')),
                label: resultSet.getString(resultSet.getColumnIndex('name')),
                type: resultSet.getString(resultSet.getColumnIndex('type')),
                mentions: resultSet.getLong(resultSet.getColumnIndex('mentions'))
            };
            nodes.push(node);
        }
        resultSet.close();
        return nodes;
    }

    private async getAllEdges(): Promise<EdgeData[]> {
        if (!this.store) return [];
        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('relations');
        const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['subject_id', 'relation', 'object_id', 'weight']);
        const edges: EdgeData[] = [];
        while (resultSet.goToNextRow()) {
            const edge: EdgeData = {
                from: resultSet.getLong(resultSet.getColumnIndex('subject_id')),
                to: resultSet.getLong(resultSet.getColumnIndex('object_id')),
                label: resultSet.getString(resultSet.getColumnIndex('relation')),
                weight: resultSet.getDouble(resultSet.getColumnIndex('weight'))
            };
            edges.push(edge);
        }
        resultSet.close();
        return edges;
    }
}