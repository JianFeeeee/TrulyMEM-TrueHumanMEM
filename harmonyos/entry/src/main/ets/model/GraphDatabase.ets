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
}

interface EdgeData {
    from: number;
    to: number;
    label: string;
    weight: number;
}

interface GraphData {
    nodes: NodeData[];
    edges: EdgeData[];
}

interface RecallResult {
    data: GraphData;
}

interface ChatMessage {
    role: string;
    content: string;
}

interface CleanupResult {
    cleaned: number;
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
                created_at TEXT
            )
        `);
        await this.store.executeSql(`
            CREATE TABLE IF NOT EXISTS chat_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tools TEXT,
                created_at TEXT
            )
        `);
    }

    async commit(triplets: TripletData[]): Promise<void> {
        if (!this.store) return;
        for (const triplet of triplets) {
            const subjectId: number = await this.upsertNode(triplet.subject);
            const objectId: number = await this.upsertNode(triplet.object);
            const bucket: relationalStore.ValuesBucket = {
                'subject_id': subjectId,
                'relation': triplet.relation,
                'object_id': objectId,
                'created_at': new Date().toISOString()
            };
            await this.store.insert('relations', bucket);
        }
    }

    private async upsertNode(name: string): Promise<number> {
        if (!this.store) return -1;
        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
        predicates.equalTo('name', name);
        const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['id']);
        if (resultSet.goToNextRow()) {
            const id: number = resultSet.getLong(resultSet.getColumnIndex('id'));
            resultSet.close();
            return id;
        }
        resultSet.close();
        const bucket: relationalStore.ValuesBucket = {
            'name': name,
            'type': 'concept',
            'created_at': new Date().toISOString(),
            'updated_at': new Date().toISOString()
        };
        return await this.store.insert('nodes', bucket);
    }

    async recall(queryIntent: string, seedEntities?: string[]): Promise<RecallResult> {
        if (!this.store) {
            const empty: RecallResult = { data: { nodes: [], edges: [] } };
            return empty;
        }
        const nodes: NodeData[] = await this.getAllNodes();
        const edges: EdgeData[] = await this.getAllEdges();
        const result: RecallResult = { data: { nodes, edges } };
        return result;
    }

    async purge(criteria: CriteriaData): Promise<void> {
        if (!this.store) return;
        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('nodes');
        await this.store.delete(predicates);
    }

    async introspect(): Promise<RecallResult> {
        const nodes: NodeData[] = await this.getAllNodes();
        const edges: EdgeData[] = await this.getAllEdges();
        const result: RecallResult = { data: { nodes, edges } };
        return result;
    }

    async archive(days: number): Promise<void> {
        // Archive old data - placeholder
    }

    async cleanup(dryRun: boolean): Promise<CleanupResult> {
        const result: CleanupResult = { cleaned: 0 };
        return result;
    }

    async saveChatMessage(role: string, content: string, tools?: string): Promise<void> {
        if (!this.store) return;
        const bucket: relationalStore.ValuesBucket = {
            'role': role,
            'content': content,
            'tools': tools || null,
            'created_at': new Date().toISOString()
        };
        await this.store.insert('chat_records', bucket);
    }

    async getChatHistory(limit?: number): Promise<ChatMessage[]> {
        if (!this.store) return [];
        const predicates: relationalStore.RdbPredicates = new relationalStore.RdbPredicates('chat_records');
        predicates.orderByDesc('created_at');
        if (limit) {
            predicates.limitAs(limit);
        }
        const resultSet: relationalStore.ResultSet = await this.store.query(predicates, ['role', 'content']);
        const messages: ChatMessage[] = [];
        while (resultSet.goToNextRow()) {
            const msg: ChatMessage = {
                role: resultSet.getString(resultSet.getColumnIndex('role')),
                content: resultSet.getString(resultSet.getColumnIndex('content'))
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
