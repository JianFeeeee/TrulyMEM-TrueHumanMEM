import relationalStore from '@ohos.data.relationalStore';
import { Constants } from '../common/Constants';

export interface TripletInput {
    subject: string;
    relation: string;
    object: string;
}

export interface GraphNode {
    id: number;
    name: string;
    type: string;
    mentions: number;
}

export interface GraphEdge {
    id: number;
    source: number;
    target: number;
    label: string;
    weight: number;
}

export interface GraphData {
    nodes: GraphNode[];
    edges: GraphEdge[];
}

export interface CommitResult {
    success: boolean;
    message: string;
    count?: number;
}

export interface RecallResult {
    success: boolean;
    data: GraphData;
    message: string;
}

export interface PurgeCriteria {
    subject?: string;
    target?: string;
    relation?: string;
}

export interface PurgeResult {
    success: boolean;
    message: string;
    affected?: number;
}

export interface ArchiveResult {
    success: boolean;
    message: string;
    archived: number;
}

export interface CleanupResult {
    success: boolean;
    message: string;
    deleted: number;
}

export interface ChatMessage {
    id: number;
    role: string;
    content: string;
    tools?: string;
    created_at: string;
}

export class GraphDatabase {
    private store: relationalStore.RdbStore | null = null;

    async init(context: any): Promise<void> {
        const STORE_CONFIG: relationalStore.StoreConfig = {
            name: Constants.DB_NAME,
            securityLevel: Constants.SECURITY_LEVEL,
        };

        this.store = await relationalStore.getRdbStore(context, STORE_CONFIG);
        await this.store.executeSql(Constants.SQL_CREATE_NODES);
        await this.store.executeSql(Constants.SQL_CREATE_RELATIONS);
        await this.store.executeSql(Constants.SQL_CREATE_CHAT);
        console.info('GraphDatabase initialized successfully');
    }

    private assertStore(): relationalStore.RdbStore {
        if (!this.store) {
            throw new Error('GraphDatabase not initialized. Call init() first.');
        }
        return this.store;
    }

    // ============ Memory Operations ============

    async commit(triplets: TripletInput[]): Promise<CommitResult> {
        const store = this.assertStore();
        let count = 0;

        try {
            await store.beginTransaction();

            for (const t of triplets) {
                // Upsert subject node
                const subjId = await this.upsertNode(store, t.subject);

                // Upsert object node
                const objId = await this.upsertNode(store, t.object);

                // Create relation
                const bucket: relationalStore.ValuesBucket = {
                    'subject_id': subjId,
                    'relation': t.relation,
                    'object_id': objId,
                    'weight': 1.0,
                };
                await store.insert(Constants.TABLE_RELATIONS, bucket);
                count++;
            }

            await store.commit();
            return { success: true, message: `Committed ${count} triplets`, count };
        } catch (e) {
            await store.rollBack();
            return { success: false, message: `Commit failed: ${e}` };
        }
    }

    private async upsertNode(store: relationalStore.RdbStore, name: string): Promise<number> {
        // Check if node exists
        const predicates = new relationalStore.RdbPredicates(Constants.TABLE_NODES);
        predicates.equalTo('name', name);
        const resultSet = await store.query(predicates, ['id', 'mentions']);

        let nodeId: number;
        if (resultSet.rowCount > 0) {
            resultSet.goToFirstRow();
            nodeId = resultSet.getLong(resultSet.getColumnIndex('id'));
            const mentions = resultSet.getLong(resultSet.getColumnIndex('mentions'));
            resultSet.close();

            // Update mentions + updated_at
            const updateBucket: relationalStore.ValuesBucket = {
                'mentions': mentions + 1,
                'updated_at': this.getNow(),
            };
            const updatePredicates = new relationalStore.RdbPredicates(Constants.TABLE_NODES);
            updatePredicates.equalTo('id', nodeId);
            await store.update(updateBucket, updatePredicates);
        } else {
            resultSet.close();
            const insertBucket: relationalStore.ValuesBucket = {
                'name': name,
                'type': 'concept',
                'mentions': 1,
                'created_at': this.getNow(),
                'updated_at': this.getNow(),
            };
            nodeId = await store.insert(Constants.TABLE_NODES, insertBucket);
        }

        return nodeId;
    }

    async recall(queryIntent: string, seedEntities?: string[]): Promise<RecallResult> {
        const store = this.assertStore();

        try {
            if (seedEntities && seedEntities.length > 0) {
                // Filter by seed entities
                const placeholders = seedEntities.map(() => '?').join(',');
                const nodeSql = `SELECT * FROM nodes WHERE name IN (${placeholders}) ORDER BY mentions DESC`;
                const nodeResultSet = await store.querySql(nodeSql, seedEntities);

                const nodeIds: number[] = [];
                const nodes: GraphNode[] = [];
                while (nodeResultSet.goToNextRow()) {
                    const node = this.rowToNode(nodeResultSet);
                    nodes.push(node);
                    nodeIds.push(node.id);
                }
                nodeResultSet.close();

                if (nodeIds.length === 0) {
                    return { success: true, data: { nodes: [], edges: [] }, message: 'No results found' };
                }

                // Get related edges
                const edgeIdPlaceholders = nodeIds.map(() => '?').join(',');
                const edgeParams = nodeIds.map(id => id.toString());
                const edgeSql = `SELECT * FROM relations WHERE subject_id IN (${edgeIdPlaceholders}) OR object_id IN (${edgeIdPlaceholders})`;
                const edgeResultSet = await store.querySql(edgeSql, edgeParams);

                const edges: GraphEdge[] = [];
                while (edgeResultSet.goToNextRow()) {
                    edges.push(this.rowToEdge(edgeResultSet));
                }
                edgeResultSet.close();

                // Collect all connected node IDs
                const allNodeIds = new Set<number>(nodeIds);
                for (const edge of edges) {
                    allNodeIds.add(edge.source);
                    allNodeIds.add(edge.target);
                }

                // Fetch all connected nodes
                if (allNodeIds.size > nodeIds.length) {
                    const allIdPlaceholders = Array.from(allNodeIds).map(() => '?').join(',');
                    const allIdParams = Array.from(allNodeIds).map(id => id.toString());
                    const allNodeSql = `SELECT * FROM nodes WHERE id IN (${allIdPlaceholders})`;
                    const allNodeRs = await store.querySql(allNodeSql, allIdParams);

                    const allNodes: GraphNode[] = [];
                    while (allNodeRs.goToNextRow()) {
                        allNodes.push(this.rowToNode(allNodeRs));
                    }
                    allNodeRs.close();

                    return {
                        success: true,
                        data: { nodes: allNodes, edges },
                        message: `Found ${allNodes.length} nodes, ${edges.length} edges`,
                    };
                }

                return {
                    success: true,
                    data: { nodes, edges },
                    message: `Found ${nodes.length} nodes, ${edges.length} edges`,
                };
            }

            // Return all data
            return await this.introspect();
        } catch (e) {
            return { success: false, data: { nodes: [], edges: [] }, message: `Recall failed: ${e}` };
        }
    }

    async purge(criteria: PurgeCriteria): Promise<PurgeResult> {
        const store = this.assertStore();
        let affected = 0;

        try {
            if (criteria.target) {
                // Delete by target node name
                const nodePredicates = new relationalStore.RdbPredicates(Constants.TABLE_NODES);
                nodePredicates.equalTo('name', criteria.target);
                const rs = await store.query(nodePredicates, ['id']);
                while (rs.goToNextRow()) {
                    const nodeId = rs.getLong(rs.getColumnIndex('id'));
                    // Delete relations involving this node
                    const relPredicates1 = new relationalStore.RdbPredicates(Constants.TABLE_RELATIONS);
                    relPredicates1.equalTo('subject_id', nodeId);
                    await store.delete(relPredicates1);

                    const relPredicates2 = new relationalStore.RdbPredicates(Constants.TABLE_RELATIONS);
                    relPredicates2.equalTo('object_id', nodeId);
                    await store.delete(relPredicates2);

                    // Delete the node itself
                    const delPredicates = new relationalStore.RdbPredicates(Constants.TABLE_NODES);
                    delPredicates.equalTo('id', nodeId);
                    affected += await store.delete(delPredicates);
                }
                rs.close();
            }

            if (criteria.subject) {
                // More sophisticated deletion could be added here
            }

            return {
                success: true,
                message: `Purged ${affected} nodes`,
                affected,
            };
        } catch (e) {
            return { success: false, message: `Purge failed: ${e}` };
        }
    }

    async introspect(): Promise<RecallResult> {
        const store = this.assertStore();

        try {
            // Get all nodes
            const nodeRs = await store.querySql('SELECT * FROM nodes ORDER BY mentions DESC LIMIT 500');
            const nodes: GraphNode[] = [];
            while (nodeRs.goToNextRow()) {
                nodes.push(this.rowToNode(nodeRs));
            }
            nodeRs.close();

            // Get all edges
            const edgeRs = await store.querySql('SELECT * FROM relations ORDER BY weight DESC LIMIT 1000');
            const edges: GraphEdge[] = [];
            while (edgeRs.goToNextRow()) {
                edges.push(this.rowToEdge(edgeRs));
            }
            edgeRs.close();

            return {
                success: true,
                data: { nodes, edges },
                message: `Found ${nodes.length} nodes, ${edges.length} edges`,
            };
        } catch (e) {
            return { success: false, data: { nodes: [], edges: [] }, message: `Introspect failed: ${e}` };
        }
    }

    async archive(days: number): Promise<ArchiveResult> {
        const store = this.assertStore();

        try {
            const sql = `DELETE FROM relations WHERE created_at < datetime('now', '-${days} days')`;
            const changes = await store.executeSql(sql);
            return { success: true, message: `Archived relations older than ${days} days`, archived: changes };
        } catch (e) {
            return { success: false, message: `Archive failed: ${e}`, archived: 0 };
        }
    }

    async cleanup(dryRun: boolean): Promise<CleanupResult> {
        const store = this.assertStore();

        try {
            if (dryRun) {
                const rs = await store.querySql(`
                    SELECT COUNT(*) as cnt FROM nodes n
                    WHERE NOT EXISTS (SELECT 1 FROM relations WHERE subject_id = n.id OR object_id = n.id)
                    AND n.name NOT IN ('_ROOT_', '_UNKNOWN_')
                `);
                rs.goToFirstRow();
                const count = rs.getLong(rs.getColumnIndex('cnt'));
                rs.close();
                return { success: true, message: `Dry run: ${count} orphaned nodes would be deleted`, deleted: count };
            }

            const rs = await store.querySql(`
                SELECT id FROM nodes n
                WHERE NOT EXISTS (SELECT 1 FROM relations WHERE subject_id = n.id OR object_id = n.id)
                AND n.name NOT IN ('_ROOT_', '_UNKNOWN_')
            `);

            const ids: number[] = [];
            while (rs.goToNextRow()) {
                ids.push(rs.getLong(rs.getColumnIndex('id')));
            }
            rs.close();

            if (ids.length === 0) {
                return { success: true, message: 'No orphaned nodes found', deleted: 0 };
            }

            const placeholders = ids.map(() => '?').join(',');
            const idParams = ids.map(id => id.toString());
            await store.executeSql(`DELETE FROM nodes WHERE id IN (${placeholders})`, idParams);

            return { success: true, message: `Cleaned up ${ids.length} orphaned nodes`, deleted: ids.length };
        } catch (e) {
            return { success: false, message: `Cleanup failed: ${e}`, deleted: 0 };
        }
    }

    // ============ Chat Operations ============

    async saveChatMessage(role: string, content: string, tools?: string): Promise<number> {
        const store = this.assertStore();
        const bucket: relationalStore.ValuesBucket = {
            'role': role,
            'content': content,
        };
        if (tools) {
            bucket['tools'] = tools;
        }
        return await store.insert(Constants.TABLE_CHAT, bucket);
    }

    async getChatHistory(limit: number = 50): Promise<ChatMessage[]> {
        const store = this.assertStore();
        const rs = await store.querySql(
            `SELECT * FROM chat_records ORDER BY id DESC LIMIT ${limit}`
        );

        const messages: ChatMessage[] = [];
        while (rs.goToNextRow()) {
            const msg: ChatMessage = {
                id: rs.getLong(rs.getColumnIndex('id')),
                role: rs.getString(rs.getColumnIndex('role')),
                content: rs.getString(rs.getColumnIndex('content')),
                created_at: rs.getString(rs.getColumnIndex('created_at')),
            };

            const toolsIdx = rs.getColumnIndex('tools');
            if (toolsIdx >= 0) {
                msg.tools = rs.getString(toolsIdx);
            }

            messages.unshift(msg); // Reverse to chronological order
        }
        rs.close();

        return messages;
    }

    async clearChatHistory(): Promise<void> {
        const store = this.assertStore();
        await store.executeSql('DELETE FROM chat_records');
    }

    // ============ Helper Methods ============

    private rowToNode(rs: relationalStore.ResultSet): GraphNode {
        return {
            id: rs.getLong(rs.getColumnIndex('id')),
            name: rs.getString(rs.getColumnIndex('name')),
            type: rs.getString(rs.getColumnIndex('type')),
            mentions: rs.getLong(rs.getColumnIndex('mentions')),
        };
    }

    private rowToEdge(rs: relationalStore.ResultSet): GraphEdge {
        return {
            id: rs.getLong(rs.getColumnIndex('id')),
            source: rs.getLong(rs.getColumnIndex('subject_id')),
            target: rs.getLong(rs.getColumnIndex('object_id')),
            label: rs.getString(rs.getColumnIndex('relation')),
            weight: rs.getDouble(rs.getColumnIndex('weight')),
        };
    }

    private getNow(): string {
        const d = new Date();
        const y = d.getFullYear();
        const mo = String(d.getMonth() + 1).padStart(2, '0');
        const da = String(d.getDate()).padStart(2, '0');
        const h = String(d.getHours()).padStart(2, '0');
        const mi = String(d.getMinutes()).padStart(2, '0');
        const s = String(d.getSeconds()).padStart(2, '0');
        return `${y}-${mo}-${da} ${h}:${mi}:${s}`;
    }
}
